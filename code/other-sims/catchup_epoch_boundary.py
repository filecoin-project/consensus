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
miners = 10000
ratMin = rat * miners
attMin = att * miners
p = e/miners

s = 2**-10

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

