import requests


class Helpers:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Authorization": "Basic dm4zNjI6SlJXOEFUNXg=",
        }

    def send_get_request(self, shift_params, shift_url):
        response = requests.get(
            shift_url, headers=self.headers, params=shift_params
        )
        return response

