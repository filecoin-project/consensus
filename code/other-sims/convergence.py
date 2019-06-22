import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import pdb

print "Takes around 25 mins..."
def confidence_of_k(target, array):
    _sum = 0.0
    for idx, i in enumerate(array):
        # attack will fail
    	if i < target:
            _sum += 1
    # attack succeeds
    return float(len(array) - _sum) / len(array) 

# because of EC's lookback param, adversary can effectively look ahead that many blocks to decide whether to release
# when honest party catches up: is this a real "catch up" or a temporary one?
def should_end_attack(honest_weight, adversarial_weight, honest_chain, adversarial_chain, lookahead):
    assert(len(honest_chain) == len(adversarial_chain))

    # no need to lookahead then, let's just compare the weights.
    if lookahead == 0:
        return adversarial_weight <= honest_weight

    if adversarial_weight > honest_weight:
        return False

    # if we're getting to end of sim, let's not look beyond the end.
    if len(honest_chain) < lookahead:
        lookahead = len(honest_chain)

    # If we are not, let's look ahead to make a choice
    for i in range(lookahead):
        honest_weight += honest_chain[i]
        adversarial_weight += adversarial_chain[i]
        # if at some point in the next lookahead blocks adversary takes over again, cancel the release and wait it out
        if adversarial_weight > honest_weight:
            return False
    # adversary can't take the risk of never getting back on top. Stop the attack.
    return True

lookahead = 0
qs=[k/100.0 for k in range(2, 54, 2)]
# qs=[k/100.0 for k in range(36, 54, 2)]
# qs = [.49]
#blocks_back = range(5, 5250, 250)
blocks_back = range(5, 105, 10)
# How often will adversarial attack succeed?
success_ec = []
success_ec_nohs = []
success_ec_nots = []
# What portion of block will adversary publish?
total_qual_ec = []
total_qual_nohs = []
total_qual_nots = []
ntot=10000
height=5000
# equal power for all miners
p=10./float(1*ntot)
sim=1000

for q in qs:
    nh=round((1-q)*ntot)
    na=round(q*ntot)
    	
    nostart = 0
    noend = 0
    lengths = []
    launched_EC = []
    quality_EC = []
    
    nostart_nohs = 0
    noend_nohs = 0
    lengths_nohs = []
    launched_nohs = []
    quality_nohs = []
    
    nostart_nots = 0
    noend_nots = 0
    lengths_nots = []
    launched_nots = []
    quality_nots = []
    
    for i in range(sim):
        ch = np.random.binomial(nh, p, height)
    	ca = np.random.binomial(na, p, height)
    	# result of flipping a coin nha times, tested 1000 times.
    	# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
    	# put another way, it represents choice between longest honest and longest adv, and not between longest honests
    	praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
    	praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
    
        #####
        ### EC w headstart
        #####
        w_a = 0
    	w_h = 0
        # for qual we are not looking at chains together, but rather at those blocks which will be counted
        q_w_a = 0
        q_w_h = 0
    	start = -2
    	end = -1
    	wt_at_start = -1
        maxLen = -1
        EC_num_atk = 0
    	for idx, j in enumerate(ca):
            # start attack	
    	    if j>0 and start < 0:
                w_h = ch[idx]
    		# headstart
    		w_a = j + w_h
                # both will be counted
                q_w_a += j
                q_w_h += ch[idx]
    		start = idx
                EC_num_atk += 1
    	    # end attack
            elif start >= 0 and should_end_attack(w_h, w_a, ch[idx+1:], ca[idx+1:], lookahead) and (wt_at_start < 0 or wt_at_start != w_h):
                end = idx
                # compare to current longest successful attack in this sim.
                if end - start > maxLen:
                    maxLen = end - start
                # attacker is sole winner (note that we assume attacker has better connectivity,
                # ie will always win in case of equal weighted chains -- this is a worst case)
                q_w_a += j
    	        # reset to run attack again
                start = -1
                end = -1
            # attack didn't start and sim ends
            elif start < -1 and idx == height - 1:
                nostart += 1
                q_w_a += j
                q_w_h += ch[idx]
            # attack didn't end and sim ends
    	    elif start >= 0 and end < 0 and idx == height - 1:
                noend += 1
	    	# stop attack here successfully. account for max
                q_w_a += j
                if height - start > maxLen:
                    maxLen = height - start
    	    # move forward each step
            else:
                w_h += ch[idx]
    		w_a += j
                q_w_h += ch[idx]
                q_w_a += j
        
        # at end of sim, append longest
    	lengths.append(maxLen)
        launched_EC.append(EC_num_atk)
        # account for chain quality
        quality_EC.append(float(q_w_a)/(q_w_h + q_w_a))
        
        #####
        ### EC wo headstart
        #####
        w_a = 0
    	w_h = 0
        q_w_a = 0
        q_w_h = 0
    	start = -2
    	end = -1
    	wt_at_start = -1
        maxLen = -1
        nohs_num_atk = 0
    	for idx, j in enumerate(ca):
            # start attack and with no headstart must make sure the other did not win more.	
            if j > 0 and start < 0 and ca[idx] >= ch[idx]:
                w_h = ch[idx]
    		# no headstart
    		w_a = j
                # only attacker block will be counted
                q_w_a += j
    		start = idx
                nohs_num_atk += 1
    		# only occurs without headstart
    		if w_h == w_a:
                    wt_at_start = w_h
            # end attack
            elif start >= 0 and should_end_attack(w_h, w_a, ch[idx+1:], ca[idx+1:], lookahead) and (wt_at_start < 0 or wt_at_start != w_h):
                end = idx
                q_w_a += j
                # compare to current longest successful attack in this sim.
                if end - start > maxLen:
                    maxLen = end - start
    	        # reset to run again
                start = -1
                end = -1
            # attack didn't start and sim ends
            elif start < -1 and idx == height - 1:
           	nostart_nohs += 1
                q_w_a += j
                q_w_h += ch[idx]
            # attack didn't end and sim ends
            elif start >= 0 and end < 0 and idx == height - 1:
                noend_nohs += 1
                q_w_a += j
	        # stop attack here successfully. account for max
                if height - start > maxLen:
                    maxLen = height - start
            # move forward each step
            else:
           	w_h += ch[idx]
           	w_a += j
                q_w_a += j
                q_w_h += ch[idx]

        # at end of sim, append longest
    	lengths_nohs.append(maxLen)
        launched_nohs.append(nohs_num_atk)
        quality_nohs.append(float(q_w_a)/(q_w_h + q_w_a))

        #####
        ### EC wo tipset
        #####
    	wpraos_h = 0
    	wpraos_a = 0
        q_w_h = 0
        q_w_a = 0
    	end = -1
    	start = -2
    	wt_at_start = -1
        maxLen = -1
        nots_num_atk = 0
    	for idx, j in enumerate(praosa):
            # in this case no need to check if other won: you'll be tied at worst, ie start attack anyways.
    	    if j  > 0 and start < 0:
                wpraos_h = praosh[idx]
    		wpraos_a = j
    		q_w_a += j
                # flag for special case where both win at attack start: prevents attack from ending in 
    		# next round
    		if wpraos_h == wpraos_a:
    			wt_at_start = wpraos_h
    		start = idx
                nots_num_atk += 1
            elif start >= 0 and should_end_attack(wpraos_h, wpraos_a, praosh[idx+1:], praosa[idx+1:], lookahead) and (wt_at_start < 0 or wt_at_start != wpraos_h):
    		end = idx
                q_w_a += j
                # compare to current longest successful attack in this sim.
                if end - start > maxLen:
                    maxLen = end - start
    	        # reset to run again
                start = -1
                end = -1
            elif start < -1 and idx == height - 1:
    		nostart_nots += 1
                q_w_a += j
                q_w_h += praosh[idx]
            elif start >= 0 and end < 0 and idx == height - 1:
    		noend_nots += 1
                q_w_a += j
                if height - start > maxLen:
                    maxLen = height - start
    	    else: 
    		wpraos_h += praosh[idx]
    		wpraos_a += j
                q_w_a += j
                q_w_h += praosh[idx]
    
        # at end of sim, append longest
    	lengths_nots.append(maxLen)
        launched_nots.append(nots_num_atk)
        quality_nots.append(float(q_w_a)/(q_w_h + q_w_a))

    # statement: the median is the distance such that an attacker creates a fork 50% of the time.
    # Q1: how often can the attacker create a fork from the average?
    EC_avg = np.average(lengths)
    nohs_avg = np.average(lengths_nohs)
    nots_avg = np.average(lengths_nots)
    print "\nAttacker power q: {q}%, num of rounds: {height}, num of sims: {sims}, lookahead: {la}".format(q=q*100, sims=sim, height=height, la=lookahead)
    print "EC: num of attacks {num}; num didn't start {nostart}, didn't end {noend}, launched on avg: {launch}\n\tconv: avg {avg}; med {med}; \n\tqual: avg {avg_qual}; med {med_qual}".format(avg=EC_avg, med = np.median(lengths), num=len(lengths), nostart=nostart, noend=noend, launch=np.average(launched_EC), avg_qual=np.average(quality_EC), med_qual=np.median(quality_EC))
    print "EC wo Headstart: num of attacks {num}; num didn't start {nostart}, didn't end {noend}, launched on avg: {launch}\n\tconv: avg {avg}; med {med}; \n\tqual: avg {avg_qual}; med {med_qual}".format(avg=nohs_avg, med = np.median(lengths_nohs), num=len(lengths_nohs), nostart=nostart_nohs, noend=noend_nohs, launch=np.average(launched_nohs), avg_qual=np.average(quality_nohs), med_qual=np.median(quality_nohs))
    print "EC wo TipSets: num of attacks {num}; num didn't start {nostart}, didn't end {noend}, launched on avg: {launch}\n\tconv: avg {avg}; med {med}; \n\tqual: avg {avg_qual}; med {med_qual}".format(avg=nots_avg, med = np.median(lengths_nots), num=len(lengths_nots), nostart=nostart_nots, noend=noend_nots, launch=np.average(launched_nots), avg_qual=np.average(quality_nots), med_qual=np.median(quality_nots))
    
    y_ec = []
    y_nohs = []
    y_nots = []
    # how far back before we can be confident there is no ongoing attack?
    for lookback in blocks_back:
    	ec_value = confidence_of_k(lookback, lengths)
    	nohs_value = confidence_of_k(lookback, lengths_nohs)
        nots_value = confidence_of_k(lookback, lengths_nots)
   	print "EC:              k {avg} will succeed {num}".format(avg=lookback, num=ec_value)
   	print "EC wo headstart: k {avg} will succeed {num}".format(avg=lookback, num=nohs_value)
   	print "EC wo tipsets:   k {avg} will succeed {num}".format(avg=lookback, num=nots_value)
    	y_ec.append(ec_value)
        y_nohs.append(nohs_value)
    	y_nots.append(nots_value)
    
    # store
    assert(len(y_ec) == len(blocks_back))
    success_ec.append(y_ec)
    assert(len(y_nohs) == len(blocks_back))
    success_ec_nohs.append(y_nohs)
    assert(len(y_nots) == len(blocks_back))
    success_ec_nots.append(y_nots)

    # Quality is not dependent on lookback, any successful attack will do it.
    total_qual_ec.append(np.average(quality_EC))
    total_qual_nohs.append(np.average(quality_nohs))
    total_qual_nots.append(np.average(quality_nots))

    # plot for a given q
#    plt.plot(blocks_back, y_ec)
#    plt.plot(blocks_back,y_nohs)
#    plt.plot(blocks_back,y_nots)
#    plt.xlabel("blocks behind")
#    plt.ylabel("chance of success")
#    plt.title("Confirmation time for q={q}".format(q=q))
#    plt.show()
#    fig1 = plt.gcf()
#    fig1.savefig("{q}-confirmationTime.png".format(q=q), format="png")
#    plt.clf()

assert(len(success_ec) == len(qs))
assert(len(success_ec_nohs) == len(qs))
assert(len(success_ec_nots) == len(qs))
assert(len(total_qual_ec) == len(qs))
assert(len(total_qual_nohs) == len(qs))
assert(len(total_qual_nots) == len(qs))

### Prettify for output
print "\nConvergence"
print "EC"
df = pd.DataFrame(success_ec, columns=blocks_back, index=qs)
print df

print "EC without HeadStart"
df = pd.DataFrame(success_ec_nohs, columns=blocks_back, index=qs)
print df

print "EC without TipSets"
df = pd.DataFrame(success_ec_nots, columns=blocks_back, index=qs)
print df

print "\nQuality"
print "EC"
df = pd.DataFrame(total_qual_ec, index=qs)
print df

print "EC without HeadStart"
df = pd.DataFrame(total_qual_nohs, index=qs)
print df

print "EC without TipSets"
df = pd.DataFrame(total_qual_nots, index=qs)
print df
