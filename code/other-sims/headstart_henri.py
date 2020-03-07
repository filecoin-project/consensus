import numpy as np 
import scipy.special as spe
from scipy.stats import binom

# User Params
k = 10000 # number of epochs
alpha = .3
e = 5.0
negl = 2**-5
numSims = 1000

# Modeling Params
miners = 10000
hon = miners * (1-alpha)
adv = miners * alpha
p = e/miners

def chernoff():
    # using honest miners since > than attacker (ie give largest bound)
    expectedVal = p * hon
    for i in range(int(e), int(e*100)):
        sigma = i / expectedVal -1
        likelihood = np.exp(-(sigma**2 / (2+sigma))*expectedVal)
        if likelihood < negl:
            return i


# let H1, H2 be the first and second epoch LE results for honest parties
# and A1, A2, be those for adversarial.
# We are looking for Pr(|H1| + |H2| <= |H1| + |O1| + |O2|): the condition
# in which the adversary will launch an attack.


# Method 1: sum probabilities for each event, using chernoff to get rid of long tail
def sumProbas():
    tailBound = 2*chernoff()
    print "binding at {ch}".format(ch=tailBound)
    win = 0
    rat = 0
    honBinoms = {}
    advBinoms = {}

    for h in range (0, tailBound + 1):
        honBinoms[h] = binom.pmf(h, hon, p) 
        advBinoms[h] = binom.pmf(h, adv, p)

    # representing the first and second honest runs separately, both adv runs together
    for h0 in range (1, tailBound + 1):
        for h1 in range(0, tailBound + 1):
            honPr = honBinoms[h0] * honBinoms[h1]
            for a0 in range(1, tailBound + 1):
                for a1 in range(0, tailBound + 1):
                    advPr = advBinoms[a0] * advBinoms[a1]
                    advWins = h0 + a0 + a1
                    if advWins >= h0 + hon*p:
                        prod = honPr *advPr
                        rat += prod
                        if advWins >= h0 + h1:
                            win += prod
    return win, rat

# Method 2: actually simulate using binomial series
def binomialRuns():
    successfulAtk = 0
    rationalAtk = 0
    ratLoss = 0
    luckyWin = 0
    luckyLoss = 0
    for i in range(numSims):
        ch = np.random.binomial(hon, p, 2)
        ca = np.random.binomial(adv, p, 2)
        
        honWins = ch[0] + ch[1]
        advWins = ch[0] + ca[0] + ca[1]
        if ch[0] > 0 and ca[0] > 0:
            if advWins >= ch[0] + hon*p:
            # extra condition without which a rational adv would not run the attack
                rationalAtk += 1
                if advWins >= honWins:
                    successfulAtk += 1
                else:
                    ratLoss += 1
            else:
                if advWins >= honWins:
                    luckyWin += 1
                else:
                    luckyLoss += 1


    return successfulAtk/float(numSims), rationalAtk/float(numSims), ratLoss/float(numSims), luckyWin/float(numSims), luckyLoss/float(numSims)

sum_, rat_ = sumProbas()
suc, rat, loss, w, l = binomialRuns()
print "Method 1: likelihood of successful atk is: {runs}. Likelihood of rational atk is: {rat}".format(runs=sum_, rat=rat)
print "Method 2: likelihood of successful atk is: {runs}. Likelihood of rational atk is: {rat}. Loss is {l}. Lucky {w}. Unlucky {ll}".format(runs=suc, rat=rat, l=loss, w=w, ll=l)
