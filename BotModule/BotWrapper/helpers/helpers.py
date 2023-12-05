from pyrogram import filters

from static.configuration.config import MAIN_USER_ID, WORKER_IDS, VITAL_USER_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

conversations = {}
users_state_data = {}


class UserStates:
    data_entry = "data_entry"


def state_filter(data):
    async def func(flt, _, query):
        return get_state(query.from_user.id) == flt.data

    return filters.create(func, data=data)


def auth_filter(_, __, query):
    return query.from_user.id in [MAIN_USER_ID, VITAL_USER_ID, *WORKER_IDS.values()]


def non_auth_filter(_, __, query):
    return query.from_user.id not in [MAIN_USER_ID, VITAL_USER_ID, *WORKER_IDS.values()]


def admin_filter(_, __, query):
    return query.from_user.id == VITAL_USER_ID


def set_state(user_id, state):
    conversations[user_id] = state


def clear_state(user_id):
    conversations.pop(user_id)


def get_state(user_id):
    return conversations.get(user_id)


def get_user_data(user_id):
    return users_state_data.get(user_id)


def update_user_data(user_id, data):
    if not users_state_data.get(user_id, None):
        users_state_data[user_id] = data
    else:
        users_state_data[user_id].update(data)


def close_shift_keyboard(shift_id):
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Ввести данные", callback_data=f"input_data_{shift_id}"
                )
            ],
        ]
    )
    return kb


def all_user_keyboard():
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Кто на смене?", callback_data='who-on-shift'
                ),
                InlineKeyboardButton(
                    "Работа бара", callback_data='is-shift-online'
                )
            ],
        ]
    )
    return kb


def private_user_keyboard():
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Кто на смене?", callback_data='who-on-shift'
                ),
                InlineKeyboardButton(
                    "Работа бара", callback_data='is-shift-online'
                )
            ],
            [
                InlineKeyboardButton(
                    "Изменить работника на сегодня", callback_data='change_shift_worker'
                )
            ]
        ]
    )
    return kb


def select_worker_keyboard():
    keyboard_buttons = []
    worker_keys = list(WORKER_IDS.keys())
    worker_values = list(WORKER_IDS.values())
    for i in range(len(WORKER_IDS)):
        button = [InlineKeyboardButton(worker_keys[i], callback_data=f'change_worker_callback_{worker_values[i]}')]
        keyboard_buttons.append(button)

    kb = InlineKeyboardMarkup(keyboard_buttons)
    return kb
