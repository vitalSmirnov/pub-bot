import numpy as np


class Helpers:
    def array_converter(self, array):
        a = np.array(array)
        a = a.flatten()
        return a

    def searcher(self, array, finder):
        for i in range(len(array)):
            if array[i][0] == finder:
                return i
