#!/usr/bin/env python3
import math
import numpy as np
import utils as u

# Time divided in T slots
# H_j : random variable denoting the slot honest player j chooses
# Pr[ H_j = t ] = 1 / T
# A_j: random variable denoting the slot attacker guesses for honest player j
# Pr[ A_j = t ] = 1 / T  = Pr[ H_j = t ]
# Then want to know the probability of sucess for targeting a specific player:
# S_j: random variable being 1 if attacker guessed a smaller t than the one
# honest player j picked
# Pr[ S_j = 1 ] = SUM(t: 0->T) Pr[ A_j = t | H_j >= t] 
#               = SUM(..) 1 / T * (1 - Pr[ H_j < t])
#               = SUM(..) Pr[ A_j = t] * (1 - SUM(ti:0 -> t) Pr[ H_j = ti ]
#               = SUM(..) 1 / T * (1 - SUM(ti:0 -> t) 1 / T)
#
# Then want to know probability of success to have success on half of the nodes
# in the network (of size n)
# A: random variable denoting how many nodes did attacker reached before their
# timeout
# Pr[ A = n/2 ] = Binomial(n/2, n, Pr[ S_j = 1])
# Probability that attacker reaches approximately a range
# Pr[ low < A < high ] SUM(t: low -> high) Pr[ A = t ]

## Approximation taken: 
## * n is size of the network but we want to target in terms of power. We assume
## there are enough small miners to have a reliable mapping
## * There are less honest nodes than n: 
##    -in this case the prob. of success of ## the attacker is a lower bound so
## it's OK (attacker has to reach lesss target ## if we remove this approx. so
## chances of success are higher).
##    - we can consider n the number of honest players

## let's imagine 100ms discrete time slots:
## 1s contains 20 of those
## if we spread randomized cutoff for a period of 4s we get 40 timeslots
## [ T - 2s; T + 2s]
nb_time_slots = 100
print("number of time slots: {}".format(nb_time_slots))

def pr_hj():
    return 1 / nb_time_slots

## Pr[ A_j = t ]
def pr_aj():
    return pr_hj()

## Pr[ S_j = 1]
def pr_sj():
    res = 0
    for t in range(nb_time_slots):
        res += pr_aj() * (1 - sum([pr_hj() for ti in range(t)]))
    return res

def pr_a(target,total):
    # print("pr_a: {} {} {}".format(target,total,pr_sj()))
    return u.binomial(target,total,pr_sj())

def pr_a_sums(targets,total):
    return sum([pr_a(t,total) for t in targets])

## pr to run this continuously
def continuous(rounds,targets,total):
    return np.prod([pr_a_sums(targets,total) for i in range(rounds)])

n=1000
f=1/3
h=1-1/3
print("number of honest nodes in network: {}".format(h))
# there are two viable strategies:
# 1. send to only the minimum number of nodes such that it reaches 50% so
# attacker will mine next round on its own block
# 2. send to half of the honest nodes and attack can mine on any half
# 2 gives higher chances of prob.
# target1=int(n/2 - n/3)
target=int(h*n/2)
print("number of nodes to target: {}".format(target))
low=0.49
high=0.51
targets=range(int(low * n), int(high* n))
rounds=10
print("Probability of successfully targeting one node: {}".format(pr_sj()))
print("Probability of targeting {} nodes: {}".format(target,pr_a(target,h*n)))
print("Probability of targeting [{}n,{}n] nodes: {}".format(low,high,pr_a_sums(targets,h*n)))
print("Probability of running attack for 10 rounds (for target [..]): {}".format(continuous(rounds,targets,h*n)))

# number of time slots: 40
# number of nodes in network: 1000
# Probability of successfully targeting one node: 0.5125
# Probability of targeting 500 nodes: 0.018453214628727465
# Probability of targeting [0.49n,0.51n] nodes: 0.35179843051803916
# Probability of running attack for 10 rounds (for target [..]): 2.9036146305554976e-05
