__author__ = 'Simon'
import random
import cProfile

def merge_sort(array):
    if len(array) == 1:
        return array
    mid = len(array)/2
    left = array[:mid]
    right = array[mid:]
    left = merge_sort(left)
    right = merge_sort(right)
    return merge(left, right)


def merge(left, right):
    merged = []
    if not left:
        merged = right
    elif not right:
        merged = left
    else:
        i = j = 0
        while i < len(left) or j < len(right):
            if i < len(left) and j >= len(right):
                merged = merged + left[i:]
                i = len(left)
            elif i >= len(left) and j < len(right):
                merged = merged + right[j:]
                j = len(right)
            elif left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
    return merged

if __name__ == "__main__":
    n = 100000
    unsorted_array = [random.randint(0, n) for i in xrange(n)]
    cProfile.run( 'merge_sort(unsorted_array)' )
