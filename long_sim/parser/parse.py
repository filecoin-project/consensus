# Parser parses dot output dotfiles from simulation runs and creates 
# intermediate data structures useful for getting metrics used for analysis.
# This dot file parser is super brittle.  It will break if we change the output
# format and is likely unusable for most dot files.
class Parser:
    def __init__(self, filename):
        self.readAndParse(filename)

    def readAndParse(self, filename):
        # Setup output datastructures.
        self.BackwardEdges = dict()
        self.ForwardEdges = dict()
        self.AllNodes = set()
        self.RankToNode = dict()
        
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
        

if __name__ == '__main__':
    chain = Parser("output-rounds=10-lbp=1-trial=1.dot")
    chain.PrintNodeRank()
    chain.PrintEdgesForwardDirection()
