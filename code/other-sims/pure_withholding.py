#!/usr/bin/env python3
import utils as u
import numpy as np

# This scripts computes the advantage of running the selfish mining attack 
# number of blocks
sims = 5
numRounds = 1000
e=5.0
att=.33
rat=1-att
miners = 10000
ratMin = rat * miners
attMin = att * miners
p = e/miners

# note we are assuming very worst case, in which adv knows exactly when to release 
# which is completely unrealistic
maxLen = 0
for _ in range(sims):
    ratBlocks = np.random.binomial(ratMin, p, numRounds)
    advBlocks = np.random.binomial(attMin, p, numRounds)
    gap = [ratBlocks[x] - advBlocks[x] for x in range(numRounds)]

    # goal is to search for the length of the longest series of contiguous numbers
    # in the array such that their sum is negative
    for i in range(numRounds):
        for j in range(i, numRounds):
            _sum = sum(gap[i:j])
            if _sum < 0:
                if (j - i) > maxLen:
                    maxLen = j- i

print maxLen
