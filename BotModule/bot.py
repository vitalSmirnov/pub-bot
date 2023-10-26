import datetime
from BotModule.BotWrapper.clientWrapper import ClientWrapper
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from static.configuration.config import BOT_TOKEN, MAIN_USER_ID, API_ID, API_HASH, VITAL_USER_ID, \
    WORKER_IDS_KEY_SWAPPEN
from BotModule.BotWrapper.helpers.helpers import (
    auth_filter,
    set_state,
    UserStates,
    update_user_data,
    state_filter,
    get_user_data,
)
from static.configuration.utils import scheduler, spreadsheet
from static.strings.strings import INPUT_DATA_ALERT, WRONG_FORMAT, SHIFT_WORKER, SHIFT_KNOW, BAR_WORKS, BAR_NOT_WORKS, \
    CLOSE_SHIFT_ALERT

app = ClientWrapper(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
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

    print(
        f'----Quick resto data {[shift.get("closingEncashment"), shift.get("totalCard")]} - {datetime.datetime.now()}')

    spreadsheet.log_shift_data(shift.get("closingEncashment"), shift.get("totalCard"), 25)
    spreadsheet.log_shift_data(data[0], data[1], 26)
    # отправка данных после закрытия смены
    spreadsheet.close_shift(
        worker_id, user_data - quick_data, shift.get("localOpenedTime", "").split("T")[0]
    )
    # сообщение об итогах
    message = message_handler(user_data - quick_data)

    # app.send_message(
    #     MAIN_USER_ID,
    #     f"У {WORKER_IDS_KEY_SWAPPEN.get(str(worker_id), '-')} на смене {message}",
    # )
    app.send_message(
        VITAL_USER_ID,
        f'У [{WORKER_IDS_KEY_SWAPPEN.get(str(worker_id), "-")}](tg://user?id={worker_id}) на смене {message}',
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
                ),
                InlineKeyboardButton(
                    "Работа бара", callback_data='is-shift-online'
                )
            ],
        ]
    )
    return kb


@app.on_callback_query(auth_filter & filters.regex("input_data_"))
async def input_data(_, callback_query: CallbackQuery):
    print(f'----Worker with id {callback_query.from_user.id} clicks on close-button - {datetime.datetime.now()}')
    await callback_query.answer()

    shift_id = callback_query.data.split("_")[-1]

    await callback_query.edit_message_reply_markup()  # reply_markup=InlineKeyboardMarkup([]))
    app.info_delete_message = await app.send_message(
        callback_query.from_user.id,
        INPUT_DATA_ALERT,
    )

    await callback_query.message.delete()
    set_state(callback_query.from_user.id, UserStates.data_entry)
    update_user_data(callback_query.from_user.id, {"shift_id": shift_id})


@app.on_message(filters.command(['start']))
def check_shift(_, message):
    app.send_message(
        message.from_user.id,
        SHIFT_KNOW,
        reply_markup=all_user_keyboard()
    )


@app.on_callback_query(filters.regex("who-on-shift"))
async def send_shift_worker(_, callback_query: CallbackQuery):
    print(f'++++Worker with id {callback_query.from_user.id} click who-on-shift - {datetime.datetime.now()}')

    await callback_query.message.delete()
    await callback_query.answer()

    date = str(datetime.date.today())
    message = spreadsheet.find_user_by_date(date)
    await app.send_photo(
        callback_query.from_user.id,
        photo=message[2],
        caption=f'{SHIFT_WORKER} {message[1]}'
    )

    await app.send_message(
        callback_query.from_user.id,
        SHIFT_KNOW,
        reply_markup=all_user_keyboard()
    )


@app.on_callback_query(filters.regex("is-shift-online"))
async def send_shift_is_online(_, callback_query: CallbackQuery):
    print(f'++++Worker with id {callback_query.from_user.id} click is-bar-works - {datetime.datetime.now()}')
    await callback_query.message.delete()
    await callback_query.answer()

    if spreadsheet.get_shift_id() is None:
        message = BAR_NOT_WORKS
    else:
        message = BAR_WORKS

    await app.send_message(
        callback_query.from_user.id,
        message,
    )
    await app.send_message(
        callback_query.from_user.id,
        SHIFT_KNOW,
        reply_markup=all_user_keyboard()
    )


@app.on_message(auth_filter & filters.text & state_filter(UserStates.data_entry))
async def data_entry(_, message):
    data = message.text.split("#")
    print(f'----Worker with id {message.from_user.id} enter data {data}- {datetime.datetime.now()}')
    if len(data) == 2 and data[0].isdigit() and data[1].isdigit():
        shift_id = get_user_data(message.from_user.id).get("shift_id")

        await app.send_message(
            message.from_user.id,
            f"Вы внесли данные {data[0]} и {data[1]}\nID: {shift_id}",
        )

        scheduler.add_job(
            send_shift_data,
            "date",
            run_date=datetime.datetime.now(),
            args=(message.from_user.id, shift_id, data),
        )
        await app.delete_messages(chat_id=app.info_delete_message.chat.id, message_ids=app.info_delete_message.id)
        await app.delete_messages(chat_id=message.from_user.id, message_ids=message.id)
        app.info_delete_message = {}
    else:
        print(f'----Worker with id {message.from_user.id} enter wrong data format- {datetime.datetime.now()}')
        await app.send_message(
            message.from_user.id,
            WRONG_FORMAT,
        )

