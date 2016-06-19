#!/bin/python

def fibgen():
    n_2 = None
    n_1 = None
    while True:
        if n_1 == None:
            yield 1
            n_1 = 1
        elif n_2 == None:
            yield 1
            n_2 = 1
        else:
            next = n_1 + n_2
            n_2 = n_1
            n_1 = next
            yield next

