import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

def confidence_of_k(target, array):
    _sum = 0.0
    for idx, i in enumerate(array):
        # attack will fail
    	if i < target:
            _sum += 1
    # attack succeeds
    return float(len(array) - _sum) / len(array) 
    
# qs=[k/100.0 for k in range(2, 54, 2)]
qs = [.52]
blocks_back = range(5,105, 10)
success_ec = []
success_ec_nohs = []
success_ec_nots = []
ntot=10000
height=2000
# equal power for all miners
p=1./float(1*ntot)
sim=1000

for q in qs:
    nh=round((1-q)*ntot)
    na=round(q*ntot)
    	
    nostart = 0
    noend = 0
    lengths = []
    
    nostart_nohs = 0
    noend_nohs = 0
    lengths_nohs = []
    
    nostart_nots = 0
    noend_nots = 0
    lengths_nots = []
    
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
    	start = -1
    	end = -1
    	wt_at_start = -1
    	for idx, j in enumerate(ca):
            # start attack	
    	    if j>0 and start < 0:
                w_h = ch[idx]
    		# headstart
    		w_a = j + w_h
    	    	# no headstart
    		# w_a = j
    		start = idx
		# only occurs without headstart
    	    	if w_h == w_a:
                    wt_at_start = w_h
    	    # end attack
    	    elif start >= 0 and w_h >= w_a and (wt_at_start < 0 or wt_at_start != w_h):
                end = idx
    		lengths.append(end-start)
    		break
            # attack didn't start and sim ends
            elif start < 0 and idx == height - 1:
                nostart += 1
            # attack didn't end and sim ends
    	    elif start >= 0 and end < 0 and idx == height - 1:
                noend += 1
	    	# account for max
    		end = height
    		lengths.append(end-start)
    	    # move forward each step
            else:
                w_h += ch[idx]
    		w_a += j

        #####
        ### EC wo headstart
        #####
        w_a = 0
    	w_h = 0
    	start = -1
    	end = -1
    	wt_at_start = -1
    	for idx, j in enumerate(ca):
            # start attack and with no headstart must make sure the other did not win more.	
            if j > 0 and start < 0 and ca[idx] >= ch[idx]:
                w_h = ch[idx]
    		# no headstart
    		w_a = j
    		start = idx
    		# only occurs without headstart
    		if w_h == w_a:
                    wt_at_start = w_h
            # end attack
            elif start >= 0 and w_h >= w_a and (wt_at_start < 0 or wt_at_start != w_h):
                end = idx
           	lengths_nohs.append(end-start)
           	break
            # attack didn't start and sim ends
            elif start < 0 and idx == height - 1:
           	nostart_nohs += 1
            # attack didn't end and sim ends
            elif start >= 0 and end < 0 and idx == height - 1:
           	noend_nohs += 1
           	# account for max
           	end = height
           	lengths_nohs.append(end-start)
            # move forward each step
            else:
           	w_h += ch[idx]
           	w_a += j

        #####
        ### EC wo tipset
        #####
    	wpraos_h = 0
    	wpraos_a = 0
    	end = -1
    	start = -1
    	wt_at_start = -1
    	for idx, j in enumerate(praosa):
            # in this case no need to check if other won: you'll be tied at worst, ie start attack anyways.
    	    if j  > 0 and start < 0:
                wpraos_h = praosh[idx]
    		wpraos_a = praosa[idx]
    		# flag for special case where both win at attack start: prevents attack from ending in 
    		# next round
    		if wpraos_h == wpraos_a:
    			wt_at_start = wpraos_h
    		start = idx
            elif start >= 0 and wpraos_h >= wpraos_a and (wt_at_start < 0 or wt_at_start != wpraos_h):
    		end = idx
    		lengths_nots.append(end-start)
    		break
            elif start < 0 and idx == height - 1:
    		nostart_nots += 1
            elif start >= 0 and end < 0 and idx == height - 1:
    		noend_nots += 1
    		end = height
    		lengths_nots.append(end-start)
    	    else: 
    		wpraos_h += praosh[idx]
    		wpraos_a += praosa[idx]
    
    # statement: the median is the distance such that an attacker creates a fork 50% of the time.
    # Q1: how often can the attacker create a fork from the average?
    EC_avg = np.average(lengths)
    nohs_avg = np.average(lengths_nohs)
    nots_avg = np.average(lengths_nots)
    print "Attacker power q: {q}%".format(q=q*100)
    print "EC: avg {avg}; med {med}; num of attacks {num}; num didn't start {nostart}, didn't end {noend}".format(avg=EC_avg, med = np.median(lengths), num=len(lengths), nostart=nostart, noend=noend)
    print "EC wo Headstart: avg {avg}; med {med}; num of attacks {num}; num didn't start {nostart}, didn't end {noend}".format(avg=nohs_avg, med = np.median(lengths_nohs), num=len(lengths_nohs), nostart=nostart_nohs, noend=noend_nohs)
    print "EC wo TipSet: avg {avg}; med {med}; num of attacks {num}; num didn't start {nostart}, didn't end {noend}".format(avg=nots_avg, med = np.median(lengths_nots),num=len(lengths_nots), nostart=nostart_nots, noend=noend_nots)		
    
    y_ec = []
    y_nohs = []
    y_nots = []
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

    # plot for a given q
    plt.plot(blocks_back, y_ec)
    plt.plot(blocks_back,y_nohs)
    plt.plot(blocks_back,y_nots)
    plt.xlabel("blocks behind")
    plt.ylabel("chance of success")
    plt.title("Confirmation time for q={q}".format(q=q))
    plt.show()
   #  fig1 = plt.gcf()
   #  fig1.savefig("{q}-confirmationTime.png".format(q=q), format="png")
   #  plt.clf()

assert(len(success_ec) == len(qs))
assert(len(success_ec_nohs) == len(qs))
assert(len(success_ec_nots) == len(qs))

### Prettify for output

print "EC"
df = pd.DataFrame(success_ec, columns=blocks_back, index=qs)
print df

print "EC without HeadStart"
df = pd.DataFrame(success_ec_nohs, columns=blocks_back, index=qs)
print df

print "EC without TipSets"
df = pd.DataFrame(success_ec_nots, columns=blocks_back, index=qs)
print df

