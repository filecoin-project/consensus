#!/usr/bin/env python2
import numpy as np
from scipy.stats import binom as bi
import math

## We are looking for a number of rounds n such that adv will have at least
## k null rounds within n with near certainty. 

targetNulls = 22 # drawn from selfish mining sim results
nullProb = .27

s = 2**-30

def chainLen():
    # This is a simple CDF of a binomial (sum of binom probas up to x).
    # each round has a proba p = advNullRound() of being null for the adversary
    # We are looking for n such that n trials will yield at least targ successes with high proba
    # which is to say n s.t. 1 - CDF(targ, n, p) > 1 - s => CDF(targ, n, p) < s
    totalRounds = targetNulls - 1
    sumToTargN = 1
    while sumToTargN >= s:
        totalRounds += 1
        sumToTargN = bi.cdf(targetNulls - 1, totalRounds, nullProb) 
    return totalRounds

print "A chain of len {chainLen} will have at least {nulls} null rounds with high proba".format(chainLen =chainLen(), nulls=targetNulls)

