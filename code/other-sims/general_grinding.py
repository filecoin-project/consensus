#!/usr/bin/env python3
import utils as u
import numpy as np
poisson = np.random.poisson

e=5
att=1/3
h=1-att
max_block=20

def nico2():
    numSims = 100000
    blocksNoGrind=[]
    blocksGrind=[]
    biggerThanExp=0
    blocksLosts=[]
    blocksWins = []
    blocksTotalNoGrind=[]
    failedAttempts=0
    honestBlocks=[]
    for i in range(numSims):
        # honest do not grind
        ch1, ch2 = poisson(h*e),poisson(h*e)
        # attacker is fixed only for first round
        ca = poisson(att*e)
        # only for comparison: attacker that doesn't grind will draw this
        ca2 = poisson(att*e)

        honWins = ch1 + ch2
        tipset = ch1 + ca 

        # round2 : first trial is on all tipset
        maxGrindedBlock = ca2
        foundBigger=0 
        triedAttack=False
        # range is exclusive - assume attacker keeps one block
        # from 1 since I already include the trieal
        for trial in range(1,tipset):
            round2 = poisson(att*e)
            advWin = tipset - trial + round2
            # attacker doesn't believe he can pull off the attack
            if advWin < ch1 + h*e:
                continue

            triedAttack=True
            # attacker can pull off the attack
            if advWin >= honWins:
                # keep the best - that's how much you can win more
                if maxGrindedBlock < round2:
                    maxGrindedBlock = round2
                if maxGrindedBlock > ca2:
                    foundBigger = 1
            # attacker tried attack but it failed

        # he successfully ran the attack
        if foundBigger == 1:
            # how many blocks more he won
            blocksWins.append(ca + maxGrindedBlock)
            blocksTotalNoGrind.append(ca+ca2)
        # he tried but failed the attack
        elif foundBigger == 0 and triedAttack:
            # how many blocks he lost = round1 + round2
            blocksLosts.append(ca + ca2)
            failedAttempts+=1
        # he did not try the attack
        else:
            honestBlocks.append(ca+ca2) 

        
        blocksGrind.append(maxGrindedBlock)
        blocksNoGrind.append(ca2)
        biggerThanExp += foundBigger

    # all blocks that the adversary gets (or could have had) without  grinding
    honest_behavior=sum(blocksTotalNoGrind)+sum(blocksLosts)+sum(honestBlocks)
    # all blocks that adv. gets by grinding
    adv_behavior=sum(blocksWins) + sum(honestBlocks) 
    adv_attacking = adv_behavior / honest_behavior
    avg_grind=np.average(blocksGrind)
    avg_nogrind=np.average(blocksNoGrind)
    avg_block_losts=np.average(blocksLosts)
    avg_additional_block_win=np.average(advWin)
    avg_blocks_total_nogrind=np.average(blocksTotalNoGrind)
    prop_failed_attempts=failedAttempts/numSims
    print("Average # of blocks when not grinding: {:.2f}".format(avg_nogrind))
    print("Average # of blocks when grinding: {:.2f}".format(avg_grind))
    print("Proportion of grinded blocks > expected block: {:.2f}".format(biggerThanExp/numSims))
    print("-> # of blocks losts (grinding): {}".format(sum(blocksLosts)))
    print("-> # of blocks he won (grinding): {}".format(sum(blocksWins)))
    print("-> # of blocks normally won (no grinding): {}".format(sum(blocksTotalNoGrind)))
    print("-> proportion of failed attemps: {}".format(prop_failed_attempts))
    print("-> adv. attacking:  {:.3f}".format(adv_attacking))
    print("Advantage when grinding: {:3f}".format(avg_grind/avg_nogrind))

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


nico2()
