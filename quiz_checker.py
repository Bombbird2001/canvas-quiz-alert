import datetime
import os
import pytz
import requests
import schedule
import time
import yaml
from dataclasses import dataclass
from datetime import timedelta, datetime as dt
from playsound3 import playsound


with open("config.yaml", "r") as f:
    data = yaml.safe_load(f)
canvas_link = data["canvas_link"]
token = data["canvas_access_token"]
courses = data["courses"]
open_advance_min = data["open_advance_min"]
close_advance_min = data["close_advance_min"]
display_tz = pytz.timezone(data["display_timezone"])
sound_file = data["alert_sound_file"]
url = canvas_link + "/api/v1/courses/{}/quizzes"
headers = {
    'Authorization': f'Bearer {token}'
}


open_notified = set()
end_notified = set()


@dataclass
class Quiz:
    id: int
    title: str
    url: str
    mobile_url: str
    unlock: dt
    due: dt
    lock: dt
    course_name: str
    
    def get_end_time(self):
        return min(self.due, self.lock)
    
    def is_opening_soon(self, time_now):
        return time_now + timedelta(minutes=open_advance_min) >= self.unlock > time_now - timedelta(minutes=1)

    def is_closing_soon(self, time_now):
        end_time = self.get_end_time()
        return self.unlock <= time_now < end_time <= time_now + timedelta(minutes=close_advance_min)


def parse_quiz(quiz, course_name) -> Quiz:
    unlock = quiz["unlock_at"]
    if unlock is None:
        unlock = pytz.utc.localize(dt.min + timedelta(days=1))
    else:
        unlock = dt.fromisoformat(unlock)
    unlock = unlock.astimezone(display_tz)
    due = quiz["due_at"]
    if due is None:
        due = pytz.utc.localize(dt.max - timedelta(days=1))
    else:
        due = dt.fromisoformat(due)
    due = due.astimezone(display_tz)
    lock = quiz["lock_at"]
    if lock is None:
        lock = pytz.utc.localize(dt.max - timedelta(days=1))
    else:
        lock = dt.fromisoformat(lock)
    lock = lock.astimezone(display_tz)
    
    quiz_id = quiz["id"]
    title = quiz["title"]
    quiz_url = quiz["html_url"]
    mobile_url = quiz["mobile_url"]
    return Quiz(quiz_id, title, quiz_url, mobile_url, unlock, due, lock, course_name)


true_start_time = dt.now(datetime.UTC)
simulated_start_time = dt.now(datetime.UTC)


def get_time_now():
    return simulated_start_time + (dt.now(datetime.UTC) - true_start_time)


def check_quizzes():
    all_quizzes = []
    for course in courses:
        course_id = course["id"]
        course_name = course["name"]
        res = requests.get(url.format(course_id), headers=headers).json()
        for quiz_str in res:
            all_quizzes.append(parse_quiz(quiz_str, course_name))
    time_now = get_time_now()
    opening = []
    opening_notif = False
    closing = []
    closing_notif = False
    for quiz in all_quizzes:
        key = (quiz.id, quiz.unlock, quiz.get_end_time())
        if quiz.is_opening_soon(time_now):
            opening.append(quiz)
            if key not in open_notified:
                open_notified.add(key)
                opening_notif = True
        if quiz.is_closing_soon(time_now):
            closing.append(quiz)
            if key not in end_notified:
                end_notified.add(key)
                closing_notif = True
    # opening_notif = True
    # closing_notif = True
    if opening_notif or closing_notif:
        print("----------------------------------------------------------------")
    if opening_notif:
        opening.sort(key=lambda x: x.unlock)
        print("The following quizzes are opening soon:")
        for quiz in opening:
            print(f"{quiz.unlock.strftime("%Y-%m-%d %H:%M:%S")} | {quiz.course_name} - {quiz.title}: {quiz.url}")
    if closing_notif:
        closing.sort(key=lambda x: x.get_end_time())
        print("The following quizzes are closing soon:")
        for quiz in closing:
            print(f"{quiz.get_end_time().strftime("%Y-%m-%d %H:%M:%S")} | {quiz.course_name} - {quiz.title}: {quiz.url}")
    if opening_notif or closing_notif:
        playsound(sound_file)


if __name__ == "__main__":
    if not os.path.exists(sound_file):
        print(sound_file, "not found!")
    else:
        print("Checking quizzes...")
        check_quizzes()
        schedule.every(20).seconds.do(check_quizzes)
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                print("Bye")
                break
