__author__ = 'Simon'

set = [1,5,8,10,13]

def memoize(f):
    memo = {}
    def wrapped(*args):
        if args in memo:
            results = memo[args]
        else:
            results = memo[args] = f(*args)
        return results
    return wrapped

@memoize
def is_subset_exist(i, sum):
    if i < 0:
        return False
    if sum < 0:
        return False
    if set[i] == sum:
        return True
    return is_subset_exist(i-1, sum-set[i]) or is_subset_exist(i-1, sum)

if __name__ == "__main__":
    print is_subset_exist(len(set)-1, 27)