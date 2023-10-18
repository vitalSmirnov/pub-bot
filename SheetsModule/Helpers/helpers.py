import numpy as np


def array_converter(array):
    a = np.array(array)
    a = a.flatten()
    return a


def searcher(array, finder):
    print(array, finder, "array")
    for i in range(len(array)):
        print(array[i], finder)
        if array[i] == finder:
            return i

