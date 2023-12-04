import datetime


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
