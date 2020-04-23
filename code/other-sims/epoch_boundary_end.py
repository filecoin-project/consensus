#!/usr/bin/env python3
import numpy as np
from scipy.stats import binom as bi

## Take two forks that yield a number of blocks i, j respectively in a given epoch with i >= j
## Epoch boundary will stop on two conditions
##      1 - the adversary produces no blocks in that round. in that case, even if i == j, normal 
##          FCR will apply at next round given a consistent view of network by all participants
##      2 - the adversary produces k blocks, with k < i - j. In this case, that means that the
##          adversary's delayed propagation tactics will not suffice to split the network given
##          the regular entropy in the network.
##
## We are looking to model the likelihood of these events, taking a worst case which means:
## - the two forks have equal power behind them (meaning perfect precision on the part of
##   the adversary when creating the split)
## - the adversary never gets slashed (ie adv wins on both chains with different sybils
##   throughout the duration of the attack)
##
## That is, take Y a variable describing adversarial wins, and X being wins in either fork,
## we are looking for
## pr(Y = 0) + sum_k=1^inf pr(Y = k) * sum_j=0^inf pr(X = j) * pr(X > i) with i = j + k

e = 5.0
alpha = 1.0/3
rat = 1 - alpha
miners = 10000

advMiners = alpha * miners
ratMiners = rat * miners
p = e / miners

def advNullRound():
    return bi.pmf(0, advMiners, p)

def advLessThanForkGap():
    # we cut it off at 30 without sacrificing much precision: whole network has
    # a 2.5E-14 chance of mining 30 blocks with e - 5
    cutoff = 30

    _sum = 0
    for k in range(1, cutoff + 1):
        
        advPr = bi.pmf(k, advMiners, p)
        for j in range(cutoff + 1):
                fork1Pr = bi.pmf(j, ratMiners/2.0, p)
                fork2Pr = 1- bi.cdf(j + k, ratMiners/2.0, p)

                _sum += advPr * fork1Pr * fork2Pr
    
    return _sum

print advNullRound() + advLessThanForkGap()
