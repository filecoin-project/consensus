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
# target success rate of the rational player
rate_success=0.2

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

def lookfwd_writeup(e,att,honest):
    print("LOOKFWD writeup computations:")
    print("-> ratio for e={} is {}".format(e,ratio(e,att)))
    print("-> ratio for e={} is {}".format(3,ratio(e,att,3)))
    print("-> attacks happens {} fraction of the time".format(attacks_happens(e,att,honest)))
    # e = 5, attacker fraction = 0.3333333333333333
    # -> ratio is 1.05948988933682
    # -> attacks happens 0.035673993347252374 fraction of the time


# lookfwd_attack looks at the feasibility of the attack if there is a rational
# miner that is trying to mine on the first round (where attacker is not sole
# miner) if it sees the attacker "dropped" too many blocks from that round when
# grinding. Rational player must be able to grind more than the chain of the
# attacker at the third round.
# Description:
# Round 1: attacker grinds on all blocks presents, evicting them one by one
# Round 2: attacker is sole winner (so expected number of blocks acc. to power)
# Round 3: two chains:
#           C1: attacker + honest chain
#           C2: rational player that mines on top of round 1, bypassing round 2
def lookfwd_attack(s, e,att,rat,honest,rate_success=0.2):
    print("Attack LOOKFWD computations")
    ## Find the minimum number of blocks that attacker has to keep on the parent
    ## tipset such that rational player is unlikely to mine a heavier chain
    def find_minimum(s,e,att,rat,honest,rate_success):
        exph = e * honest
        expa = e * att
        expr = e * rat
        # = e I know 
        exp_round = exph + expa + expr
        print("-> expected number of honest blocks: {}".format(exph))
        print("-> expected number of attacker blocks: {}".format(expa))
        print("-> expected number of rational blocks: {}".format(expr))
        print("-> expected number of blocks in a round: {}".format(exp_round))

        ## find probability that rational player will find more blocks when attacker
        ## only uses i blocks to mine on from the first round
        ## minimum_inclusion is the minimum number of blocks attacker must
        ## include
        minimum_inclusion = int(exp_round)
        for blocks_kept in range(0,minimum_inclusion):
            round1 = blocks_kept
            round2 = expa
            round3 = expa + exph
            print("\t* Attacker number of blocks in chain: {} -> {:.3f} -> {:.3f}".format(round1,round2,round3))
            # minimum number of blocks rational must mine at round 3 to get heavier 
            # chain > round2 + round3 - "diff between round1 and expected # round1"
            minrat = round2 + round3 - (exp_round - round1)
            # Pr[rational mines more than minrat] = 1 - Pr[rat mines < min_rat]
            pr = 1 - u.binomial_cdf(int(minrat), s*rat, e/s)
            print("\t  Rational player needs to find >= {:.3f} blocks".format(minrat))
            print("\t  Rational probability of having more blocks: {:.3f}".format(pr))
            if pr < rate_success:
                return blocks_kept
        raise Exception("no such numbers!")

    ## minimum number of blocks attacker has to keep
    min_keeping = find_minimum(s,e,att,rat,honest,rate_success)
    togrind_on = e - min_keeping
    print("-> minimum numbers of blocks to keep: {}".format(min_keeping))
    print("-> maximum numbers of blocks to grind on: {}".format(togrind_on))
    adv = ratio(e,att,togrind_on)
    original = ratio(e,att)
    print("-> ratio of the attacker: {:.4f} vs original {:4f}".format(adv,original)) 

print("e = {}, attacker fraction = {}".format(e,att))
lookfwd_writeup(e,att,honest)
lookfwd_attack(s,e,att,rat,honest,rate_success)
