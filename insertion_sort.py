import random
import cProfile


def insertion_sort(a):
    for i in xrange(1, len(a)):
        j = i
        while j > 0 and a[j-1] > a[j]:
            a[j-1], a[j] = a[j], a[j-1]
            j -= 1
    return a

if __name__ == "__main__":
    n = 10000
    a = [random.randint(0, n) for i in xrange(n)]
    print insertion_sort(a)
    cProfile.run('insertion_sort(a)')