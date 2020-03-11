#!/usr/bin/env python3
import numpy as np 
import multiprocessing as mp

poisson = np.random.poisson

sim=500 #number of simulations
attacker=1/3 # fraction of attacker power
honest=1-attacker
e=5
Kmax=10#length of the attack
null_blocks=3#how many "grinds" we allow

def nogrinding(e,power,sim,Kmax,init_power):
    forks=[]
    def runsim():
        init = poisson(e*init_power)
        return init+sum([poisson(e*power) for slot in range(Kmax)])
    return [runsim() for i in range(sim)]

# grind_branch grinds on a branch of possiblities in the whole grinding tree
def grind_branch(node):
    weight = node['weight']
    won_blocks = node['won']
    slot = node['slot']
    # constants but allows for parallelism 
    power = node['power']
    e = node['e']
    null = node['null']
    kmax = node['kmax']
    if slot >= kmax:
        return []

    # contains list of new nodes that future grinding attempts will try
    branches = []
    # grinding attempts here means null blocks
    for null_block in range(null+1):
        new_slot = slot + null_block + 1 # one round after i null blocks
        if new_slot >= kmax:
            return branches

        # for the blocks won previously, I can try to grind on each of them
        for trial in range(won_blocks):
            won = poisson(e*power)
            if won == 0:
                continue
            
            new_node = {
                'weight': weight + won - null_block,
                'won': won,
                'slot': new_slot,
                'power': power,
                'e': e,
                'null': null,
                'kmax': kmax,
            }
            branches.append(new_node)

    return branches

def grinding_runsim(info):
    node = {
            'weight': 0,
            'won': 1, ## assumes he starts from one block
            'slot': 0,
            'power': info['power'],
            'e':e,
            'null': info['null'],
            'kmax': info['kmax'],
    }
    if info['headstart'] == True:
        node['won'] = info['e']

    branches = [node]
    max_weight = 0
    # as long as there are possiblities
    while len(branches) > 0:
        # take maximum weight seen so far
        max_local = max(n['weight'] for n in branches)
        if max_local > max_weight:
            max_weight = max_local

        # grind on all branches
        res = map(grind_branch,branches)
        # flatten out results
        branches = [n for subn in res for n in subn if len(n) > 0]
    return max_weight
    
def grinding(e,power,sim,Kmax,null_blocks,headstart=False):
    cpus = mp.cpu_count()
    with mp.Pool(processes=cpus) as pool:
        info = {
           'e':e,
           'power':power,
           'null':null_blocks,
           'kmax': Kmax,
           'headstart': headstart,
        }
        return pool.map(grinding_runsim, [info]*sim)

def quality_chain(attacker, honest):
    return [1 if attacker[i]>=honest[i] else 0 for i in range(sim)]

def run(headstart=False):
    print("Simulation starting with e={}, Kmax={} and null blocks={}".format(e,Kmax,null_blocks))
    print("-> headstart mode: {}".format(headstart))
    cpus = mp.cpu_count()
    print("-> number of CPUs: {}".format(cpus))
    honest_chain = nogrinding(e,honest,sim,Kmax,honest)
    avg_honest = np.average(honest_chain)
    print("-> honest chain weight average: {:.3f}".format(avg_honest))
    attacker_nogrind = nogrinding(e,attacker,sim,Kmax,attacker)
    avg_attacker_ng = np.average(attacker_nogrind)
    print("-> attacker chain weight average no grinding: {:.3f}".format(avg_attacker_ng))
    attacker_grind = grinding(e,attacker,sim,Kmax,null_blocks,headstart)
    avg_attacker_grind = np.average(attacker_grind)
    print("-> attacker chain average with grinding: {:.3f}".format(avg_attacker_grind))

    nogrind_quality = quality_chain(attacker_nogrind,honest_chain)
    nogrind_prob = np.average(nogrind_quality)
    print("-> probability of success when not grinding: {:.3f}".format(nogrind_prob))
    grinding_quality = quality_chain(attacker_grind,honest_chain)
    grinding_prob = np.average(grinding_quality)
    print("-> probability of success when grinding: {:.3f}".format(grinding_prob))

run()
run(headstart=True)
