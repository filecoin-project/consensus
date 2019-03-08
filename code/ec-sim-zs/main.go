// example run: ./long_sim -lbp=100 -rounds=10 -miners=10 -trials=100 -output="output"

package main

import (
	crand "crypto/rand"
	"encoding/json"
	"flag"
	"fmt"
	"math/big"
	"math/rand"
	"os"
	"runtime/pprof"
	"sort"
	"strconv"
	"strings"
	"time"
)

var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to file")
var suite bool

var uniqueID int

const bigOlNum = 100000

//**** Utils

func printSingle(content string) {
	if !suite {
		fmt.Printf(content)
	}
}

func getUniqueID() int {
	uniqueID += 1
	return uniqueID - 1
}

func randInt(limit int64) int64 {
	limitBig := big.NewInt(limit)
	n, err := crand.Int(crand.Reader, limitBig)
	if err != nil {
		panic(err)
	}
	return n.Int64()
}

//**** Helpers

// makeGen makes the genesis block.  In the case the lbp is more than 1 it also
// makes lbp -1 genesis ancestors for sampling the first lbp - 1 blocks after genesis
func makeGen(lbp int, totalMiners int) *Block {
	var gen *Tipset
	for i := 0; i < lbp; i++ {
		gen = NewTipset([]*Block{&Block{
			Nonce:   getUniqueID(),
			Parents: gen,
			Owner:   -1,
			Height:  0,
			Null:    false,
			Weight:  0,
			Seed:    randInt(int64(bigOlNum * totalMiners)), // 12, // rand.Int63n(int64(bigOlNum * totalMiners)),
		}})
	}
	return gen.Blocks[0]
}

// Input a set of newly mined blocks, return a map grouping these blocks
// into tipsets that obey the tipset invariants.
/*
// This variant is slower for some bizarre reason... i'm perplexed
func allTipsets(blks []*Block) []*Tipset {
        var tipsets []*Tipset
        for i, blk1 := range blks {
                tipset := []*Block{blk1}
                for _, blk2 := range blks[i+1:] {
                        if blk1.Height == blk2.Height && blk1.Parents.Name == blk2.Parents.Name {
                                tipset = append(tipset, blk2)
                        }
                }
                tipsets = append(tipsets, NewTipset(tipset))
        }
        return tipsets
}
*/

func allTipsets(blks []*Block) map[string]*Tipset {
	tipsets := make(map[string]*Tipset)
	for i, blk1 := range blks {
		tipset := []*Block{blk1}
		for j, blk2 := range blks {
			if i != j {
				if blk1.Height == blk2.Height && blk1.Parents.Name == blk2.Parents.Name {
					tipset = append(tipset, blk2)
				}
			}
		}
		sortBlocks(tipset)
		key := stringifyBlocks(tipset)
		if _, seen := tipsets[key]; !seen {
			tipsets[key] = NewTipset(tipset)
		}
	}
	return tipsets
}

// forksFromTipset returns the n subsets of a tipset of length n: for every ticket
// it returns a tipset containing the block containing that ticket and all blocks
// containing a ticket larger than it.  This is a rational miner trying to mine
// all possible non-slashable forks off of a tipset.
func forksFromTipset(ts *Tipset) []*Tipset {
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

func sortBlocks(blocks []*Block) {
	sort.Slice(blocks, func(i, j int) bool { return blocks[i].Seed < blocks[j].Seed })
}

func stringifyBlocks(blocks []*Block) string {
	// blocks are already sorted... just do the easy thing
	b := new(strings.Builder)
	for i, blk := range blocks {
		b.WriteString(strconv.Itoa(blk.Nonce))
		if i != len(blocks)-1 {
			b.WriteByte('-')
		}
	}
	return b.String()
}

//**** Structs

// Block
type Block struct {
	// Nonce is unique for each block
	Nonce   int     `json:"nonce"`
	Parents *Tipset `json:"tipset"`
	Owner   int     `json:"owner"`
	Height  int     `json:"height"`
	Null    bool    `json:"null"`
	Weight  int     `json:"weight"`
	Seed    int64   `json:"seed"`
}

// Tipset
// bringing in from json would need to manually link blocks into Tipset using name
type Tipset struct {
	// Blocks are sorted
	Blocks    []*Block `json:"-"`
	Name      string   `json:"name"`
	MinTicket int64    `json:"minTicket"`
}

// Chain tracker
type chainTracker struct {
	// index tipsets per height
	blocksByHeight map[int][]*Block `json:"blocksByHeight"`
	blocks         map[int]*Block   `json:"blocks"`
	maxHeight      int              `json:"maxHeight"`
	head           *Tipset          `json:"head"`
	miners         []*RationalMiner `json:"miner"`
}

// Rational Miner
type RationalMiner struct {
	Power        float64            `json:"power"`
	PrivateForks map[string]*Tipset `json:"-"`
	ID           int                `json:"id"`
	TotalMiners  int                `json:"-"`
	Rand         *rand.Rand         `json:"-"`
}

//**** Block helpers

func (b *Block) sansParent() {

}

//**** Tipset helpers

func NewTipset(blocks []*Block) *Tipset {
	sortBlocks(blocks)
	minTicket := int64(-1)
	for _, block := range blocks {
		if minTicket == int64(-1) || block.Seed < minTicket {
			minTicket = block.Seed
		}
	}

	return &Tipset{
		Blocks:    blocks,
		Name:      stringifyBlocks(blocks),
		MinTicket: minTicket,
	}
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

//**** CT Helpers

func NewChainTracker(miners []*RationalMiner) *chainTracker {
	return &chainTracker{
		blocksByHeight: make(map[int][]*Block),
		blocks:         make(map[int]*Block),
		maxHeight:      -1,
		miners:         miners,
	}
}

// setHead updates the heaviest tipset seen by the network.
func (ct *chainTracker) setHead(blocks []*Block) {
	for _, ts := range allTipsets(blocks) {
		if ts.getWeight() > ct.head.getWeight() {
			ct.head = ts
			printSingle(fmt.Sprintf("setting head to %s\n", ts.Name))
		}
	}
}

//**** Miner Helpers

func NewRationalMiner(id int, power float64, totalMiners int, rng *rand.Rand) *RationalMiner {
	return &RationalMiner{
		Power:        power,
		PrivateForks: make(map[string]*Tipset, 0),
		ID:           id,
		TotalMiners:  totalMiners,
		Rand:         rng,
	}
}

// generateBlock makes a new block with the given parents
// note that while it uses a "null block abstraction" rather than ticket arrays as in
// the spec, the result is the same for consensus.
// To that end, we use separate tickets for new ticket generation and election proof generation
// in case there is randomness skew (though can't think of what it would be rn)
func (m *RationalMiner) generateBlock(parents *Tipset, lbp int) *Block {
	// Given parents and id we have a unique source for new ticket
	lotteryTicket := lookbackTipset(parents, lbp).MinTicket
	lastTicket := lookbackTipset(parents, 1).MinTicket

	// generate a new ticket from parent tipset
	t := m.generateTicket(lastTicket)
	// include in new block
	nextBlock := &Block{
		Nonce:   getUniqueID(),
		Parents: parents,
		Owner:   m.ID,
		Height:  parents.getHeight() + 1,
		Weight:  parents.getWeight(),
		Seed:    t,
	}

	// check lotteryTicket to see if the block can be published
	electionProof := m.generateTicket(lotteryTicket)
	if isWinningTicket(electionProof, m.Power, m.TotalMiners) {
		nextBlock.Null = false
		nextBlock.Weight += 1
	} else {
		nextBlock.Null = true
	}

	return nextBlock
}

// generateTicket, simulates a VRF
func (m *RationalMiner) generateTicket(minTicket int64) int64 {
	seed := minTicket + int64(m.ID)
	// r := rand.New(rand.NewSource(seed))
	// return r.Int63n(int64(bigOlNum * m.TotalMiners))

	m.Rand.Seed(seed)
	return m.Rand.Int63n(int64(bigOlNum * m.TotalMiners))
}

func (m *RationalMiner) ConsiderAllForks(atsforks [][]*Tipset) {
	// rational miner strategy look for all potential minblocks there
	for _, forks := range atsforks {
		for _, ts := range forks {
			m.PrivateForks[ts.Name] = ts
		}
	}
}

// Input the base tipset for mining lookbackTipset will return the ancestor
// tipset that should be used for sampling the leader election seed.
// On LBP == 1, returns itself (as in no farther than direct parents)
func lookbackTipset(tipset *Tipset, lbp int) *Tipset {
	for i := 0; i < lbp-1; i++ {
		tipset = tipset.getParents()
	}
	return tipset
}

func isWinningTicket(ticket int64, power float64, totalMiners int) bool {
	// this is a simulation of ticket checking: the ticket is drawn uniformly from 0 to bigOlNum * totalMiners.
	// If it is smaller than that * the miner's power (between 0 and 1), it wins.
	return float64(ticket) < float64(bigOlNum)*float64(totalMiners)*power
}

//**** Main logic

// Mine outputs the block that a miner mines in a round where the leaves of
// the block tree are given by newBlocks.  A miner will only ever mine one
// block in a round because if it mines two or more it gets slashed.
func (m *RationalMiner) Mine(atsforks [][]*Tipset, lbp int) *Block {
	// Start by combining existing pforks and new blocks available to mine atop of
	m.ConsiderAllForks(atsforks)

	var nullBlocks []*Block
	maxWeight := 0
	var bestBlock *Block
	printSingle(fmt.Sprintf("miner %d. number of priv forks: %d\n", m.ID, len(m.PrivateForks)))
	for k := range m.PrivateForks {
		// generateBlock takes in a block's parent tipset, as in current head of PrivateForks
		blk := m.generateBlock(m.PrivateForks[k], lbp)
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

func runSim(totalMiners int, roundNum int, lbp int, c chan *chainTracker) {
	seed := randInt(1 << 62)
	r := rand.New(rand.NewSource(seed)) // TODO: this line is not used right now

	uniqueID = 0
	miners := make([]*RationalMiner, totalMiners)
	chainTracker := NewChainTracker(miners)
	gen := makeGen(lbp, totalMiners)
	chainTracker.head = NewTipset([]*Block{gen})

	for m := 0; m < totalMiners; m++ {
		miners[m] = NewRationalMiner(m, 1.0/float64(totalMiners), totalMiners, r)
	}

	blocks := []*Block{gen}
	// Throughout we represent chains (or forks) as arrays of arrays of Tipsets.
	// Tipsets are possible sets of blocks to mine of off in a given round.
	// Arrays of tipsets represent the multiple choices a miner has in a given
	//     round for a given chain.
	// Arrays of arrays of tipsets represent each chain/fork.
	atsforks := make([][]*Tipset, 0, 50)
	var currentHeight int
	for round := 0; round < roundNum; round++ {
		// Update heaviest chain
		chainTracker.setHead(blocks)

		// Cache blocks for future stats
		for _, blk := range blocks {
			chainTracker.blocks[blk.Nonce] = blk
		}

		// checking an assumption
		if len(blocks) > 0 {
			currentHeight = blocks[0].Height
			// add new blocks if we have any!
			chainTracker.blocksByHeight[currentHeight] = blocks
		}
		for _, blk := range blocks {
			if currentHeight != blk.Height {
				panic("Check your assumptions: all block heights from a round are not equal")
			}
		}

		printSingle(fmt.Sprintf("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"))
		printSingle(fmt.Sprintf("Round %d -- %d new blocks\n", round, len(blocks)))
		for _, blk := range blocks {
			printSingle(fmt.Sprintf("b%d (m%d)\t", blk.Nonce, blk.Owner))
		}
		printSingle(fmt.Sprintf("\n"))
		printSingle(fmt.Sprintf("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"))
		var newBlocks = []*Block{}

		ats := allTipsets(blocks)
		// declaring atsforks outside of loop and reusing it for better mem mgmt
		atsforks = atsforks[:0]
		// map to array
		for _, v := range ats {
			atsforks = append(atsforks, forksFromTipset(v))
		}

		for _, m := range miners {
			// Each miner mines
			blk := m.Mine(atsforks, lbp)
			if blk != nil {
				newBlocks = append(newBlocks, blk)
			}
		}
		// NewBlocks added to network
		printSingle(fmt.Sprintf("\n"))
		blocks = newBlocks
	}
	// height is 0 indexed
	chainTracker.maxHeight = roundNum - 1
	c <- chainTracker
}

//**** IO

// writeChain output a json from which you can rebuild your chain tracker
func writeChain(ct *chainTracker, name string, outputDir string) {
	fmt.Printf(fmt.Sprintf("Writing Out %s\n", name))

	if _, err := os.Stat(outputDir); os.IsNotExist(err) {
		fmt.Printf("HERE")
		err2 := os.MkdirAll(outputDir, 0755)
		if err2 != nil {
			panic(err2)
		}
	}

	fil, err := os.Create(fmt.Sprintf("%s/%s.json", outputDir, name))
	if err != nil {
		panic(err)
	}
	defer fil.Close()

	// What do we need?
	// 1. Nodes: All blocks, including their details.
	// 2. Edges: Included in Node pointer to Tipset

	// open JSON block
	fmt.Fprintln(fil, "{")

	blocks := make([]*Block, 0, len(ct.blocks))
	for _, value := range ct.blocks {
		blocks = append(blocks, value)
	}

	marshalledBlocks, err := json.MarshalIndent(blocks, "", "\t")
	if err != nil {
		panic(err)
	}

	fmt.Fprintln(fil, "\"blocks\":")
	fmt.Fprintln(fil, string(marshalledBlocks))
	fmt.Fprintln(fil, ",")

	// 3. Miners: All minersV
	// This should appropriately capture tipsets as well as full tree.
	// TODO: some form of checksumming for this data (e.g. some stats about tispets or heads over time)
	marshalledMiners, err := json.MarshalIndent(ct.miners, "", "\t")
	if err != nil {
		panic(err)
	}

	fmt.Fprintln(fil, "\"miners\":")
	fmt.Fprintln(fil, string(marshalledMiners))

	// close JSON block
	fmt.Fprintln(fil, "}")
}

// drawChain output a dot graph of the entire blockchain generated by the simulation
func drawChain(ct *chainTracker, name string, outputDir string) {
	fmt.Printf(fmt.Sprintf("Drawing Graph %s\n", name))

	fil, err := os.Create(fmt.Sprintf("%s/%s.dot", outputDir, name))
	if err != nil {
		panic(err)
	}
	defer fil.Close()

	fmt.Fprintln(fil, "digraph G {")
	fmt.Fprintln(fil, "\t{\n\t\tnode [shape=plaintext];")

	// Write out height index alongside the block graph
	fmt.Fprintf(fil, "\t\t0")
	// Start at 1 because we already wrote out the 0 for the .dot file
	for cur := int(1); cur <= ct.maxHeight+1; cur++ {
		fmt.Fprintf(fil, " -> %d", cur)
	}
	fmt.Fprintln(fil, ";")
	fmt.Fprintln(fil, "\t}")

	fmt.Fprintln(fil, "\tnode [shape=box];")
	// Write out the "head" pointer to heaviest chain
	// fmt.Fprintf(fil, "\t{ rank = same; %d;", ct.maxHeight+1)
	// fmt.Fprintln(fil, "\"head\";}")
	// for _, blk := range ct.head.Blocks {
	//	fmt.Fprintf(fil, "\t\"head\" -> \"b%d (m%d)\";\n", blk.Nonce, blk.Owner)
	// }
	// Write out the actual blocks
	for cur := ct.maxHeight; cur >= 0; cur-- {
		// get blocks per height
		blocks, ok := ct.blocksByHeight[cur]

		if cur == 0 {
			fmt.Printf(fmt.Sprintf("at height 0, blocks: %d", len(blocks)))
		}

		// if no blocks at height, skip
		if !ok {
			continue
		}

		// for every block at this height
		fmt.Fprintf(fil, "\t{ rank = same; %d;", cur)

		for _, block := range blocks {
			// print block
			fmt.Fprintf(fil, " \"b%d (m%d)\";", block.Nonce, block.Owner)
		}
		fmt.Fprintln(fil, " }")

		// link to parents
		for _, block := range blocks {
			// genesis has no parents
			if block.Owner == -1 {
				continue
			}
			parents := block.Parents
			// Tipsets with null blocks only contain one block (since null blocks are mined privately)
			// walk back until we find a tipset with a live parent
			for parents.Blocks[0].Null {
				parents = parents.Blocks[0].Parents
			}
			for _, parent := range parents.Blocks {
				fmt.Fprintf(fil, "\t\"b%d (m%d)\" -> \"b%d (m%d)\";\n", block.Nonce, block.Owner, parent.Nonce, parent.Owner)
			}
		}
	}

	fmt.Fprintln(fil, "}\n")
}

func main() {
	fLbp := flag.Int("lbp", 1, "sim lookback")
	fRoundNum := flag.Int("rounds", 100, "number of rounds to sim")
	fTotalMiners := flag.Int("miners", 10, "number of miners to sim")
	fNumTrials := flag.Int("trials", 1, "number of trials to run")
	fOutput := flag.String("output", ".", "output folder")

	flag.Parse()
	lbp := *fLbp
	roundNum := *fRoundNum
	totalMiners := *fTotalMiners
	trials := *fNumTrials
	outputDir := *fOutput

	if trials <= 0 {
		panic("None of your assumptions have been proven wrong")
	}

	if *cpuprofile != "" {
		f, err := os.Create(*cpuprofile)
		if err != nil {
			panic(err)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}

	suite = trials > 1
	var cts []*chainTracker
	c := make(chan *chainTracker, trials)
	for n := 0; n < trials; n++ {
		fmt.Printf("Trial %d\n", n)
		fmt.Printf("-*-*-*-*-*-*-*-*-*-*-\n")
		go runSim(totalMiners, roundNum, lbp, c)
	}
	for result := range c {
		cts = append(cts, result)
		if len(cts) == trials {
			close(c)
		}
		chainName := fmt.Sprintf("rds=%d-lbp=%d-mins=%d-ts=%d-%d", roundNum, lbp, totalMiners, time.Now().Unix(), len(cts))

		// create output folder if it doesn't exist
		if _, err := os.Stat(outputDir); os.IsNotExist(err) {
			os.Mkdir(outputDir, 0700)
		}

		// capture chain for future use
		writeChain(result, chainName, outputDir)

		// if single trial, draw output
		if !suite {
			drawChain(result, chainName, ".")
		}
	}
}
