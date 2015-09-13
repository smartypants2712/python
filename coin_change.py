__author__ = 'Simon'

def dpMakeChange(coinValueList, change, minCoins, coins_used):
    for cents in range(change+1):
        coinCount = cents
        newCoin = 1
        for j in [c for c in coinValueList if c <= cents]:
            if minCoins[cents-j] + 1 < coinCount:
                coinCount = minCoins[cents-j]+1
                newCoin = j
        minCoins[cents] = coinCount
        coins_used[cents] = newCoin
    return minCoins[change]

def printCoins(coinsUsed,change):
    coin = change
    while coin > 0:
        thisCoin = coinsUsed[coin]
        print(thisCoin)
        coin = coin - thisCoin

if __name__ == "__main__":
   coins = [1, 5, 10, 25, 100]
   change = 77
   minCoins = [0] * (change+1)
   coins_used = [0] * (change+1)
   dpMakeChange(coins, change, minCoins, coins_used)
   printCoins(coins_used, change)
   print minCoins
   print coins_used
