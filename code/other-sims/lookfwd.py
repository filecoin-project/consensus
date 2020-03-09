#!/usr/bin/env python3
import utils as u

# This scripts computes the advantage of running the lookfwd attack according to
# the paper formula (lookfwd.pdf)
# number of blocks
s = 10000
e=5
att=1/3
rat=1/3
honest=1-att-rat

def ratio(e,att,trials=e):
    honest=1-att
    p0 = u.poisson(0,honest*e)
    b = u.poisson(1, att*e)
    ratio = 1 / (1 - b * p0 * trials)
    return ratio

# prob. attacker wins more than 0 times
def att_prb(e,f):
    return 1 - u.poisson_cdf(0,e*att)

# prob. honest wins 0 times
def honest_prb(e,f):
    return u.poisson(0,e*f)

def attacks_happens(e,att,honest):
    return att_prb(e,att) * honest_prb(e,honest)

def simple_lookfwd(e,att,honest):
    print("Simple LOOKFWD computations")
    print("-> ratio is {}".format(ratio(e,att)))
    print("-> ratio for e={} is {}".format(3,ratio(e,att,3)))
    print("-> ratio for e={} is {}".format(1,ratio(e,att,1)))
    print("-> attacks happens {} fraction of the time".format(attacks_happens(e,att,honest)))
    # e = 5, attacker fraction = 0.3333333333333333
    # -> ratio is 1.05948988933682
    # -> attacks happens 0.035673993347252374 fraction of the time

# advanced_lookfwd looks at the feasibility of the attack if there is a rational
# miner that is trying to mine on the first round (where attacker is not sole
# miner) if it sees the attacker "dropped" too many blocks from the tipset
def advanced_lookfwd(s, e,att,rat,honest):
    print("Advanced LOOKFWD computations")
    ## Find the maximum number of blocks that attacker can grind on before the
    ## rational player
    def find_maximum(s,e,att,rat,honest):
        exph = e * honest
        expa = e * att
        print("-> expected number of honest blocks: {}".format(exph))
        print("-> expected number of attacker blocks: {}".format(expa))

        ## find probability that rational player will find more blocks when attacker
        ## only uses i blocks to mine on from the first round
        for i in range(0,int(exph + expa - 1.0)):
            # exp. number of blocks at round 3 using attacker's chain
            # round 1 : i
            # round 2 : expa
            # round 3 : expa + exph
            r3a = int(i + expa + expa + exph)
            # Pr[rational mines more than r3a] = 1 - Pr[rat mines < r3a]
            r3r = 1 - u.binomial_cdf(r3a, s*rat, e/s)
            if r3r >= r3a:
                return i
        raise Exception("no such numbers!")

    max_grinding = find_maximum(s,e,att,rat,honest)
    print("-> maximum grinding attemps allowed: {}".format(max_grinding))
    adv = ratio(e,att,max_grinding)
    print("-> ratio of the attacker: {}".format(adv)) 

print("e = {}, attacker fraction = {}".format(e,att))
simple_lookfwd(e,att,honest)
advanced_lookfwd(s,e,att,rat,honest)
