import datetime
import json
import requests
from Client_wrapper import ClientWrapper
from bot import keyboard
from config import MAIN_USER_ID
from sheets_ntegration import SpreadSheets


class QuickResto:
    def __init__(self, bot: ClientWrapper, spreads_sheets: SpreadSheets):
        self.test_value = True

        self.sheets_integration = spreads_sheets
        self.bot = bot
        self.shift_id = ""
        self.current_shift_date = ""
        self.worker = ("", "")
        self.layer_name = "vn362"
        self.authorization = "JRW8AT5x"
        self.last_shift_url = (
            f"https://{self.layer_name}.quickresto.ru/platform/online/api/list"
        )
        self.shift_url = (
            f"https://{self.layer_name}.quickresto.ru/platform/online/api/read"
        )
        self.last_shift_params = {
            "moduleName": "front.zreport",
            "className": "ru.edgex.quickresto.module3s.front.zreport.Shift",
            "sortField%5B%5D": "closed",
            "sortOrder%5B%5D": "asc",
        }
        self.headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Authorization": "Basic dm4zNjI6SlJXOEFUNXg=",
        }

    def get_shift(self):
        shift_params = {
            "moduleName": "front.zreport",
            "className": "ru.edgex.quickresto.module3s.front.zreport.Shift",
            "objectId": self.shift_id,
        }
        response = requests.get(
            self.shift_url, headers=self.headers, params=shift_params
        )
        shift = response.json()
        if shift.get("status") == "CLOSED":
            self.bot.shifts[self.shift_id] = shift
            self.bot.send_message(
                int(self.worker[1]),
                f"Смена закрыта, внесите данные",
                reply_markup=keyboard(self.shift_id),
            )
            self.shift_id = ""

    def get_last_shift_monitoring(self):
        response = requests.get(
            self.last_shift_url, headers=self.headers, params=self.last_shift_params
        )
        shift_array = json.loads(response.text)
        shift = shift_array[1]
        today = datetime.date.today()
        shift_time = shift.get("localOpenedTime", "").split("T")[0]
        if (
                str(today) == shift_time
                or str(today - datetime.timedelta(days=1)) == shift_time
        ) and shift.get("status") == "OPENED":
            self.shift_id = shift.get("id")
            self.worker = self.sheets_integration.find_user_by_date(shift_time)
            print(self.worker)
            self.bot.send_message(
                MAIN_USER_ID,
                f"{self.worker[0]} открыл(а) смену",
            )
            self.bot.send_message(
                int(self.worker[1]),
                f"Вы открыли смену",
            )

    def shift_manager(self):
        print("work")
        self.shift_id = '664'
        self.worker = ['Соня', MAIN_USER_ID]
        self.current_shift_date = '2023-10-17'
        self.get_shift()

        # if self.shift_id == "":
        #     self.get_last_shift_monitoring()
        # else:
        #     self.get_shift()
