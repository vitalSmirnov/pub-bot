import datetime

from BotModule.BotWrapper.helpers.helpers import close_shift_keyboard
from static.strings.strings import OPEN_SHIFT_ALERT


def message_handler(value: int):
    if value == 0:
        return f"итоги совпали ✅"
    elif value > 0:
        return f"сверхприбыль **{value}** 📈"
    else:
        return f"убыток **{value}** 📉"


def output_logging_data(prefix: str, data):
    print(f'{prefix} {data} - {datetime.datetime.now()}')


def shift_hours_total(opened_time, closed_time):
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    date1 = datetime.datetime.strptime(opened_time, date_format)
    date2 = datetime.datetime.strptime(closed_time, date_format)

    time_difference = date2 - date1

    return int(time_difference.total_seconds() / 3600)


def get_date(spreadsheet):
    if datetime.time(0, 0, 0) < datetime.datetime.now().time() < datetime.time(16, 0, 0) \
            and spreadsheet.get_shift_id() is not None:
        return str(datetime.date.today() - datetime.timedelta(days=1))
    else:
        return str(datetime.date.today())


def check_user_input_is_valid(data: []):
    if len(data) == 2 and data[0].isdigit() and data[1].isdigit():
        return True
    return False


def log_shift_data_compiler(shift):
    return {
        'closingEncashment': int(shift.get("closingEncashment")),
        'totalReturnCash': int(shift.get('totalReturnCash', 0)),
        'totalCard': int(shift.get("totalCard")),
        'totalReturnCard': int(shift.get('totalReturnCard', 0)),
    }


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


async def send_service_message(bot, receiver_id: int, type: str):
    print(bot.current_worker)
    if type == 'close':
        await bot.send_message(
            receiver_id,
            f"[{bot.current_worker.get('name')}](tg://user?id={bot.current_worker.get('id')}) закрыл(а) смену, ожидается внесение данных"
        )
    else:
        await bot.send_message(
            receiver_id,
            f"[{bot.current_worker.get('name')}](tg://user?id={bot.current_worker.get('id')}) открыл(а) смену"
        )


async def send_worker_alerts(bot, type: str, shift_id: int = 0):
    if type == 'close':
        await bot.send_message(
            bot.current_worker.get('id'),
            f"Вы закрыли смену"
        )
    else:
        await bot.send_message(
            bot.current_worker.get('id'),
            f"Вы открыли смену",
            reply_markup=close_shift_keyboard(shift_id)
        )
