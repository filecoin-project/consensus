package main

import (
	"runtime/pprof"
	"strconv"
	"flag"
        "fmt"
        "math/rand"
	"os"
        "sort"
        "time"
)

var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to file")
var uniqueID int
var lbp int

func getUniqueID() int {
	uniqueID += 1
	return uniqueID - 1
}

// Input a set of newly mined blocks, return a map grouping these blocks
// into tipsets that obey the tipset invariants.
func allTipsets(blks []*Block) map[string][]*Block {
        tipsets := make(map[string][]*Block)
        for i, blk1 := range blks {
                tipset := []*Block{blk1}
                for j, blk2 := range blks {
                        if i != j {
                                if stringifyTipset(blk1.Parents) == stringifyTipset(blk2.Parents) &&
                                        blk1.Height == blk2.Height {
                                        tipset = append(tipset, blk2)
                                }
                        }
                }
                key := stringifyTipset(tipset)
                if _, seen := tipsets[key]; !seen {
                        tipsets[key] = tipset
                }
        }
        return tipsets
}

// forkTipsets returns the n subsets of a tipset of length n: for every ticket
// it returns a tipset containing the block containing that ticket and all blocks
// containing a ticket larger than it.  This is a rational miner trying to mine
// all possible non-slashable forks off of a tipset.
func forkTipsets(blks []*Block) [][]*Block {
        sort.Slice(blks, func(i, j int) bool { return blks[i].Seed < blks[j].Seed })       
        var forks [][]*Block
        for i := range blks {
            currentFork := []*Block{blks[i]}
                    for j := i + 1; j < len(blks); j++ {
                            currentFork = append(currentFork, blks[j])
                    }
                    forks = append(forks, currentFork)
        }
        return forks
}

var totalMiners int
const bigOlNum = 100000

type Block struct {
	Nonce int
        Parents []*Block
        Owner int
        Height int
        Null bool
        Weight int
        Seed int64
}

func stringifyTipset(blocks []*Block) string {
    var blockStrings []string
    for _, block := range blocks {
	    blockStrings = append(blockStrings, strconv.Itoa(block.Nonce) + "-")
    }
    sort.Strings(blockStrings)

    var str string
    for _, strBlock := range blockStrings {
        str += strBlock
    }
    return str
}

type RationalMiner struct {
        Power float64
        PrivateForks map[string][]*Block
        ID int
}

func NewRationalMiner(id int, power float64) *RationalMiner {
        return &RationalMiner{
                Power: power,
                PrivateForks: make(map[string][]*Block, 0),
                ID: id,
        }
}

func blocksParents(blocks []*Block) []*Block {
	if len(blocks) == 0 {
		panic("Don't call parents on nil blocks")
	}
	return blocks[0].Parents
}

func blocksHeight(blocks []*Block) int {
        if len(blocks) == 0 {
                panic("Don't call height on nil blocks")
        }
        return blocks[0].Height
}

func blocksWeight(blocks []*Block) int {
        if len(blocks) == 0 {
                panic("Don't call weight on nil blocks")
        }
        return len(blocks) + blocks[0].Weight - 1
}

// Input the base tipset for mining lookbackTipset will return the ancestor
// tipset that should be used for sampling the leader election seed.
func lookbackTipset(blocks []*Block) []*Block {
	for i := 0; i < lbp - 1; i++ {
		blocks = blocksParents(blocks)
	}
	return blocks
}

func retrieveSeed(parents []*Block) int64 {
        // get minTicket from lbp tipset
	lbpAncestor := lookbackTipset(parents)
	minSeed := int64(-1)
        for _, block := range lbpAncestor {
                if minSeed == int64(-1) || block.Seed < minSeed {
                        minSeed = block.Seed
                }
        }
        return minSeed
}

// generateBlock makes a new block with the given parents
func (m *RationalMiner) generateBlock(parents []*Block) *Block {
        // Given parents and id we have a unique source for new ticket
        minTicket := retrieveSeed(parents)
        t := m.generateTicket(minTicket)
        nextBlock := &Block{
		Nonce: getUniqueID(),
                Parents: parents,
                Owner: m.ID,
                Height: blocksHeight(parents) + 1,
                Weight: blocksWeight(parents),
                Seed: t,
        }
        
        if isWinningTicket(t, m.Power) {
                nextBlock.Null = false
                nextBlock.Weight += 1
        } else {
                nextBlock.Null = true
        }

        return nextBlock
}

func isWinningTicket(ticket int64, power float64) bool {
    // this is a simulation of ticket checking: the ticket is drawn uniformly from 0 to bigOlNum * totalMiners.
    // If it is smaller than that * the miner's power (between 0 and 1), it wins.
    return float64(ticket) < float64(bigOlNum) * float64(totalMiners) * power
}

// generateTicket
func (m *RationalMiner) generateTicket(minTicket int64) int64 {
        seed := minTicket + int64(m.ID)
        r := rand.New(rand.NewSource(seed))
        ticket := r.Int63n(int64(bigOlNum * totalMiners))
        return ticket
}

func (m *RationalMiner) SourceAllForks(newBlocks []*Block) {
        // split the newblocks into all potential forkable tipsets
        allTipsets := allTipsets(newBlocks)
        for k := range allTipsets {
                forkTipsets := forkTipsets(allTipsets[k])
                for _, ts := range forkTipsets {
                        m.PrivateForks[stringifyTipset(ts)] = ts
                }
        }
}

// Mine outputs the block that a miner mines in a round where the leaves of
// the block tree are given by newBlocks.  A miner will only ever mine one
// block in a round because if it mines two or more it gets slashed.  #Incentives #Blockchain
func (m *RationalMiner) Mine(newBlocks []*Block) *Block {
        // Start by combining existing pforks and new blocks available to mine atop of
        m.SourceAllForks(newBlocks)

        var nullBlocks []*Block
        maxWeight := 0
        var bestBlock *Block
	fmt.Printf("miner %d.  len priv forks: %d\n", m.ID, len(m.PrivateForks))
        for k := range m.PrivateForks {
                // generateBlock takes in a blocks parent's, as in current head of PrivateForks
                blk := m.generateBlock(m.PrivateForks[k])
                if !blk.Null && blk.Weight > maxWeight {
                        bestBlock = blk
                        maxWeight = blk.Weight
                } else if blk.Null && bestBlock == nil {
                    // if blk is null and we haven't found a winning block yet
                    // we will want to extend private forks with it
                    // no need to do it if blk is not null since the pforks will get deleted anyways
                    nullBlocks = append(nullBlocks, blk)
                }
        }


        // if bestBlock is not null
        if bestBlock != nil {
            // kill all pforks
            m.PrivateForks = make(map[string][]*Block)
        } else {
            // extend null block chain
            for _, nblk := range nullBlocks {
                    delete(m.PrivateForks, stringifyTipset(nblk.Parents))
                    // add the new null block to our private forks
                    m.PrivateForks[stringifyTipset([]*Block{nblk})] = []*Block{nblk}
            }
        }
        return bestBlock
}

// makeGen makes the genesis block.  In the case the lbp is more than 1 it also
// makes lbp -1 genesis ancestors for sampling the first lbp - 1 blocks after genesis
func makeGen() *Block {
	var gen *Block
	for i := 0; i < lbp; i++ {
		gen = &Block{
			Nonce: getUniqueID(),
			Parents: []*Block{gen},
			Owner: -1,
			Height: 9,
			Null: false,
			Weight: 0,
			Seed: rand.Int63n(int64(bigOlNum * totalMiners)),
		}			
	}
	return gen
}

func main() {
	flag.Parse()
	if *cpuprofile != "" {
		f, err := os.Create(*cpuprofile)
		if err != nil {
			panic(err)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}
	uniqueID = 0
        rand.Seed(time.Now().UnixNano())
        roundNum := 100
        totalMiners = 1000
	lbp = 100
        miners := make([]*RationalMiner, totalMiners)
	gen := makeGen()
        for m := 0; m < totalMiners; m++ {
                miners[m] = NewRationalMiner(m, 1.0/float64(totalMiners))
        }
        blocks := []*Block{gen}
        for round := 0; round < roundNum; round++ {
		fmt.Printf("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
		fmt.Printf("Round %d -- %d new blocks\n", round, len(blocks))
		fmt.Printf("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")		
                var newBlocks = []*Block{}
                for _, m := range miners {
                        // Each miner mines
                        blk := m.Mine(blocks)
                        if blk != nil {
                                newBlocks = append(newBlocks, blk)
                        }
                }

                // NewBlocks added to network
                blocks = newBlocks
        }
}
