import datetime
from BotModule.BotWrapper.clientWrapper import ClientWrapper
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from static.configuration.config import BOT_TOKEN, MAIN_USER_ID, WORKER_IDS
from BotModule.BotWrapper.helpers.helpers import (
    auth_filter,
    set_state,
    UserStates,
    update_user_data,
    state_filter,
    get_user_data,
)
from static.configuration.utils import scheduler, spreadsheet
from static.strings.strings import INPUT_DATA_ALERT, WRONG_FORMAT, SHIFT_WORKER, SHIFT_KNOW

app = ClientWrapper(
    "bot",
    api_id=19295348,
    api_hash="120269548c981091dac0c5cffad74808",
    bot_token=BOT_TOKEN,
    in_memory=True,
)
auth_filter = filters.create(auth_filter)


def message_handler(value: int):
    if value == 0:
        return f"итоги совпали ✅"
    elif value > 0:
        return f"сверхприбыль **{value}** 📈"
    else:
        return f"убыток **{value}** 📉"


def send_shift_data(worker_id, shift_id, data):
    user_data = int(data[0]) + int(data[1])
    shift = app.shifts.get(int(shift_id))

    quick_data = int(shift.get("closingEncashment")) + int(shift.get("totalCard"))
    spreadsheet.log_shift_data(shift.get("closingEncashment"), shift.get("totalCard"), 25)
    spreadsheet.log_shift_data(data[0], data[1], 26)
    # отправка данных после закрытия смены
    spreadsheet.close_shift(
        worker_id, user_data - quick_data, shift.get("localOpenedTime", "").split("T")[0]
    )
    # сообщение об итогах
    message = message_handler(user_data - quick_data)

    app.send_message(
        MAIN_USER_ID,
        f"У {WORKER_IDS.get(worker_id, '-')} на смене {message}",
    )
    app.send_message(
        784338982,
        f"У {WORKER_IDS.get(worker_id, '-')} на смене {message}",
    )
    app.shifts.pop(int(shift_id))
    set_state(int(worker_id), None)


# inline клавиатура для бота
def keyboard(shift_id):
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
                )
            ],
        ]
    )
    return kb


@app.on_callback_query(auth_filter & filters.regex("input_data_"))
def input_data(_, callback_query: CallbackQuery):
    callback_query.answer()
    shift_id = callback_query.data.split("_")[-1]
    callback_query.edit_message_reply_markup()  # reply_markup=InlineKeyboardMarkup([]))
    app.send_message(
        callback_query.from_user.id,
        INPUT_DATA_ALERT,
    )
    set_state(callback_query.from_user.id, UserStates.data_entry)
    update_user_data(callback_query.from_user.id, {"shift_id": shift_id})


@app.on_message()
def check_shift(_, message):
    app.send_message(
        message.from_user.id,
        SHIFT_KNOW,
        reply_markup=all_user_keyboard()
    )


@app.on_callback_query(filters.regex("who-on-shift"))
def send_shift_worker(_, callback_query: CallbackQuery):
    callback_query.answer()
    date = str(datetime.date.today())
    message = spreadsheet.find_user_by_date(date)
    app.send_message(
        callback_query.from_user.id,
        f'{SHIFT_WORKER} {message[1]}',
    )


@app.on_message(auth_filter & filters.text & state_filter(UserStates.data_entry))
def data_entry(_, message):
    data = message.text.split("#")
    if len(data) == 2 and data[0].isdigit() and data[1].isdigit():
        shift_id = get_user_data(message.from_user.id).get("shift_id")
        app.send_message(
            message.from_user.id,
            f"Вы внесли данные {data[0]} и {data[1]}\nID: {shift_id}",
        )
        scheduler.add_job(
            send_shift_data,
            "date",
            run_date=datetime.datetime.now(),
            args=(message.from_user.id, shift_id, data),
        )
    else:
        app.send_message(
            message.from_user.id,
            WRONG_FORMAT,
        )
