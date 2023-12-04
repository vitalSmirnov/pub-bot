import itertools

from static.configuration.config import WORKER_IDS_KEY_SWAPPEN
from static.strings.strings import WORKER_CHANGED_ALERT


def array_converter(array):
    return list(itertools.chain(*array))


def searcher(array, finder):
    for i in range(len(array)):
        if array[i] == finder:
            return i


def change_worker_alert(user_id):
    return f"[{WORKER_IDS_KEY_SWAPPEN}](tg://user?id={user_id}) {WORKER_CHANGED_ALERT}"
