import numpy as np

ntot = 10000
height = 20
p = 1./float(1*ntot)
sim = 4
qs = [.10, .25, .33, .49]
# qs = [k/100.0 for k in range (10, 32, 5)]

for s in range(sim):
    for q in qs:
        nh = round((1-q)*ntot)
        na = round(q*ntot)
        ch = np.random.binomial(nh, p, height)
        ca = np.random.binomial(na, p, height)
        print "attacker power is {q}".format(q = q)
        print "honest is {ch}".format(ch = ch)
        print "advers is {ca}".format(ca = ca)
