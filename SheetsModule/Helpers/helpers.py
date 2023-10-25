import itertools


def array_converter(array):
    return list(itertools.chain(*array))


def searcher(array, finder):
    for i in range(len(array)):
        if array[i] == finder:
            return i
