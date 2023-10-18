from pyrogram import filters

from static.configuration.config import MAIN_USER_ID, WORKER_IDS

conversations = {}
users_state_data = {}


class UserStates:
    data_entry = "data_entry"


def state_filter(data):
    async def func(flt, _, query):
        return get_state(query.from_user.id) == flt.data

    return filters.create(func, data=data)


def auth_filter(_, __, query):
    return query.from_user.id in [MAIN_USER_ID, *WORKER_IDS.keys()]


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
