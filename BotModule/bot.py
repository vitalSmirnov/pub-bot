import datetime

from BotModule.BotWrapper.helpers.pyrothrottle.filters.throttle import Throttle
from googleapiclient.errors import HttpError
from pyrogram import filters
from pyrogram.errors import Forbidden
from pyrogram.types import CallbackQuery
from BotModule.BotWrapper.clientWrapper import ClientWrapper
from BotModule.BotWrapper.helpers.helpers import (
    auth_filter,
    non_auth_filter,
    set_state,
    UserStates,
    update_user_data,
    state_filter,
    get_user_data,
    admin_filter,
    all_user_keyboard, select_worker_keyboard, private_user_keyboard
)
from BotModule.helpers.helpers import log_shift_data_compiler, output_logging_data, shift_hours_total, message_handler, \
    get_date, check_user_input_is_valid
from static.configuration.config import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    VITAL_USER_ID,
    WORKER_IDS_KEY_SWAPPEN,
    MAIN_USER_ID, WORKER_IDS
)
from static.configuration.utils import scheduler, spreadsheet
from static.strings.strings import (
    INPUT_DATA_ALERT,
    WRONG_FORMAT,
    SHIFT_WORKER,
    SHIFT_KNOW,
    BAR_WORKS,
    BAR_NOT_WORKS, CHANGE_WORKER
)

app = ClientWrapper(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
)
throttle = Throttle(1)
auth_filter = filters.create(auth_filter)
non_auth_filter = filters.create(non_auth_filter)
admin_filter = filters.create(admin_filter)


def user_data_comparer(shift, user_data):
    # создание объекта для логгирования
    log_data = log_shift_data_compiler(shift)
    output_logging_data('----Quick resto data', log_data)

    quick_data_cash = int(shift.get("closingEncashment")) - int(shift.get('totalReturnCash', 0))
    quick_data_card = int(shift.get("totalCard")) - int(shift.get('totalReturnCard', 0))

    if abs(int(user_data[0])) - quick_data_cash < 50:
        # если разница в наличных в пределах 50 рублей (монетки) считаем, что всё окей
        return int(user_data[1]) - quick_data_card
    else:
        # если разница в наличных больше 50 рублей (бумажки) злимся и сообщаем
        return int(user_data[0]) - quick_data_cash + (int(user_data[1]) - quick_data_card)


def send_shift_data(worker_id, shift_id, data):
    shift = app.shifts.get(int(shift_id))
    result = user_data_comparer(shift, data)

    # Погрешность на копейки
    if abs(result) <= 1:
        result = 0

    # Часы смены по quickResto
    shift_hours = shift_hours_total(shift.get("localOpenedTime"), shift.get("localClosedTime"))

    # логгирование данных
    spreadsheet.log_shift_data(shift.get("closingEncashment"), shift.get("totalCard"), 25)
    spreadsheet.log_shift_data(data[0], data[1], 26)

    # отправка данных после закрытия смены
    spreadsheet.close_shift(
        worker_id, result, shift.get("localOpenedTime", "").split("T")[0], shift_hours
    )

    # сообщение об итогах
    message = message_handler(result)

    app.send_message(
        MAIN_USER_ID,
        f'У [{WORKER_IDS_KEY_SWAPPEN.get(str(worker_id), "-")}](tg://user?id={worker_id}) на смене {message}',
    )
    app.send_message(
        VITAL_USER_ID,
        f'У [{WORKER_IDS_KEY_SWAPPEN.get(str(worker_id), "-")}](tg://user?id={worker_id}) на смене {message}',
    )

    # очистка состояния
    app.shifts.pop(int(shift_id))
    set_state(int(worker_id), None)
    spreadsheet.set_shift_id(None)

    try:
        spreadsheet.refresh_token()
    except HttpError as error:
        output_logging_data('\nSome error happens', {error})


@app.on_callback_query(auth_filter & filters.regex("input_data_"))
async def input_data(_, callback_query: CallbackQuery):
    output_logging_data('----Worker clicks on close-button', {callback_query.from_user.id})

    await callback_query.answer()

    shift_id = callback_query.data.split("_")[-1]

    await callback_query.edit_message_reply_markup()
    app.info_delete_message = await app.send_message(
        callback_query.from_user.id,
        INPUT_DATA_ALERT,
    )
    try:
        await callback_query.message.delete()
    except Forbidden as error:
        output_logging_data('++++Bot has loses context on input_data', {error, callback_query.from_user.id})

    set_state(callback_query.from_user.id, UserStates.data_entry)
    update_user_data(callback_query.from_user.id, {"shift_id": shift_id})


@app.on_message(filters.command(['start']) & throttle.filter)
async def start_command_all_users(_, message):
    if message.from_user.id in [MAIN_USER_ID, VITAL_USER_ID, *WORKER_IDS.values()]:
        await app.send_message(
            message.from_user.id,
            SHIFT_KNOW,
            reply_markup=private_user_keyboard()
        )
    else:
        await app.send_message(
            message.from_user.id,
            SHIFT_KNOW,
            reply_markup=all_user_keyboard()
        )


@app.on_message(filters.command(['refresh_token']) & admin_filter)
async def refresh_token(_, message):
    msg = spreadsheet.refresh_token()
    await app.send_message(chat_id=message.from_user.id, text=str(msg))


@app.on_callback_query(filters.regex("who-on-shift") & throttle.filter)
async def send_shift_worker(_, callback_query: CallbackQuery):
    output_logging_data('++++User click who-on-shift', {callback_query.from_user.id})

    try:
        await callback_query.message.delete()
    except Forbidden as error:
        output_logging_data('++++Bot has loses context on input_data', {error, callback_query.from_user.id})

    await callback_query.answer()

    date = get_date(spreadsheet)
    worker_data = spreadsheet.find_user_by_date(date)

    await app.send_photo(
        callback_query.from_user.id,
        photo=worker_data[2],
        caption=f'{SHIFT_WORKER} {worker_data[1]}',
        reply_markup=all_user_keyboard()
    )


@app.on_callback_query(filters.regex("is-shift-online") & throttle.filter)
async def send_shift_is_online(_, callback_query: CallbackQuery):
    output_logging_data('++++User click is-bar-works', {callback_query.from_user.id})

    try:
        await callback_query.message.delete()
    except Forbidden as error:
        output_logging_data('++++Bot has loses context on input_data', {error, callback_query.from_user.id})

    await callback_query.answer()

    if spreadsheet.get_shift_id() is None:
        message = BAR_NOT_WORKS
    else:
        message = BAR_WORKS

    await app.send_message(
        callback_query.from_user.id,
        message,
        reply_markup=all_user_keyboard()
    )


@app.on_callback_query(filters.regex("change_shift_worker") & throttle.filter & auth_filter)
async def change_shift_worker(_, callback_query: CallbackQuery):
    output_logging_data('++++Worker change shift member', {callback_query.from_user.id})

    try:
        await callback_query.message.delete()
    except Forbidden as error:
        output_logging_data('++++Bot has loses context on input_data', {error, callback_query.from_user.id})

    await callback_query.answer()

    await app.send_message(
        callback_query.from_user.id,
        CHANGE_WORKER,
        reply_markup=select_worker_keyboard()
    )


@app.on_message(auth_filter & filters.text & state_filter(UserStates.data_entry))
async def data_entry(_, message):
    data = message.text.split("#")
    # output_logging_data('----Worker enter data', {message.from_user.id, data})

    if check_user_input_is_valid(data):
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
        # output_logging_data('----Worker enter wrong data format', {message.from_user.id, data})
        await app.send_message(
            message.from_user.id,
            WRONG_FORMAT,
        )


@app.on_callback_query(auth_filter & filters.regex("change_worker_callback_"))
async def change_worker(_, callback_query: CallbackQuery):
    output_logging_data('----Worker have changed shift-worker', {callback_query.from_user.id})

    await callback_query.answer()

    user_id = callback_query.data.split("_")[-1]
    spreadsheet.change_user_shift(user_id)

    await callback_query.edit_message_reply_markup()
    app.info_delete_message = await app.send_message(
        callback_query.from_user.id,
        INPUT_DATA_ALERT,
    )
    try:
        await callback_query.message.delete()
    except Forbidden as error:
        output_logging_data('++++Bot has loses context on input_data', {error, callback_query.from_user.id})
