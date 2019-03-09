import json

# Parse a block tree from json
class BlockTree:
    def __init__(self, filename):
        self.readAndParse(filename)

    def readAndParse(self, filename):
        # Setup output datastructures.
        self.BlocksByNonce = dict()
        self.BlocksByHeight = dict()
        self.Miners = []
        self.TotalNonNull = 0
        
        with open(filename, 'r') as jfile:
            data = json.load(jfile)
            
            # Get all blocks.  Add all into indexes.
            blocks = data["blocks"]
            for block in blocks:
                self.BlocksByNonce[block["nonce"]] = block
                h = block["height"]
                if h not in self.BlocksByHeight:
                    self.BlocksByHeight[h] = []
                self.BlocksByHeight[h].append(block)
                if not block["null"]:
                    self.TotalNonNull += 1
                
            # Get all miners
            self.Miners = data["miners"]

    ### Extract various metrics from the block tree.

    # HeaviestChain returns a set of nonces of blocks that form the heaviest
    # chain in the block tree.
    def HeaviestChain(self):
        length = len(self.BlocksByHeight)
        heaviestTipSet = self.heaviestAtHeight(length-1)
        chain = set()
        for blk in heaviestTipSet:
            chain.add(blk["nonce"])
        cur = heaviestTipSet[0]
        curHeight = cur["height"]
        while curHeight > 0:
            next = parentNonces(cur["tipset"]["name"])
            for nonce in next:
                chain.add(nonce)
            cur = self.BlocksByNonce[next[0]]
            curHeight = cur["height"]
        return chain

    # RatioUsefulBlocks returns the ratio of blocks making it into the 
    # heaviest chain to the total blocks mined.
    def RatioUsefulBlocks(self):
        mainChain = self.HeaviestChain()
        return float(self.countNonNullBlocks(mainChain)) / float(self.TotalNonNull)

    # AvgHeadsPerRound returns the mean number of possible mining heads per
    # round.
    def AvgHeadsPerRound(self):
        acc = 0.0
        numTrials = len(self.BlocksByHeight)
        for round in range(0, numTrials):
            if round in self.BlocksByHeight:
                acc += len(self.BlocksByHeight[round])
                
        return acc / float(numTrials) 

    # NumReorgs returns the number of times that the heaviest tipset in round
    # n was on a different parent than the heaviest tipset at round n - 1.
    def NumReorgs(self):
        count = 0
        # start with genesis
        prevHead = self.headAtHeight(0)
        curHeight = 0
        # traverse chain
        while curHeight < len(self.BlocksByHeight):
            curHeight += 1
            curHead = self.headAtHeight(curHeight)
            # This round the head is a null block
            if curHead == []:
                continue
            # Found a non-null head
            else:
                # check if this head traverses back to the previous one through
                # null blocks.  If not we have a reorg.
                parentNonces = self.nonNullParentNonces(curHead)
                prevNonces = [ block["nonce"] for block in prevHead]
                if set(parentNonces) != set(prevNonces):
                    count += 1
                prevHead = curHead
        return count

    # Return the first non null parent nonces of input tipset child
    def nonNullParentNonces(self, child):
        childBlock = child[0] # all tipset blocks have the same parent so use one
        while True:
            nonces = parentNonces(childBlock["tipset"]["name"])
            if len(nonces) > 1:
                return nonces
            else:
                childBlock = self.BlocksByNonce[nonces[0]]
                if not childBlock["null"]:
                    return nonces
                    

    # return list of blocks representing head tipset at a round if one exists.
    def headAtHeight(self, h):
        blocks = []
        if h not in self.BlocksByHeight:
            return blocks
        for block in self.BlocksByHeight[h]:
            if block["inHead"]:
                blocks.append(block)

        return blocks


    # return blocks of heaviest tipset at height
    def heaviestAtHeight(self, h):
        if h not in self.BlocksByHeight:
            raise "no BlocksByHeight entry at height "

        # make all possible heaviest tipsets
        # tipsets repr with triple: (name, blockset, weightint)
        tipsets = []
        for block in self.BlocksByHeight[h]:
            placed = False
            for ts in tipsets:
                if ts[0]["tipset"]["name"] == block["tipset"]["name"]:
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


