# These functions are used for rapidly calculating the values of closed form
# expressions explored in the attacks.tex document to drive research.
#
# This is intended to be run with python 2.

import scipy.special
import math
import matplotlib.pyplot as plt


###**Predictable Selfish Mining Attack Probabilities**##

# ElectionWinis the exact probability that an attacker with power a
# wins m out of n successive elections where the final election must be won.
def ElectionWin(n, m, a):
    return a**m * scipy.special.binom(n-1, m-1) * (1.0 - a)**(n-m) 

# Success is a (loose) upper bound on the probability that an attacker with
# power a beats the honest chain in an instance where the attacker knows that
# they will win m out of n successive elections and follows the strategy of
# witholding until the success in the final round.  Bound is loose because
# chernoff bound is not tight and because we give attacker probability 1
# in cases where chernoff bound is not useful.
def Success(n, m, a):
    if n == 0: # handle div-by-zero
        return 0.0
    mu = n * (1.0 - a)
    delta = 1 - (m / (n * (1.0 - a)))
    if delta < 0: # can't apply bound if delta < 0
        return 1.0
    chernoff = math.exp(-1 * mu * delta**2 / 2.0)
    return min(1.0, chernoff) # min might not be necessary with the check on delta

# ForkWin is a (loose) upper bound on the probability that an attacker with
# power a can successfully mine a fork of n rounds.  Bound is not tight because
# we use union bound on all values of m when in reality events with m1 out
# of n successes overlap with events having m2 out of n successes.
def ForkWin(n, a):
    win = 0.0
    for m in range(1, n+1):
        win += ElectionWin(n, m, a) * Success(n, m, a)
    return win

# ForksPerYear is an upper bound on expected forks per year based on ForkWin
# Probability and 30 second block times.  This is an upper bound because it
# applies an aggressive union bound over every block when actually there is
# a lot of dependence.  For example if round x has no forks with 9 out of
# 10 attacker wins then then the chances of round x + 1 having 9 out of 10
# wins is much lower.
def ForksPerYear(n, a):
    blocksPerYear = 2.0*60.0*24.0*365.0
    return ForkWin(n, a) * blocksPerYear


# PDayLongFork determines probability of attacker with power a running a
# fork for a day's worth of blocks.
def PThreeHourFork(a):
    blocksPerYear = 2.0*60.0*24.0*365.0
    return ForkWin(360, a) * 360



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
        
