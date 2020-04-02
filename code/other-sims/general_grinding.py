#!/usr/bin/env python3
import utils as u
import numpy as np
poisson = np.random.poisson

e=5
att=1/3
h=1-att
max_block=20

def grindWithHS():
    numSims = 100000
    blocksNoGrind=[]
    blocksGrind=[]
    biggerThanExp=0
    HSBlocksLost=[]
    failedAttempts=0
    noAttackBlocks=[]
    for i in range(numSims):
        # honest do not grind
        ch1, ch2 = poisson(h*e),poisson(h*e)
        # attacker is fixed only for first round
        ca = poisson(att*e)
        # only for comparison: attacker that doesn't grind will draw this
        ca2 = poisson(att*e)

        honWins = ch1 + ch2
        tipset = ch1 + ca 

        # grindingRound: adversary tries the second round again
        # first trial is on the full tipset, then removing one block at a time
        maxGrindedBlock = ca2
        attackSuccess=False
        triedAttack=False
        # from 1 since I already include the first trial to reusing none of the tipset
        for trial in range(1,tipset+1):
            grindRound = poisson(att*e)
            advWin = tipset - trial + grindRound
            
            # simple heuristic where attacker doesn't attack unless
            # they can pull off the attack based on the honest chain's expectation
            # otherwise risk losing their withheld blocks
            if advWin < ch1 + h*e:
                continue

            triedAttack=True
            # attack success -- we assume better network connectivity from attacker
            if advWin >= honWins:
                attackSuccess = True
                # keep the best - that's how much you can win more
                if grindRound > maxGrindedBlock:
                    maxGrindedBlock = grindRound
            # attacker tried attack but it failed

        # adv successfully ran the attack
        if attackSuccess:
            # how many blocks adv won
            blocksGrind.append(ca + maxGrindedBlock)
            # alternatively would have won ca2
            blocksNoGrind.append(ca+ca2)
        # he tried but failed the attack
        elif not attackSuccess and triedAttack:
            # how many blocks he lost = round1 + round2
            HSBlocksLost.append(ca + ca2)
            failedAttempts+=1
        # he did not try the attack
        else:
            noAttackBlocks.append(ca+ca2)

    # all blocks that the adversary gets (or could have had) without  grinding
    honest_behavior=sum(blocksNoGrind)+sum(HSBlocksLost)+sum(noAttackBlocks)
    # all blocks that adv. gets by grinding
    adv_behavior=sum(blocksGrind) + sum(noAttackBlocks) 
    adv_attacking = adv_behavior / honest_behavior
    avg_grind=np.average(blocksGrind)
    avg_nogrind=np.average(blocksNoGrind)
    avg_block_losts=np.average(HSBlocksLost)
    prop_failed_attempts=failedAttempts/numSims
    print("Average # of blocks when not grinding: {:.2f}".format(avg_nogrind))
    print("Average # of blocks when grinding: {:.2f}".format(avg_grind))
    print("-> # of blocks losts (grinding): {}".format(sum(HSBlocksLost)))
    print("-> # of blocks he won (grinding): {}".format(sum(blocksGrind)))
    print("-> # of blocks normally won (no grinding): {}".format(sum(blocksNoGrind)))
    print("-> proportion of failed attemps: {}".format(prop_failed_attempts))
    print("-> adv. attacking:  {:.3f}".format(adv_attacking))
    # adv can only attack every second epoch: 
    # epoch 0, honest blocks are put out, adv decides whether to withhold or not
    # epoch 1, adv attacks (or not): puts out withheld blocks on grinded tipset
    # repeat
    # we account for blocks from both epochs here (preparation and attack)

# in the case without HS the adv can no longer grind on their own blocks 
# lest they get slashed (they've already put them out).
def grindWithoutHS():
    numSims = 100000
    blocksNoGrind=[]
    blocksGrind=[]
    biggerThanExp=0
    HSBlocksLost=[]
    failedAttempts=0
    noAttackBlocks=[]
    for i in range(numSims):
        # honest do not grind
        ch1 = poisson(h*e)
        ca = poisson(att*e)

        tipset = ch1 + ca 
        
        # second round on full tipset
        ca2 = poisson(att*e)
        honWins = tipset + poisson(h*e)

        # grindingRound: adversary tries the second round on subsets of tipset
        
        # first trial is on the full tipset, then removing one block at a time
        # until only left with the adversary's (can't drop those)
        maxGrindedBlock = ca2
        # from 1 since I already include the first trial to reusing none of the tipset
        for trial in range(1,ch1 + 1):
            grindRound = poisson(att*e)
            advWin = tipset - trial + grindRound
            
            # attack success -- we assume better network connectivity from attacker
            if advWin > honWins:
                # keep the best - that's how much you can win more
                if grindRound >= maxGrindedBlock:
                    maxGrindedBlock = grindRound
            # attacker tried attack but it failed

        # adv ran the attack -- if didn't work, still gets ca2 blocks by mining honestly.
        blocksGrind.append(ca + maxGrindedBlock)
        # alternatively would have won ca2 regardless
        blocksNoGrind.append(ca+ca2)

    # all blocks that the adversary gets (or could have had) without  grinding
    honest_behavior=sum(blocksNoGrind)
    # all blocks that adv. gets by grinding
    adv_behavior=sum(blocksGrind)
    adv_attacking = adv_behavior / honest_behavior
    avg_grind=np.average(blocksGrind)
    avg_nogrind=np.average(blocksNoGrind)
    print("Average # of blocks when not grinding: {:.2f}".format(avg_nogrind))
    print("Average # of blocks when grinding: {:.2f}".format(avg_grind))
    print("-> # of blocks he won (grinding): {}".format(sum(blocksGrind)))
    print("-> # of blocks normally won (no grinding): {}".format(sum(blocksNoGrind)))
    print("-> adv. attacking:  {:.3f}".format(adv_attacking))
    # adv can attack every epoch here

def nico():
    maxGrindPr = 0
    maxNoGrindPr = 0
    for hb1 in range(max_block):
        for ab1 in range(max_block):
            for ab2 in range(max_block):
                totalA= ab1 + ab2
                # - 1
                totalGrindPr = 0
                totalNoGrindPr = 0
                for grinded in range(totalA):
                    # HonestToFind
                    # honest must find this value at second round to have 
                    # a heavier chain
                    htf = totalA - grinded
                    if ab1 + ab2 < int(h*e):
                        continue
                    # probability that honest finds less than htf
                    phtf = u.poisson_cdf(htf, h*e)
                    # probability of winning for adversary means:
                    #  1 honest finds hb1 blocks in first round
                    #  2 attacker finds ab1 blocks in first round
                    #  3 honest finds less than htf blocks in second round
                    #  4 attacker finds ab2 blocks in second round
                    p1 = u.poisson(hb1,h*e)
                    p2 = u.poisson(ab1,att*e)
                    p3 = u.poisson_cdf(htf,h*e)
                    p4 = u.poisson(ab2,att*e)
                    pwinA = p1 * p2 * p3 * p4
                    totalGrindPr += pwinA
            
                # probability of winning for adversary that don't grind is
                # computed as the same way as for no grinding but there is only one
                # tentative for the attack, no "for grinded" loop
                # 1. honest finds hb1 blocks in first round
                # 2. attacker finds ab1 blocks in first round
                # 3. honest finds less than totalA at second round
                # 4. attacker finds ab2 blocks in second round
                p1 = u.poisson(hb1,h*e)
                p2 = u.poisson(ab1,att*e)
                p3 = u.poisson_cdf(totalA,h*e)
                p4 = u.poisson(ab2,att*e)
                pwinANoGrind = p1*p2*p3*p4
                totalNoGrindPr += pwinANoGrind

                if totalGrindPr > maxGrindPr:
                    maxGrindPr = totalGrindPr

                if totalNoGrindPr > maxNoGrindPr:
                    maxNoGrindPr = totalNoGrindPr

    print("max probability when grinding {:.4f}".format(maxGrindPr))
    print("max probability when no grinding {:.4f}".format(maxNoGrindPr))
    print("ratio: {:.4f}".format(maxGrindPr/maxNoGrindPr))

print("\nWith HS:")
grindWithHS()
print("\nWithout HS:")
grindWithoutHS()
