'''
Peculiar balance
================

Can we save them? Beta Rabbit is trying to break into a lab that contains the only known zombie cure - but there's an obstacle.
The door will only open if a challenge is solved correctly. The future of the zombified rabbit population is at stake, so Beta
reads the challenge: There is a scale with an object on the left-hand side, whose mass is given in some number of units.
Predictably, the task is to balance the two sides. But there is a catch: You only have this peculiar weight set,
having masses 1, 3, 9, 27, ... units. That is, one for each power of 3. Being a brilliant mathematician,
Beta Rabbit quickly discovers that any number of units of mass can be balanced exactly using this set.

To help Beta get into the room, write a method called answer(x), which outputs a list of strings representing where the
weights should be placed, in order for the two sides to be balanced, assuming that weight on the left has mass x units.

The first element of the output list should correspond to the 1-unit weight, the second element to the 3-unit weight,
and so on. Each string is one of:

"L" : put weight on left-hand side
"R" : put weight on right-hand side
"-" : do not use weight

To ensure that the output is the smallest possible, the last element of the list must not be "-".

x will always be a positive integer, no larger than 1 000 000 000.


Test cases
==========

Inputs:
    (int) x = 2
Output:
    (string list) ["L", "R"]

Inputs:
    (int) x = 8
Output:
    (string list) ["L", "-", "R"]

'''

def answer(x):
    digits = [1, -1, 0]
    powers_of_3 = [1, 3, 9, 27, 81, 243, 729, 2187, 6561, 19683, 59049, 177147, 531441, 1594323, 4782969, 14348907, 43046721, 129140163, 387420489, 1162261467]
    offset = [0]
    for i in xrange(len(powers_of_3)):
        if i == 0:
            offset[0] = 0
        else:
            offset.append(offset[i-1]+pow(3,i-1))
    highest_power = 0
    for i in xrange(len(powers_of_3)):
        if powers_of_3[i] > x:
            highest_power = i
            break
    def convert(guess):
        weight = 0
        for i in xrange(len(guess)):
            weight += powers_of_3[i]*guess[i]
        return weight
    def get_digit(pos, input_x):
        if input_x <= offset[pos]:
            return 0
        else:
            idx = (input_x - offset[pos] - 1) % (powers_of_3[pos]*3)
        if idx < powers_of_3[pos]:
            return 1
        elif idx >= powers_of_3[pos] and idx < powers_of_3[pos]*2:
            return -1
        else:
            return 0
    answer = [get_digit(p, x) for p in xrange(highest_power+1)]
    print 'answer: ', answer
    print 'answer value: ', convert(answer)
    for i in xrange(len(answer)):
        if answer[i] == 1:
            answer[i] = 'R'
        elif answer[i] == -1:
            answer[i] = 'L'
        else:
            answer[i] = '-'
    if answer[-1] == '-':
        return answer[:-1]
    else:
        return answer

if __name__ == '__main__':
    print answer(1000000000)