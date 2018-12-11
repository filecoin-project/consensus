package main

import (
        "encoding/json"
        "fmt"
        "math/rand"
        "gx/ipfs/QmcTzQXRcU2vf8yX5EEboz1BSvWC7wWmeYAKVQmhp8WZYU/sha256-simd" 
        "sort"
        "time"
)

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
        Parents []*Block
        Owner int
        Height int
        Null bool
        Weight int
        Seed int64
}

// Hash returns the hash of this block
func (b *Block) Hash() [32]byte {
        d, _ := json.Marshal(b)
        return sha256.Sum256(d)
}

func stringifyTipset(blocks []*Block) string {
    var blockStrings []string
    for _, block := range blocks {
        h := block.Hash()
        blockStrings = append(blockStrings, string(h[:]))
    }
    sort.Strings(blockStrings)

    var str string
    for _, strBlock := range blockStrings {
        str += strBlock
    }
    return str
}

func (b *Block) ShortName() string {
        h := b.Hash()
        return fmt.Sprintf("%x", h[:8])
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

func parentHeight(parents []*Block) int {
        if len(parents) == 0 {
                panic("Don't call height on no parents")
        }
        return parents[0].Height
}

func parentWeight(parents []*Block) int {
        if len(parents) == 0 {
                panic("Don't call weight on no parents")
        }
        return len(parents) + parents[0].Weight - 1
}

func retrieveSeed(parents []*Block) int64 {
        // get minTicket from tipset
        minTicket := int64(-1)
        for _, block := range parents {
                if minTicket == int64(-1) || block.Seed < minTicket {
                        minTicket = block.Seed
                }
        }
        return minTicket
}

// generateBlock makes a new block with the given parents
func (m *RationalMiner) generateBlock(parents []*Block) *Block {
        // Given parents and id we have a unique source for new ticket
        minTicket := retrieveSeed(parents)
        t := m.generateTicket(minTicket)
        nextBlock := &Block {
                Parents: parents,
                Owner: m.ID,
                Height: parentHeight(parents) + 1,
                Weight: parentWeight(parents),
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

func main() {
        rand.Seed(time.Now().UnixNano())
        gen := &Block{
                Parents: nil,
                Owner: -1,
                Height: 0,
                Null: false,
                Weight: 0,
        }
        roundNum := 1000
        totalMiners = 30
        miners := make([]*RationalMiner, totalMiners)
        for m := 0; m < totalMiners; m++ {
                miners[m] = NewRationalMiner(m, 1.0/float64(totalMiners))
        }
        blocks := []*Block{gen}
        for round := 0; round < roundNum; round++ {
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
                fmt.Printf("Round %d -- %d new blocks\n", round, len(newBlocks))
        }
}
