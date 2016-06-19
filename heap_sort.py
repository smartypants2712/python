__author__ = 'Simon'

import random
import cProfile

"""
Max Heap
"""

def heap_sort(a):
    count = len(a)
    end = count - 1
    heapify(a, end)
    while end > 0:
        a[0], a[end] = a[end], a[0]
        end -= 1
        sift_down(a, 0, end)
    return a


def heapify(a, end):
    start = (end - 1)/2
    while start >= 0:
        sift_down(a, start, end)
        start -= 1


def sift_down(a, start, end):
    root = start
    while root * 2 + 1 <= end:
        left = root * 2 + 1
        right = left + 1
        swap = root
        if a[left] > a[root]:
            swap = left
        if right <= end and a[right] > a[swap]:
            swap = right
        if swap == root:
            return
        else:
            a[swap], a[root] = a[root], a[swap]
            root = swap


if __name__ == "__main__":
    n = 100000
    a = [random.randint(0, n) for i in xrange(n)]
    cProfile.run('heap_sort(a)')
    # print heap_sort(a)

