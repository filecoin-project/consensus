#!/usr/bin/env python3
import numpy as np 
import multiprocessing as mp
import collections as c

poisson = np.random.poisson

sim=500 #number of simulations
attacker=1/3 # fraction of attacker power
honest=1-attacker
e=5
null_blocks=6#how many "grinds" we allow

Node = c.namedtuple("Node",['weight','won','slot'])

def nogrinding(e,power,sim,kmax):
    forks=[]
    def runsim():
        # + 1 to account for round where attack is based off ?
        return sum([poisson(e*power) for slot in range(kmax+1)])
    return [runsim() for i in range(sim)]

# grind_branch grinds on a branch of possiblities in the whole grinding tree
def grind_branch(node,info):
    # constants but allows for parallelism 
    power,e,null,kmax = info['power'],info['e'],info['null'],info['kmax']
    if node.slot >= kmax:
        return []

    # contains list of new nodes that future grinding attempts will try
    branches = []
    # grinding attempts here means null blocks
    for null_block in range(null+1):
        new_slot = node.slot + null_block + 1 # one round after i null blocks
        if new_slot >= kmax:
            return branches

        # for the blocks won previously, I can try to grind on each of them
        for trial in range(node.won):
            won = poisson(e*power)
            if won == 0:
                continue
            
            new_node = Node(weight=node.weight + won - null_block,
                won=won,
                slot=new_slot)
            
            branches.append(new_node)

    return branches

def grinding_runsim(info):
    e = info['e']
    expected_blocks = int(info['power'] * e) + 1
    ## assumes he starts from his own blocks
    node = Node(weight=0, won=expected_blocks,slot=0)
    if info['headstart'] == True:
        # for headstart, he starts grinding on all the blocks presents in the
        # tipset
        node = Node(weight=0, won=info['e'],slot=0)

    branches = [node]
    max_weight = 0
    # as long as there are possiblities
    while len(branches) > 0:
        # take maximum weight seen so far
        max_local = max(n.weight for n in branches)
        if max_local > max_weight:
            max_weight = max_local

        res = []
        # grind on all branches
        for branch in branches:
            newb = grind_branch(branch,info)
            if len(newb) > 0:
                res = res + newb

        branches = res 

    return max_weight
    
def grinding(e,power,sim,kmax,null_blocks,headstart=False,cpus=mp.cpu_count()):
    with mp.Pool(processes=cpus,maxtasksperchild=1) as pool:
        info = { 'e':e, 'power':power, 'null':null_blocks, 'kmax': kmax,
           'headstart': headstart,
        }
        return pool.map(grinding_runsim, [info]*sim)

def quality_chain(attacker, honest):
    return [1 if attacker[i]>=honest[i] else 0 for i in range(sim)]

def run(kmax,null,e,attacker,headstart=False,log=False,cpus=mp.cpu_count()):
    honest = 1 - attacker
    honest_chain = nogrinding(e,honest,sim,kmax)
    avg_honest = np.average(honest_chain)

    attacker_nogrind = nogrinding(e,attacker,sim,kmax)
    avg_attacker_ng = np.average(attacker_nogrind)
    attacker_grind = grinding(e,attacker,sim,kmax,null_blocks,headstart,cpus=cpus)
    avg_attacker_grind = np.average(attacker_grind)

    nogrind_quality = quality_chain(attacker_nogrind,honest_chain)
    nogrind_prob = np.average(nogrind_quality)
    grinding_quality = quality_chain(attacker_grind,honest_chain)
    grinding_prob = np.average(grinding_quality)
    if log == True:
        print("Simulation starting with e={}, kmax={} and null blocks={}".format(e,kmax,null_blocks))
        print("-> headstart mode: {}".format(headstart))
        cpus = mp.cpu_count()
        print("-> number of CPUs: {}".format(cpus))
        print("-> honest chain weight average: {:.3f}".format(avg_honest))
        print("-> attacker chain weight average no grinding: {:.3f}".format(avg_attacker_ng))
        print("-> attacker chain average with grinding: {:.3f}".format(avg_attacker_grind))
        print("-> probability of success when not grinding: {:.3f}".format(nogrind_prob))
        print("-> probability of success when grinding: {:.3f}".format(grinding_prob))
    return avg_honest,avg_attacker_grind,grinding_prob

def run_multiple(kmaxes,nulls,es,attackers,cpus=mp.cpu_count()):
    def f(v):
        if isinstance(v, float):
            return "{:.3f}".format(v)
        return "{}".format(v)

    print("e,attacker,kmax,null,headstart,weight_honest,weight_grinding,prob_success")
    for kmax in kmaxes:
        for null in nulls:
            # failsafe to try low value of kmax
            if null >= kmax:
                if kmax > 2:
                    null=1
                else:
                    null=0
            for e in es:
                for att in attackers:
                    (wh,wa,noheadstart) = run(kmax,null,e,att,cpus=cpus)
                    str1 = map(f,[e,att,kmax,null] + [False,wh,wa,noheadstart])
                    print("{}".format(",".join(str1)))
                    (wh,wa,headstart) = run(kmax,null,e,att,headstart=True,cpus=cpus)
                    str2 = map(f,[e,att,kmax,null] + [True,wh,wa,headstart])
                    print("{}".format(",".join(str2)))
                    


kmaxes = [2,5,10,12,14,20,30]
run_multiple(kmaxes,[5],[e],[attacker])
