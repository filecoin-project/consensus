#!/usr/bin/env python3
import utils as u
import numpy as np

# This scripts computes the advantage of running the lookfwd attack according to
# the paper formula (lookfwd.pdf)
# number of blocks
sims = 10000
numRounds = 5000
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

    attacking = False
    atkLen = 0

    # track longest possible run in the 5k rounds
    # adv stops as soon as neg gap returns to 0
    gap = 0
    for rnd in range(numRounds):
        rndDiff = ratBlocks[rnd] - advBlocks[rnd]
        
        if attacking:
            newGap = gap + rndDiff
            # adv wins on ties (so >, not >=)
            if newGap > 0:
                # stop attack (note this is a loss, but we assume perfect knowledge)
                gap = 0
                attacking = False
                if atkLen - 1 > maxLen:
                    maxLen = atkLen - 1
                atkLen = 0
            else:
                # continue attack
                gap = newGap
                atkLen += 1
        else:
            # not attacking and miner miners more, can start attack
            if rndDiff < 0:
                # do HS, ie adv can coopt ratBlocks and mine over full tipset next round
                # which makes gap be full advBlocks, not just diff
                gap = ratBlocks[rnd]
                attacking = True
                atkLen = 1


print maxLen



