import json
import os
API_ID = 0
BOT_TOKEN = ""
SHEETS_ID = ""
SCOPES = []
MAIN_USER_ID = 0
WORKER_IDS = {}

if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as json_conf:
        credentials = json.load(json_conf)
        sheets = credentials.get("sheets")
        users = credentials.get("users")
        bot = credentials.get("bot")

        API_ID = bot.get("api_id")
        API_HASH = bot.get("api_hash")
        BOT_TOKEN = bot.get("token")

        SHEETS_ID = sheets.get("id")
        SCOPES = sheets.get("scopes")

        MAIN_USER_ID = int(users.get("main_user"))
        WORKER_IDS = users.get("worker_ids")

