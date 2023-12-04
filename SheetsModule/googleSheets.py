import os
from google.auth.transport.requests import Request
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from static.configuration.config import SCOPES, SHEETS_ID, WORKER_IDS_KEY_SWAPPEN
from SheetsModule.Helpers.helpers import searcher, array_converter, change_worker_alert


class SpreadSheets:
    credentials = None
    service = None
    sheets = None

    def __init__(self):
        if os.path.exists("token.json"):
            self.credentials = credentials.Credentials.from_authorized_user_file(
                "token.json", SCOPES
            )
        if not self.credentials or not self.credentials.valid:
            if (
                    self.credentials
                    and self.credentials.expired
                    and self.credentials.refresh_token
            ):
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.credentials = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.credentials.to_json())

        self.service = build("sheets", "v4", credentials=self.credentials)
        self.sheets = self.service.spreadsheets()
        self.shift_id = None
        self.current_shift_date = None

    def refresh_token(self):
        if self.credentials.valid:
            if (
                    self.credentials
                    and self.credentials.expired
                    and self.credentials.refresh_token
            ):
                self.credentials.refresh(Request())

        return 'Token refreshed'

    def set_shift_id(self, shift_id):
        self.shift_id = shift_id

    def get_shift_id(self):
        return self.shift_id

    def find_users_index_by_id(self, user_id):
        try:
            index = 3
            workers_sheet = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet1!A3:A8")
                .execute()
            ).get('values')

            workers_sheet = array_converter(workers_sheet)
            return searcher(workers_sheet, str(user_id)) + index

        except HttpError as error:
            print(error)

    def find_user_by_date(self, date_time):
        try:
            worker_index = 0
            result = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet2!E2:AI2")
                .execute()
            )
            date_index = searcher(result.get("values")[0], date_time)
            result = (
                self.sheets.values()
                .get(
                    spreadsheetId=SHEETS_ID,
                    range=f"Sheet2!{chr(date_index + 69)}3:{chr(date_index + 69)}8",
                )
                .execute()
            )
            for i in range(len(result.get('values'))):
                if result.get('values')[i] == ['1']:
                    worker_index = i + 3

            worker_tg_id = (
                self.sheets.values()
                .get(
                    spreadsheetId=SHEETS_ID,
                    range=f"Sheet2!A{worker_index}:C{worker_index}",
                )
                .execute()
            )

            return worker_tg_id.get("values", [])[0]

        except HttpError as error:
            print(error)

    def close_shift(self, user_id, resulting_value, current_shift_date, current_shift_hours):
        try:
            result = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet2!E2:AI2")
                .execute()
            )
            date_index = searcher(result.get("values")[0], current_shift_date) + 69
            worker_index = self.find_users_index_by_id(user_id)

            result = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet1!D{worker_index}")
                .execute()
            )
            print(result.get('values', 0))
            hours = int(result.get('values', 0)[0][0]) + current_shift_hours

            self.sheets.values().update(
                spreadsheetId=SHEETS_ID,
                range=f"Sheet1!{chr(date_index)}{worker_index}",
                valueInputOption="USER_ENTERED",
                body={"values": [[resulting_value]]},
            ).execute()

            self.sheets.values().update(
                spreadsheetId=SHEETS_ID,
                range=f"Sheet1!D{worker_index}",
                valueInputOption="USER_ENTERED",
                body={"values": [[hours]]},
            ).execute()

        except HttpError as error:
            return error

    def change_user_shift(self, user_id):

        user_index = self.find_users_index_by_id(user_id)

        try:
            result = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet2!E2:AI2")
                .execute()
            )
            date_index = searcher(result.get("values")[0], self.current_shift_date) + 69

            self.sheets.values().clear(spreadsheetId=SHEETS_ID, range=f"Sheet2!{chr(date_index)}3:{chr(date_index)}7").execute()

            self.sheets.values().update(
                spreadsheetId=SHEETS_ID,
                range=f"Sheet2!{chr(date_index)}{user_index}",
                valueInputOption="USER_ENTERED",
                body={"values": [['1']]},
            ).execute()

            return change_worker_alert(user_id)

        except HttpError as error:
            print(error)

    def log_shift_data(self, closing_encashment, total_card, index):
        try:
            self.sheets.values().update(
                spreadsheetId=SHEETS_ID,
                range=f"Sheet2!B{index}:C{index}",
                valueInputOption="USER_ENTERED",
                body={"values": [[closing_encashment, total_card]]},
            ).execute()
        except HttpError as error:
            return error
