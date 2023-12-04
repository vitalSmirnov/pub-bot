import datetime
from BotModule.BotWrapper.clientWrapper import ClientWrapper
from BotModule.BotWrapper.helpers.helpers import keyboard
from QuickRestoModule.Helpers.helpers import Helpers
from static.configuration.config import MAIN_USER_ID, VITAL_USER_ID
from SheetsModule.googleSheets import SpreadSheets
from static.strings.strings import CLOSE_SHIFT_ALERT, OPEN_SHIFT_ALERT


class QuickResto:
    def __init__(self, bot: ClientWrapper, spreads_sheets: SpreadSheets):
        self.test_value = True
        self.helpers = Helpers()
        self.sheets_integration = spreads_sheets
        self.bot = bot
        self.shift_id = ""
        self.worker = []
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
            "filters": [{"field": "status", "operation": "eq", "value": "OPENED"}]
        }

    def get_shift(self):
        shift_params = {
            "moduleName": "front.zreport",
            "className": "ru.edgex.quickresto.module3s.front.zreport.Shift",
            "objectId": self.shift_id,
        }
        shift = self.helpers.send_get_request(shift_params, self.shift_url)
        if shift.get("status") == "CLOSED":
            print(f'Worker {self.worker[1]} with id {self.worker[0]} CLOSE shift - {datetime.datetime.now()}')

            self.bot.shifts[self.shift_id] = shift

            # self.helpers.send_service_message(self.bot, self.worker, MAIN_USER_ID, 'close')
            self.helpers.send_service_message(self.bot, self.worker, VITAL_USER_ID, 'close')

            self.bot.send_message(
                int(self.worker[0]),
                CLOSE_SHIFT_ALERT,
                reply_markup=keyboard(self.shift_id),
            )

            self.shift_id = ""
            self.sheets_integration.set_shift_id(None)

    def get_last_shift_monitoring(self):
        shift_array = self.helpers.send_get_request(self.last_shift_params, self.last_shift_url)
        shift = shift_array[1]
        today = datetime.date.today()
        shift_time = shift.get("localOpenedTime", "").split("T")[0]
        if str(today) == shift_time and shift.get("status") == "OPENED":
            self.worker = self.sheets_integration.find_user_by_date(shift_time)

            print(f'Worker {self.worker[1]} with id {self.worker[0]} OPEN shift - {datetime.datetime.now()}')

            self.shift_id = shift.get("id")
            self.sheets_integration.set_shift_id(self.shift_id)

            self.helpers.send_service_message(self.bot, self.worker, MAIN_USER_ID, 'open')
            self.helpers.send_service_message(self.bot, self.worker, VITAL_USER_ID, 'open')

            self.bot.send_message(
                int(self.worker[0]),
                OPEN_SHIFT_ALERT,
            )

    def shift_manager(self):
        print(f'\nShift manager works - {datetime.datetime.now()}')

        # --------------------------------- debug settings ---------------------------------
        self.shift_id = 773
        self.worker = [955279593, "Соня", "picture"]
        self.current_shift_date = '2023-11-28'
        self.sheets_integration.set_shift_id(773)
        self.get_shift()
        # self.get_last_shift_monitoring()
        # -----------------------------------------------------------------------------------

        # if self.shift_id == "":
        #     self.get_last_shift_monitoring()
        # else:
        #     self.get_shift()
