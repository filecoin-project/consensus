#!/usr/bin/env python3
import utils as u

# This scripts computes the advantage of running the lookfwd attack according to
# the paper formula (lookfwd.pdf)
e=5
att=1/3
honest=1-att

def ratio(e,att):
    honest=1-att
    p0 = u.poisson(0,honest*e)
    b = u.poisson(1, att*e)
    ratio = 1 / (1 - b * p0 * e)
    return ratio

# prob. attacker wins more than 0 times
def att_prb(e,f):
    return 1 - u.poisson_cdf(0,e*att)

# prob. honest wins 0 times
def honest_prb(e,f):
    return u.poisson(0,e*f)

def attacks_happens(e,att,honest):
    return att_prb(e,att) * honest_prb(e,honest)

print("e = {}, attacker fraction = {}".format(e,att))
print("-> ratio is {}".format(ratio(e,att)))
print("-> attacks happens {} fraction of the time".format(attacks_happens(e,att,honest)))
# e = 5, attacker fraction = 0.3333333333333333
# -> ratio is 1.05948988933682
# -> attacks happens 0.035673993347252374 fraction of the time

