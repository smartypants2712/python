#!/bin/python

import random
import cProfile

def quicksort(list, low, high):
    if low < high:
        pivot = partition(list, low, high)
        quicksort(list, low, pivot-1)
        quicksort(list, pivot+1, high)

def partition(list, low, high):
    pivot = list[low]
    i = low
    j = high
    while True:
        while list[i] < pivot:
            i += 1
        while list[j] > pivot:
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]

if __name__ == "__main__":
    n = 10
    a = [random.randint(0, n) for i in xrange(n)]
    print a
    cProfile.run( 'quicksort(a, 0, len(a)-1)' )