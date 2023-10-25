import json
import os

INPUT_DATA_ALERT = ""
WRONG_FORMAT = ""
CLOSE_SHIFT_ALERT = ""
OPEN_SHIFT_ALERT = ""
SHIFT_WORKER = ""
SHIFT_KNOW = ""
BAR_WORKS = ""
BAR_NOT_WORKS = ""

if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as json_conf:
        credentials = json.load(json_conf)
        strings = credentials.get("strings")

        INPUT_DATA_ALERT = strings.get("input_data_alert")
        WRONG_FORMAT = strings.get("wrong_format")

        CLOSE_SHIFT_ALERT = strings.get("close_shift_alert")
        OPEN_SHIFT_ALERT = strings.get("open_shift_alert")

        SHIFT_WORKER = strings.get("current_worker")
        SHIFT_KNOW = strings.get("shift_info_message")

        BAR_WORKS = strings.get("shift_is_working")
        BAR_NOT_WORKS = strings.get("shift_isnt_work")
