#!/usr/bin/env python3
import utils as u
import numpy as np

# This scripts computes the advantage of running the lookfwd attack according to
# the paper formula (lookfwd.pdf)
# number of blocks
sims = 10000
e=5.0
att=.33
rat=1-att
miners = 1000
ratMin = rat * miners
attMin = att * miners
p = e/miners

s = 2**-30

# multiDraw is not a good approximation since it redraws the full chain
# at every epoch of the attempted catchup. This is tantamount to the 
# adversary redrawing every past epoch at every epoch, which is not the 
# right model and increases their chances (since more entropy)
def multiDraw():
    caughtUp = 0
    maxDistToCU = 0
    for _ in range(sims):
        ## we can use the number from block withholding sim here as max
        for distCatchup in range(1, 250):
            ratBlocks = sum(np.random.binomial(ratMin, p, distCatchup))
            advBlocks = sum(np.random.binomial(attMin, p, distCatchup))
            
            if advBlocks >= ratBlocks:
                caughtUp += 1
                maxDistToCU = max(distCatchup, maxDistToCU)
                break
    
    print caughtUp
    pCatchUp = float(caughtUp)/sims
    print "pr(catchup) = " + str(pCatchUp)
    
    r = 1
    while pCatchUp**r > s:
        r += 1
    
    print "secure after " + str(r) + " cycles of at most " + str(maxDistToCU) + " epochs"


def singleDraw():
    caughtUp = 0
    maxDistToCU = 0
    CUDists = []

    for _ in range(sims):
        # count rat blocks found in null adversarial period
        ratAdvance = 0
        # ratAdvance = np.random.binomial(ratMin/2, p, 1)[0]

        maxCatchup = 250
        ratBlocks = np.random.binomial(ratMin, p, maxCatchup)
        advBlocks = np.random.binomial(attMin, p, maxCatchup)
        for distCatchup in range(1, maxCatchup):
            if sum(advBlocks[:distCatchup]) >= sum(ratBlocks[:distCatchup]) + ratAdvance:
                caughtUp += 1
                maxDistToCU = max(distCatchup, maxDistToCU)
                CUDists.append(distCatchup)
                break
    
    print caughtUp
    pCatchUp = float(caughtUp)/sims
    print "pr(catchup) = " + str(pCatchUp)
    
    r = 1
    while pCatchUp**r > s:
        r += 1
    
    print "secure after " + str(r) + " cycles of at most " + str(maxDistToCU) + " epochs"

    CUDists.sort(reverse=True)
    avg = np.average(CUDists[:r])

    print "looking at worst " + str(r) + " dists, we can take " + str(avg)

singleDraw()


