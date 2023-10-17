from apscheduler.schedulers.background import BackgroundScheduler

from SheetsModule.googleSheets import SpreadSheets

scheduler = BackgroundScheduler()
spreadsheet = SpreadSheets()
