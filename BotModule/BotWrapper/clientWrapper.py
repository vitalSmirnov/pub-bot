from pyrogram import Client


class ClientWrapper(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shifts = {}