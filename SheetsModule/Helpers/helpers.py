import numpy as np


def array_converter(array):
    a = np.array(array)
    a = a.flatten()
    return a


def searcher(array, finder):
    for i in range(len(array)):
        if array[i] == finder:
            return i
