from pyrogram import Client


class ClientWrapper(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shifts = {}
        self.info_delete_message = {}
        self.current_worker = {}
        self.current_shift_status = ''
