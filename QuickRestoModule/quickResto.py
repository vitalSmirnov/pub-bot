import asyncio
import datetime
from QuickRestoModule.Helpers.helpers import Helpers


class QuickResto:
    def __init__(self):
        self.test_value = True
        self.helpers = Helpers()
        self.shift_id = None
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
        self.shift_params = {
            "moduleName": "front.zreport",
            "className": "ru.edgex.quickresto.module3s.front.zreport.Shift",
            "objectId": self.shift_id,
        }

    async def get_shift(self):
        shift_object = await self.helpers.send_get_request(self.shift_params, self.shift_url)

        if shift_object.get("status") == "CLOSED":
            self.shift_id = None
            return {"shift": shift_object, "status": 'CLOSED'}
        else:
            return {"shift": shift_object, "status": 'CONTINUE'}

    async def get_last_shift(self):
        try:
            shift_array = await self.helpers.send_get_request(self.last_shift_params, self.last_shift_url)
            shift_object = shift_array[1]
        except:
            return {"shift": None, "status": 'UNDEFINED'}

        shift_time = shift_object.get("localOpenedTime", "").split("T")[0]

        if self.is_shift_opened(shift_object, shift_time, str(datetime.date.today())):
            self.shift_id = shift_object.get("id")
            return {"shift": shift_object, "status": 'OPENED'}
        else:
            return {"shift": shift_object, "status": 'NOT_OPENED'}

    def is_shift_opened(self, shift, shift_time, today):
        return str(today) == shift_time and shift.get("status") == "OPENED" and self.shift_id is None

    async def shift_manager(self):
        print(f'\nShift manager works - {datetime.datetime.now()}')

        if self.shift_id is not None:
            return await self.get_shift()
        else:
            return await self.get_last_shift()
