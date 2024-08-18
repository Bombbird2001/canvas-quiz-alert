import yaml
import requests


if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        data = yaml.safe_load(f)
    canvas_link = data["canvas_link"]
    token = data["canvas_access_token"]
    url = f"{canvas_link}/api/v1/courses?per_page=100&enrollment_state=active"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    course_list = requests.get(url, headers=headers).json()
    courses_to_include = []
    for course in course_list:
        print("Include", course["id"], "|", course["course_code"] + "?")
        choice = None
        while choice is None:
            choice = input().lower()
            if choice == 'y' or choice == 'yes':
                choice = True
            elif choice == 'n' or choice == 'no':
                choice = False
            else:
                print("Please input Y or N")
                choice = None
        if choice:
            courses_to_include.append({"id": course["id"], "name": course["course_code"]})
    data["courses"] = courses_to_include
    with open("config.yaml", "w") as of:
        of.write(yaml.dump(data))
