import json
import math
from scipy.stats import binom
import numpy as np
import pandas as pd
import pdb
import matplotlib.pyplot as plt

# system wide params
miners = 1000
eBlocksPerRound = 1.0
p = eBlocksPerRound/float(miners)

# can be used to estimate with a headstart
headstart = True

if headstart:
    # random heuristic: let's pick best headstart with likelihood > 1/10k to happen for a 49% attacker,
    # or -x st binom.pmf(x, 490, 1./1000) > 10**-4
    start = -5
else:
    start = 0

# meta params
errorBound = 10**-10
stdDevPrecision = .99

def checkDistrib(inProb):
    assert abs(1 - inProb) <= errorBound

def chebLimits(mean, stdDev):
    # find number of std devs we want to get right precision
    k = 0
    i = 0.
    while k == 0:
        i += 1
        if i ** 2 >= 1./(1-stdDevPrecision):
            k = i
    return (int(math.floor(mean - k*stdDev)), int(math.ceil(mean + k*stdDev)))

class MarkovChain:
    def __init__(self, alpha):
        self.alpha = alpha
        self.honestMiners = int(round((1-self.alpha)*miners))
        self.advMiners = int(round(self.alpha*miners))
        self.setupChain()

    def setupChain(self):
        self.mean = (self.honestMiners - self.advMiners)*p
        self.stdDev = miners*p*(1-p)
        self.transProbs = self.getTransProbs()

    def calculateTrans(self, trans):
        _sum = 0.
        if trans < 0:
            trans = abs(trans)
            for i in range(self.advMiners - trans + 1):
                # H[i] A[i+trans]
                _sum += binom.pmf(i, self.honestMiners, p) * binom.pmf(i + trans, self.advMiners, p)
        else:
            for i in range(self.advMiners + 1):
                # H[i+trans] A[i]
                _sum += binom.pmf(i + trans, self.honestMiners, p) * binom.pmf(i, self.advMiners, p)
        return _sum

    def calculateTransProbs(self, probs):
        # in any given round, we can move up to honestMiners up, or advMiners down, for a total
        # of miners unique possible state transitions
        for trans in range(-1*self.advMiners, self.honestMiners + 1):
            prob = self.calculateTrans(trans)
            probs[trans] = prob
        return probs

    def getTransProbs(self):
        transDoc = "./markov/transitions_{alpha}_{miners}.json".format(alpha=alpha, miners=miners)
        transProbs = dict()
        try:
            with open(transDoc) as f:
                tmp = json.load(f)
                # ergh, json int keys
                for key in tmp.keys():
                    transProbs[int(key)] = tmp[key]
        except:
            transProbs = self.calculateTransProbs(transProbs)
            assert sum(transProbs.values()) >= stdDevPrecision
            with open(transDoc, 'w') as f:
                json.dump(transProbs, f, sort_keys=True, indent=4)
        return transProbs

def generateTransMatrix(probs, states):
    # transitionMatrix is represents the proba from state(row) to state(col)
    # for each slot: [ row -> col ]: what distance between col and row: col - row
    # also works with negs
    transMatrix = np.zeros(shape = (len(states), len(states)))
    for row in range(len(states)):
        for col in range(len(states)):
            key = states[col]-states[row]
            if key in probs:
                transMatrix[row][col] = probs[key]
            else:
                transMatrix[row][col] = 0.0
    return transMatrix

def getBoundedStates(markovChain, rounds):
    bounds = chebLimits(markovChain.mean, markovChain.stdDev)
    return range(bounds[0]*rounds, bounds[1]*rounds + 1)

def calcEndStateProbs(states, transMatrix, rounds):
    startVector = np.zeros(len(states))
    startVector[states.index(start)] = 1
    expMatrix = np.linalg.matrix_power(transMatrix, rounds)
    endStates = np.matmul(startVector, expMatrix)
    checkDistrib(sum(endStates))
    return endStates

def atkSuccess(states, endStates):
    # all states for which gap <= 0
    _sum = 0
    for i in range(states.index(0) + 1):
        _sum += endStates[i]
    return _sum

def getEndStates(markovChain, states, rounds):
    transMatrix = generateTransMatrix(markovChain.transProbs, states)
    return calcEndStateProbs(states, transMatrix, rounds)

def plot(endStates, states, alpha, rounds):
    plt.plot(states, endStates)
    plt.xlabel("gap between H and A")
    plt.ylabel("likelihood")
    plt.title("{m} miners, alpha = {al}, over {rd} rounds".format(m = miners, al=alpha, rd = rounds))
    plt.show()

alphas = [k/100.0 for k in range(2, 54, 2)]
roundsBack = range(5, 105, 10)

successRates = []
print "{min} miners\n{eb} blocks per round on expectation\nheadstart: {start}".format(min=miners, eb=eBlocksPerRound, start=start)
for alpha in alphas:
    print "\nFor alpha = {alpha}".format(alpha=alpha)
    AtkrSuccess = []
    mc = MarkovChain(alpha)
    for rounds in roundsBack:
        states = getBoundedStates(mc, rounds)
        endStates = getEndStates(mc, states, rounds)
        # plot(endStates, states, alpha, rounds)
        prob = atkSuccess(states, endStates)
        print "{rounds} rounds back, atkr wins: {win}".format(rounds = rounds, win = prob)
        AtkrSuccess.append(prob)
    successRates.append(AtkrSuccess)

df = pd.DataFrame(successRates, columns=roundsBack, index=alphas)
print df
