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
var totalMiners int
const bigOlNum = 100000
var lbp int

func getUniqueID() int {
        uniqueID += 1
        return uniqueID - 1
}

// Input a set of newly mined blocks, return a map grouping these blocks
// into tipsets that obey the tipset invariants.
func allTipsets(blks []*Block) map[string]*Tipset {
        tipsets := make(map[string]*Tipset)
        for i, blk1 := range blks {
                tipset := []*Block{blk1}
                for j, blk2 := range blks {
                        if i != j {
                                if blk1.Parents.Name == blk2.Parents.Name &&
                                        blk1.Height == blk2.Height {
                                        tipset = append(tipset, blk2)
                                }
                        }
                }
                key := stringifyTipset(tipset)
                if _, seen := tipsets[key]; !seen {
                        tipsets[key] = NewTipset(tipset)
                }
        }
        return tipsets
}

// forkTipsets returns the n subsets of a tipset of length n: for every ticket
// it returns a tipset containing the block containing that ticket and all blocks
// containing a ticket larger than it.  This is a rational miner trying to mine
// all possible non-slashable forks off of a tipset.
func forkTipsets(ts *Tipset) []*Tipset {
        var forks []*Tipset
        // works because blocks are kept ordered in Tipsets
        for i := range ts.Blocks {
            currentFork := []*Block{ts.Blocks[i]}
                    for j := i + 1; j < len(ts.Blocks); j++ {
                            currentFork = append(currentFork, ts.Blocks[j])
                    }
                    forks = append(forks, NewTipset(currentFork))
        }
        return forks
}


// Block
type Block struct {
        Nonce int
        Parents *Tipset
        Owner int
        Height int
        Null bool
        Weight int
        Seed int64
}

// Tipset
type Tipset struct {
    // Blocks are sorted
    Blocks []*Block
    Name string
    MinTicket int64
}

// Tipset helper functions
func NewTipset(blocks []*Block) *Tipset {
    sort.Slice(blocks, func(i, j int) bool { return blocks[i].Seed < blocks[j].Seed })
    minTicket := int64(-1)
    for _, block := range blocks {
            if minTicket == int64(-1) || block.Seed < minTicket {
                    minTicket = block.Seed
            }
    }
    return &Tipset {
        Blocks: blocks,
        Name: stringifyTipset(blocks),
        MinTicket: minTicket,
    }
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

func (ts *Tipset) getHeight() int {
        if len(ts.Blocks) == 0 {
                panic("Don't call height on no parents")
        }
        // Works because all blocks in a tipset have same height (see allTipsets)
        return ts.Blocks[0].Height
}

func (ts *Tipset) getWeight() int {
        if len(ts.Blocks) == 0 {
                panic("Don't call weight on no parents")
        }
        // Works because all blocks in a tipset have the same parent (see allTipsets)
        return len(ts.Blocks) + ts.Blocks[0].Weight - 1
}

func (ts *Tipset) getParents() *Tipset {
        if len(ts.Blocks) == 0 {
                panic("Don't call parents on nil blocks")
        }
        return ts.Blocks[0].Parents
}

// Chain tracker
type chainTracker struct {
    // index tipsets per height
    blocks map[uint64]Tipset

}

// Rational Miner
type RationalMiner struct {
        Power float64
        PrivateForks map[string]*Tipset
        ID int
}

// Rational Miner helper functions
func NewRationalMiner(id int, power float64) *RationalMiner {
        return &RationalMiner{
                Power: power,
                PrivateForks: make(map[string]*Tipset, 0),
                ID: id,
        }
}

// Input the base tipset for mining lookbackTipset will return the ancestor
// tipset that should be used for sampling the leader election seed.
// On LBP == 1, returns itself (as in no farther than direct parents)
func lookbackTipset(tipset *Tipset) *Tipset {
        for i := 0; i < lbp - 1; i++ {
                tipset = tipset.getParents()
        }
        return tipset
}

// generateBlock makes a new block with the given parents
func (m *RationalMiner) generateBlock(parents *Tipset) *Block {
        // Given parents and id we have a unique source for new ticket
        minTicket := lookbackTipset(parents).MinTicket

        t := m.generateTicket(minTicket)
        nextBlock := &Block{
                Nonce: getUniqueID(),
                Parents: parents,
                Owner: m.ID,
                Height: parents.getHeight() + 1,
                Weight: parents.getWeight(),
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
        // rational miner strategy look for all potential minblocks there
        for k := range allTipsets {
                forkTipsets := forkTipsets(allTipsets[k])
                for _, ts := range forkTipsets {
                        m.PrivateForks[ts.Name] = ts
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
                // generateBlock takes in a block's parent tipset, as in current head of PrivateForks
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
            m.PrivateForks = make(map[string]*Tipset)
        } else {
            // extend null block chain
            for _, nblk := range nullBlocks {
                    delete(m.PrivateForks, nblk.Parents.Name)
                    // add the new null block to our private forks
                    nullTipset := NewTipset([]*Block{nblk})
                    m.PrivateForks[nullTipset.Name] = nullTipset
            }
        }
        return bestBlock
}

// makeGen makes the genesis block.  In the case the lbp is more than 1 it also
// makes lbp -1 genesis ancestors for sampling the first lbp - 1 blocks after genesis
func makeGen() *Block {
        var gen *Tipset
        for i := 0; i < lbp; i++ {
                gen = NewTipset([]*Block{&Block{
                        Nonce: getUniqueID(),
                        Parents: gen,
                        Owner: -1,
                        Height: 0,
                        Null: false,
                        Weight: 0,
                        Seed: rand.Int63n(int64(bigOlNum * totalMiners)),
               }})       
        }
        return gen.Blocks[0]
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
