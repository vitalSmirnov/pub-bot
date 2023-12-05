import requests


class Helpers:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Authorization": "Basic dm4zNjI6SlJXOEFUNXg=",
        }

    async def send_get_request(self, shift_params, shift_url):
        response = requests.get(
            shift_url, headers=self.headers, params=shift_params
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def send_service_message(self, bot, worker: {}, receiver_id: int, type: str):
        if type == 'close':
            bot.send_message(
                receiver_id,
                f"[{worker[1]}](tg://user?id={worker[0]}) закрыл(а) смену, ожидается внесение данных"
            )
        else:
            bot.send_message(
                receiver_id,
                f"[{worker[1]}](tg://user?id={worker[0]}) открыл(а) смену",
            )
