# Parser parses dot output dotfiles from simulation runs and creates 
# intermediate data structures useful for getting metrics used for analysis.
# This dot file parser is super brittle.  It will break if we change the output
# format and is likely unusable for most dot files.
import argparse

class Parser:
    def __init__(self, filename):
        self.readAndParse(filename)

    def readAndParse(self, filename):
        # Setup output datastructures.
        self.BackwardEdges = dict()
        self.ForwardEdges = dict()
        self.AllNodes = set()
        self.RankToNode = dict()
        self.NodeToRank = dict()
        
        with open(filename, 'r') as dotfile:
            lines = dotfile.readlines()
            
            # Make sure format is as expected and trim header lines.
            assert(lines[4].strip() == "}")
            assert(lines[5].strip() == "node [shape=box];")
            lines = lines[6:]

            # Iterate once adding all nodes.
            for line in lines:
                line = line.strip()
                if line == "}":
                    # done parsing
                    break
                if line[0] == "{":
                    self.parseNodeLine(line)

            # Iterate again adding all edges.
            for line in lines:
                line = line.strip()
                if line == "}":
                    # done parsing
                    return
                if line[0] != "{":
                    self.parseEdgeLine(line)
                
                    
            
    # Parse a line of the dot file specifying nodes (i.e. blocks)
    # ex: { rank = same; 78; "b6171 (m7)"; "b6199 (m8)"; }
    def parseNodeLine(self, nodesStr):
        nodesStr = nodesStr.strip("{}") # strip brackets
        nodesStr = nodesStr.rstrip() # strip whitespace
        nodesStr = nodesStr.rstrip(";") # strip trailing semicolon
        nodeStrs = nodesStr.split(";") # split on semicolon
        assert(len(nodeStrs) >= 3)
        assert(nodeStrs[0].strip() == "rank = same")
        rank = int(nodeStrs[1].strip())
        for nodeStr in nodeStrs[2:]:
            nodeStr = nodeStr.strip()
            self.AllNodes.add(nodeStr)
            if not self.RankToNode.has_key(rank):
                self.RankToNode[rank] = []
            self.RankToNode[rank].append(nodeStr)
            self.NodeToRank[nodeStr] = rank

    # Parse a line of the dot file specifying edges (i.e. hash links)
    # ex: "b6485 (m0)" -> "b6440 (m4)";
    def parseEdgeLine(self, edgeStr):
        edgeStr = edgeStr.strip(";")
        edgeNodes = edgeStr.split("->")
        assert(len(edgeNodes) == 2)
        node1 = edgeNodes[0].strip()
        node2 = edgeNodes[1].strip()
        assert(node1 in self.AllNodes)
        assert(node2 in self.AllNodes)
        if not self.BackwardEdges.has_key(node1):
            self.BackwardEdges[node1] = []
        self.BackwardEdges[node1].append(node2)
        if not self.ForwardEdges.has_key(node2):
            self.ForwardEdges[node2] = []
        self.ForwardEdges[node2].append(node1)

    def PrintNodeRank(self):
        print(self.RankToNode)
        for rank in self.RankToNode:
            print("rank -- " + str(rank))
            for node in self.RankToNode[rank]:
                print(node)

            print("\n")

    def PrintEdgesForwardDirection(self):
        for node1 in self.ForwardEdges:
            print("from " + node1)
            for node2 in self.ForwardEdges[node1]:
                print(node1 + " -> " + node2)

            print("\n")                


 

# MainChain returns the genesis block and the set of blocks in the main chain.
# Its argument is a dictionary mapping block ids to their parents.
def makeChain(backwardEdges):
    mainChain = set()
    assert('\"head\"' in backwardEdges)
    mainChain.add('\"head\"')    
    parents = backwardEdges['\"head\"']
    assert(len(parents) > 0)
    for block in parents:
        mainChain.add(block)
    
    while parents[0] in backwardEdges:
        parents = backwardEdges[parents[0]]
        assert(len(parents) > 0)
        for block in parents:
            mainChain.add(block)

    assert(len(parents) == 1)
    return parents[0], mainChain

# avgHeadsPerRound returns the mean number of possible mining heads per round.
# mined in that round.
def avgHeadsPerRound(rankToNode, numTrials):
    acc = 0.0
    for rank in range(0, numTrials):
        if rank in rankToNode:
            acc += len(rankToNode[rank]) 
    return acc / float(numTrials)

# ratioUsefulBlocks returns the ratio of blocks that make it into the main chain
# to total blocks mined
def ratioUsefulBlocks(backwardEdges, allBlocks):
    _, mainChain = makeChain(backwardEdges)
    return float(len(mainChain)) / float(len(allBlocks))

# countRounds calculates the latest round of a block of a fork.
def countRounds(forkBlock, forwardEdges, nodeToRank):
    if forkBlock not in forwardEdges:
        return nodeToRank[forkBlock]        
    else:
        children = forwardEdges[forkBlock]
        assert(len(children) > 0)
        counts = []
        for child in children:
            counts.append(countRounds(child, forwardEdges, nodeToRank))
        return max(counts)
        

# avgMaxForkLength calculates the longest branch of every fork that shares a
# base with a main chain block.  It then averages these lengths together.
def avgMaxForkRound(forwardEdges, backwardEdges, nodeToRank):
    genesis, mainChain = makeChain(backwardEdges)
    maxForkLengths = []
    mainTipset = set()
    mainTipset.add(genesis)
    while '\"head\"' not in mainTipset:
        nextMain = set()
        nextForks = set()

        # Enumerate children, separating out into mainChain and forks.
        for b in mainTipset:
            next = forwardEdges[b]
            for a in next:
                if a in mainChain:
                    nextMain.add(a)
                else:
                    nextForks.add(a)

        # Calculate depth of forks coming from this tipset..
        for forkBlock in nextForks:
            maxForkLengths.append(countRounds(forkBlock, forwardEdges, nodeToRank) - nodeToRank[forkBlock] + 1)

        # Continue traversal on next tipset
        mainTipset = nextMain
        assert(len(mainTipset) > 0)

    return maxForkLengths


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Pass in a .dot file.", default="output-rounds=100-lbp=1-trial=1.dot")
    args = parser.parse_args()
    chain = Parser(args.input)
    print(avgHeadsPerRound(chain.RankToNode, 10))
    print(ratioUsefulBlocks(chain.BackwardEdges, chain.AllNodes))
    print(avgMaxForkRound(chain.ForwardEdges, chain.BackwardEdges, chain.NodeToRank))
