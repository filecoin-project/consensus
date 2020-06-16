import json
import pdb
from collections import defaultdict

# Parse a block tree from json
class BlockTree:
    def __init__(self, filename):
        self.readAndParse(filename)

    def readAndParse(self, filename):
        # Setup output datastructures.
        self.BlocksByNonce = dict()
        self.BlocksByRound = dict()
        self.BlocksByParentWeight = dict()
        self.MaxWeight = 0
        self.Miners = []
        self.TotalNonNull = 0
        
        with open(filename, 'r') as jfile:
            data = json.load(jfile)
            print "loaded {file}".format(file=filename)

            # Get all blocks.  Add all into indexes.
            blocks = data["blocks"]
            for block in blocks:
                self.BlocksByNonce[block["nonce"]] = block
                r = block["round"]
                if r not in self.BlocksByRound:
                    self.BlocksByRound[r] = []
                self.BlocksByRound[r].append(block)
                w = block["parentWeight"]
                if w not in self.BlocksByParentWeight:
                    self.BlocksByParentWeight[w] = []
                self.BlocksByParentWeight[w].append(block)
                if w > self.MaxWeight:
                    self.MaxWeight = w
                if not block["null"]:
                    self.TotalNonNull += 1
            print "parsed blocks"

            # Get all miners
            self.Miners = data["miners"]
            print "parsed miners"

    ### Extract various metrics from the block tree.

    # HeaviestChains returns an array of sets of nonces of blocks that form the heaviest
    # chain in the block tree.
    def HeaviestChains(self):
        # get the heaviest live TipSets
        heaviestBlocks = []
        maxWeight = self.MaxWeight
        while not heaviestBlocks:
            heaviestBlocks = filter(lambda x: not x["null"], self.BlocksByParentWeight[maxWeight])
            maxWeight -= 1

        heaviestTipsets = dict()
        for block in heaviestBlocks:
            # actually go through the direct parent: ie incl null blocks
            parentsName = block["directParent"]["name"]
            if not parentsName in heaviestTipsets:
                heaviestTipsets[parentsName] = []
            heaviestTipsets[parentsName].append(block)

        chains = []
        for tipset in heaviestTipsets.keys():
            chain = set()
            heaviestTS = heaviestTipsets[tipset]
            for blk in heaviestTS:
                chain.add(blk["nonce"])
            # all will have the same parents and round so only need to take first
            cur = heaviestTS[0]
            curRound = cur["round"]
            while curRound > 0:
                next = parentNonces(cur["directParent"]["name"])
                for nonce in next:
                    chain.add(nonce)
                cur = self.BlocksByNonce[next[0]]
                curRound = cur["round"]
            chains += sorted(chain)
        return chains
        # TODO: potentially do something if there are multiple chains of same weight (unlikely)

    # RatioUsefulBlocks returns the ratio of blocks making it into the 
    # heaviest chain to the total blocks mined.
    def RatioUsefulBlocks(self):
        mainChain = self.HeaviestChains()[0]
        return float(self.countNonNullBlocks(mainChain)) / float(self.TotalNonNull)

    # AvgHeadsPerRound returns the mean number of possible mining heads per
    # round.
    def AvgHeadsPerRound(self):
        acc = 0.0
        numTrials = len(self.BlocksByRound)
        for round in range(0, numTrials):
            if round in self.BlocksByRound:
                acc += len(self.BlocksByRound[round])
                
        return acc / float(numTrials) 

    # NumReorgs returns the number of times that the heaviest tipset in round
    # n was on a different parent than the heaviest tipset at round n - 1.
    def NumReorgs(self):
        # maps length of head to number of times it led to a reorg
        # reorgs[curHeadLen]-># of reorgs
        reorgs = defaultdict(int)
        # length of current head
        curHeadLen = 1
        # start with genesis
        prevHead = self.headAtRound(0)
        curRound = 0
        print "curR: {curR}, chainR: {chainR}".format(curR=curRound, chainR=len(self.BlocksByRound))
        # traverse chain
        while curRound < len(self.BlocksByRound):
            curRound += 1
            curHead = self.headAtRound(curRound)
            # This round the head is a null block
            if curHead == []:
                curHeadLen += 1
                continue
            # Found a non-null head
            else:
                # check if this head traverses back to the previous one through
                # null blocks.  If not we have a reorg.
                _parentNonces = parentNonces(curHead[0]["tipset"]["name"])
                prevNonces = [ block["nonce"] for block in prevHead]
                if set(_parentNonces) != set(prevNonces):
                    reorgs[findBucket(curHeadLen)] += 1
                    # reset curHeadLen
                    curHeadLen = 1
                else:
                    curHeadLen += 1
                prevHead = curHead
        return reorgs

    # return list of blocks representing head tipset at a round if one exists.
    def headAtRound(self, r):
        blocks = []
        if r not in self.BlocksByRound:
            return blocks
        for block in self.BlocksByRound[r]:
            if block["inHead"]:
                blocks.append(block)

        return blocks


    # return blocks of heaviest tipset at round
    def heaviestAtRound(self, r):
        if r not in self.BlocksByRound:
            raise "no BlocksByRound entry at round "

        # make all possible heaviest tipsets
        # tipsets repr with triple: (name, blockset, weightint)
        tipsets = []
        for block in self.BlocksByRound[r]:
            placed = False
            for ts in tipsets:
                if ts[0]["tipset"]["name"] == block["tipset"]["name"] and ts[0]["round"] == block["round"]:
                    ts.append(block)
                    placed = True
                    break
            if not placed:
                tipsets.append([block])

        maxTs = tipsets[0]
        for ts in tipsets:
            if tipsetWeight(ts) > tipsetWeight(maxTs):
                maxTs = ts
                
        return maxTs

    def countNonNullBlocks(self, blockSet):
        count = 0
        for block in blockSet:
            if not self.BlocksByNonce[block]["null"]:
                count += 1
                
        return count

def tipsetWeight(blocks):
    return blocks[0]["parentWeight"] + len(blocks)

def parentNonces(name):
    nonces = name.split('-')
    return [int(nonce) for nonce in nonces]


# 5000 is a max more or less
LENGTHS = [1, 2, 5, 10, 25, 50, 100, 250, 5000]
def findBucket(forkLen):
    for idx, elem in enumerate(LENGTHS):
        if elem > forkLen:
            return elem

