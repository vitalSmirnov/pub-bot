import os
from google.auth.transport.requests import Request
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from static.configuration.config import SCOPES, SHEETS_ID


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

    def searcher_row(self, array, finder):
        for i in range(len(array)):
            if array[i][0] == finder:
                return i

    def searcher_col(self, array, finder):
        for i in range(len(array)):
            if array[0][i] == finder:
                return i

    def find_users_index_by_id(self, user_id):
        try:
            index = 3
            workers_sheet = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet1!A3:A20")
                .execute()
            ).get('values')
            print(workers_sheet)

            return self.searcher_row(workers_sheet[0], user_id) + index

        except HttpError as error:
            print(error)

    def read_spreadsheet(self, first_parameter, second_parameter):
        try:
            result = (
                self.sheets.values()
                .get(
                    spreadsheetId=SHEETS_ID,
                    range=f"Sheet1!{first_parameter}:{second_parameter}",
                )
                .execute()
            )
            print(result)
        except HttpError as error:
            print(error)

    def find_user_by_date(self, date_time):
        try:
            worker_index = 0
            result = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet2!D2:O2")
                .execute()
            )
            date_index = self.searcher_col(result.get("values"), date_time)

            result = (
                self.sheets.values()
                .get(
                    spreadsheetId=SHEETS_ID,
                    range=f"Sheet2!{chr(date_index + 68)}3:{chr(date_index + 68)}8",
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
                    range=f"Sheet2!A{worker_index}:B{worker_index}",
                )
                .execute()
            )

            return worker_tg_id.get("values", [])[0]

        except HttpError as error:
            print(error)

    def color_changer(self, color, row, col):
        try:

            data = {
                "requests": [
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": 0,
                                "startRowIndex": row - 1,
                                "endRowIndex": row,
                                "startColumnIndex": col - 1,
                                "endColumnIndex": col,
                            },
                            "cell": {"userEnteredFormat": {"backgroundColor": color}},
                            "fields": "userEnteredFormat.backgroundColor",
                        }
                    }
                ]
            }
            self.sheets.batchUpdate(spreadsheetId=SHEETS_ID, body=data).execute()
        except HttpError as e:
            print(e)

    def close_shift(self, user_id, resulting_value, current_shift_date):
        try:
            result = (
                self.sheets.values()
                .get(spreadsheetId=SHEETS_ID, range=f"Sheet2!D2:R2")
                .execute()
            )
            date_index = self.searcher_row(result.get("values"), current_shift_date) + 69
            worker_index = self.find_users_index_by_id(user_id)

            self.sheets.values().update(
                spreadsheetId=SHEETS_ID,
                range=f"Sheet1!{chr(date_index)}{worker_index}",
                valueInputOption="USER_ENTERED",
                body={"values": [[resulting_value]]},
            ).execute()

            if resulting_value == 0:
                self.color_changer(
                    {"red": 0, "green": 0.7, "blue": 0.1, "alpha": 0.05},
                    worker_index,
                    date_index - 64,
                )

            elif resulting_value < 0:
                self.color_changer(
                    {"red": 1, "green": 0, "blue": 0, "alpha": 1},
                    worker_index,
                    date_index - 64,
                )

            elif resulting_value > 0:
                self.color_changer(
                    {"red": 0, "green": 0.2, "blue": 0.6, "alpha": 0.05},
                    worker_index,
                    date_index - 64,
                )

        except HttpError as error:
            return error
