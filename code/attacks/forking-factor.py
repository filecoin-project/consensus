# These functions are used for rapidly calculating the values of closed form
# expressions explored in the attacks.tex document to drive research.
#
# This is intended to be run with python 2.

import scipy.special
import math
import matplotlib.pyplot as plt

"""
Initial Condition has 1 block (genesis), "rational" miner mines block on heaviest winning chain.
In Round n, what are the expected number of network forks with weight > 3/4 n, with n the number of rounds considered (with genesis the first).
With weight as win: add 1, lose: add nothing. And Weight a proxy for expected return.
"""

THRESHOLD = 0.75
ROUNDS = 10000
LOOKBACK = 1
MINERS = 3
POWER = 1/MINERS

def simulate(forkingFactor=THRESHOLD, rounds=ROUNDS, lookback=1):
    

def simulate_round(forks):
    

## Matplotlib plotting
def plotForks():
    for a in [0.01, 0.05, 0.1]:
        data = []
        for n in range(1, 500):
            data.append(ForkWin(n,a))
        plt.plot(range(1,500), data)
    plt.xlabel("Fork Length (rounds)")
    plt.ylabel("Success Probability")
    plt.ylim(top=0.01)
    plt.xlim(right=100)
    plt.legend([r'$\alpha=0.01$', r'$\alpha=0.05$', r'$\alpha=0.1$'], loc='upper right')
    plt.title("Upper bound on fork probabilities")
    plt.savefig("small-probs.png")
    plt.show()

if __name__ == '__main__':
    plotForks()
