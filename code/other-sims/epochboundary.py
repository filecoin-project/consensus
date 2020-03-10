#!/usr/bin/env python3
import math
import numpy as np
import utils as u

## Epoch Boundary attack mitigation:
## This is the analysis of the effectiveness of the randomization mitigiation
## for the epoch boundary boundary attack: an honest player chooses a random
## cutoff at each round after which he doesn't accept new blocks for the current
## round.

# Time divided in T slots
# H_j : random variable denoting the slot honest player j chooses
# Pr[ H_j = t ] = 1 / T
# A_j: random variable denoting the slot attacker guesses for honest player j
# Pr[ A_j = t ] = 1 / T  = Pr[ H_j = t ]
# Then want to know the probability of sucess for targeting a specific player:
# S_j: random variable being 1 if attacker guessed a smaller t than the one
# honest player j picked. See later for a better model.
# Pr[ S_j = 1 ] = SUM(t: 0->T) Pr[ A_j = t | H_j >= t] 
#               = SUM(..) 1 / T * (1 - Pr[ H_j < t])
#               = SUM(..) Pr[ A_j = t] * (1 - SUM(ti:0 -> t) Pr[ H_j = ti ]
#               = SUM(..) 1 / T * (1 - SUM(ti:0 -> t) 1 / T)
#
# A more precise model introduces the notion of a maximum delay d such that the
# attacker that transmits a block to a node do it "just" before the node's
# deadline. Just before means between [t-d; t]
# If the adversary broadcasts before t-d, the honest player have the chance to
# rebroadcast the block to other peers hence defeating the attack.
# P_j: random variable = 1 if attacker guessed a time "close" to the time t of
# player j
# Pr[ P_j = 1 ] = SUM(t: d->T) Pr[ t-d <= A_j <= t | H_j = t ]
#               = SUM(t: d->T) (Pr[Aj <= t] - Pr[ A_j < t-d])* Pr[ H_j = t ]
#
# Then want to know probability of attacker to reach success on half of the
# honest nodes in the network (of size n*h with h = # honest players)
# A: random variable denoting how many nodes did attacker reached before their
# timeout
# Pr[ A = n*h/2 ] = Binomial(n*h/2, n, Pr[ S_j = 1])
# Or using the more precise model
# Pr[ A = n*h/2 ] = Binomial(n*h/2, n, Pr[ P_j = 1])
# Probability that attacker reaches approximately a range
# Pr[ low < A < high ] = BinomialCDF(low -> high) = SUM(t: low -> high) Pr[ A = t ]

## Approximation taken: 
## * n is size of the network but we want to target in terms of power. We assume
## there are enough small miners to have a reliable mapping
##      - this actually gives more prob. of success for attacker, since it
## doesn't differentiate between miners while it should.
## * There are less honest nodes than n: 
##    -in this case the prob. of success of ## the attacker is a lower bound so
## it's OK (attacker has to reach lesss target ## if we remove this approx. so
## chances of success are higher).
##    - we can consider n the number of honest players
## * Pr[ S_j = 1 ] is too relaxed: in practice if he sends it one sec before the
## random deadline, the block is gonna get passed around via gossip. However
## analysis shows it already  has a low chance of probability.

def pr_hj(nslot):
    return 1 / nslot

def pr_hj_cdf(upto,nslot):
    return sum([pr_hj(nslot) for t in range(upto)])

## Pr[ A_j = t ]
def pr_aj(nslot):
    return pr_hj(nslot)

def pr_aj_cdf(upto,nslot,start=0):
    return sum([pr_aj(nslot) for t in range(start,upto)])

## Pr[ S_j = 1]
def pr_sj(info):
    nslot = info['nslot']
    res = 0
    for t in range(nslot):
        res += pr_aj(nslot) * (1 - pr_hj_cdf(t,nslot))
    return res

def pr_pj(info):
    nslot = info['nslot']
    delay = info['delay']
    res = 0
    for t in range(delay,nslot):
        ## even though it's a constant because of uniform dist. let's keep 
        ## according to formulas
        left = pr_aj_cdf(t,nslot,t-delay)
        right = pr_hj(nslot)
        res += left*right
        # print("{} - {} -> {}".format(left,right,res))
    return res

def pr_a(info,target):
    mean_prob = np.mean([info['prob'](info) for t in range(10)])
    return u.binomial(target,info['honests'],mean_prob)

def pr_a_sums(info):
    lown = int(info['low'] * info['target'])
    highn = int(info['high'] * info['target'])
    targets = range(lown,highn)
    return sum([pr_a(info,target) for target in targets])

## pr to run this continuously
def continuous(info):
    return np.prod([pr_a_sums(info) for i in range(info['rounds'])])

def print_info(info):
    print("Computation using {}".format(info['prob'].__name__))
    print("Total number of nodes: {}".format(info['nodes']))
    print("Honest nodes: {} - Attacker nodes: {}".format(info['honests'],info['attacker']))
    print("Target: t={} - range target [{}t,{}t] - for {} rounds".format(info['target'],info['low'],info['high'],info['rounds']))
    print("Number of time slots: {} - Maximum delay: {}".format(info['nslot'],info['delay'])) 

def default(prob=pr_sj):
    info={}
    ## let's imagine 100ms discrete time slots:
    ## 1s contains 10 of those
    ## if we spread randomized cutoff for a period of 4s we get 40 timeslots
    ## [ T - 2s; T + 2s]
    info['nslot'] = 40
    info['delay'] = 5
    # number of nodes in total
    n = 50
    info['nodes']=n
    info['honests']=1/3 * n
    info['attacker']=(1-1/3) * n
    # there are two viable strategies:
    # 1. send to only the minimum number of nodes such that it reaches 50% so
    # attacker will mine next round on its own block
    # 2. send to half of the honest nodes and attack can mine on any half
    # 2 gives higher chances of prob.
    # target=int(n/2 - n/3)
    info['target']=int(info['honests']/2)
    # Attacker tries to attack a certain percentage of nodes, not necessarily
    # exactly 50%. We give here the factor for the lower bounds and a factor for
    # the highest bounds. It translates to the attacker trying to attack a
    # portion of honest nodes between [low * target; high * target]
    # Here I set low = 1 because with low < 1, low * target < 50% so attacker
    # risks losing its block.
    info['low']=1
    info['high']=1.9
    info['rounds']=10
    info['prob'] = prob
    return info

def run_computations(info):
    print("-----------------------------------------")
    print("\n+++ INFO +++")
    print_info(info)
    print("\n+++ RESULTS +++")
    target = info['target']
    prob = info['prob']
    print("Probability of successfully targeting one node: {}".format(prob(info)))
    print("Probability of reaching exactly the # of targets: {}".format(pr_a(info,target)))
    sums=pr_a_sums(info)
    print("Probability of targeting the range of nodes: {}".format(sums))
    rounds=continuous(info)
    print("Probability of running attack for 10 rounds (for target [..]): {}".format(rounds))
    print("-----------------------------------------")

info=default()
run_computations(info)
info2=default(prob=pr_pj)
run_computations(info2)
