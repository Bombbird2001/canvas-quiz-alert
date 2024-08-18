# Canvas Quiz Alert (WIP)
Professor forcing lecture attendance by opening a short impromptu graded quiz during lecture?
This script will alert you when a quiz is opened on Canvas.

Simply run the script in the background during the lecture time slot(s) you want to monitor,
and turn up your volume.
Enjoy the blaring Boeing 787 autopilot disconnect warning (changeable) when a quiz is about to open or close!

## Requirements
- Python 3
- Canvas API access token (instructions [here](https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273))
- Working speakers

## Installation
1. Clone the repository
2. Install the required packages
    ```bash
    pip install -r requirements.txt
    ```
3. Copy and update config.sample.yaml
    ```bash
    cp config.sample.yaml config.yaml
    ```
Edit canvas_access_token and canvas_link in config.yaml.

You can also change close_advance_min and open_advance_min to adjust the time before the quiz opens/closes to alert you. Change display_timezone to the timezone you wish to display quiz times in.

To change the alert sound, replace the default sound file (alert.mp3) with your own sound file. If the file name or format has changed, update the alert_sound_file field in config.yaml.
**Keep the alert sound duration below 20s, else update rate will be reduced.**
4. Run the setup script to retrieve and select which courses to check
    ```bash
    python get_course_id.py
    ```

## Usage
1. Run the script
    ```bash
    python quiz_checker.py
    ```
2. Turn up your volume

To exit the script, press Ctrl+C.