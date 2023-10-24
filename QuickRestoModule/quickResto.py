import datetime
import json
from BotModule.BotWrapper.clientWrapper import ClientWrapper
from BotModule.bot import keyboard
from QuickRestoModule.Helpers.helpers import Helpers
from static.configuration.config import MAIN_USER_ID
from SheetsModule.googleSheets import SpreadSheets
from static.strings.strings import CLOSE_SHIFT_ALERT, OPEN_SHIFT_ALERT


class QuickResto:
    def __init__(self, bot: ClientWrapper, spreads_sheets: SpreadSheets):
        self.test_value = True
        self.helpers = Helpers()
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

    def get_shift(self):
        shift_params = {
            "moduleName": "front.zreport",
            "className": "ru.edgex.quickresto.module3s.front.zreport.Shift",
            "objectId": self.shift_id,
        }
        shift = self.helpers.send_get_request(shift_params, self.shift_url)
        if shift.get("status") == "CLOSED":
            self.bot.shifts[self.shift_id] = shift
            self.bot.send_message(
                int(self.worker[0]),
                CLOSE_SHIFT_ALERT,
                reply_markup=keyboard(self.shift_id),
            )
            self.bot.send_message(
                MAIN_USER_ID,
                f"[{self.worker[1]}](tg://user?id={self.worker[0]}) закрыл(а) смену, ожидается внесение данных",
            )
            self.shift_id = ""

    def get_last_shift_monitoring(self):
        shift_array = self.helpers.send_get_request(self.last_shift_params, self.last_shift_url)
        shift = shift_array[1]
        today = datetime.date.today()

        shift_time = shift.get("localOpenedTime", "").split("T")[0]
        if (str(today) == shift_time or str(today - datetime.timedelta(days=1)) == shift_time) \
                and shift.get("status") == "OPENED":
            self.shift_id = shift.get("id")
            self.worker = self.sheets_integration.find_user_by_date(shift_time)
            print(self.worker)
            self.bot.send_message(
                MAIN_USER_ID,
                f"[{self.worker[1]}](tg://user?id={self.worker[0]}) открыл(а) смену",
            )
            self.bot.send_message(
                784338982,
                f"[{self.worker[1]}](tg://user?id={self.worker[0]}) открыл(а) смену",
            )
            self.bot.send_message(
                int(self.worker[0]),
                OPEN_SHIFT_ALERT,
            )

    def shift_manager(self):
        print("work")
        if self.shift_id == "":
            self.get_last_shift_monitoring()
        else:
            self.get_shift()
