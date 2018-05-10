package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"os/signal"
	"sort"
	"sync"
	"time"

	"github.com/fatih/color"
)

var colors = []*color.Color{
	color.New(color.BgCyan, color.FgBlack),
	color.New(color.BgHiYellow, color.FgBlack),
	color.New(color.BgMagenta, color.FgBlack),
	color.New(color.BgGreen, color.FgBlack),
	color.New(color.BgHiYellow, color.FgBlack),
	color.New(color.BgHiRed, color.FgBlack),
	color.New(color.BgHiMagenta, color.FgBlack),
}

type Blockstore struct {
	blocks map[[32]byte]*Block
	lk     sync.Mutex
}

func newBlockstore() *Blockstore {
	return &Blockstore{
		blocks: make(map[[32]byte]*Block),
	}
}

func (bs *Blockstore) Put(blk *Block) {
	bs.lk.Lock()
	defer bs.lk.Unlock()
	bs.blocks[blk.Hash()] = blk
}

func (bs *Blockstore) Get(h [32]byte) *Block {
	bs.lk.Lock()
	defer bs.lk.Unlock()
	b, ok := bs.blocks[h]
	if !ok {
		panic("couldnt find block")
	}
	return b
}

type Block struct {
	Parents    [][32]byte
	Owner      int
	Height     uint64
	Nonce      int
	Challenge  int
	NullBlocks uint64
	PWeight    int
	hash       [32]byte
}

func (b *Block) IncrWeight(c *Consensus) int {
	return 10 + ((c.Power[b.Owner] * 100) / c.TotalPower)
}

func (b *Block) Hash() [32]byte {
	if b.hash == [32]byte{} {
		d, _ := json.Marshal(b)
		h := sha256.Sum256(d)
		b.hash = h
	}

	return b.hash
}

func (b *Block) ShortName() string {
	h := b.Hash()
	return fmt.Sprintf("%x", h[:8])
}

type Consensus struct {
	Power      map[int]int
	TotalPower int
	Miners     []*Miner
	Blockstore *Blockstore
}

type Message struct {
	Type  string
	Power uint64
	Block *Block
}

type Miner struct {
	id        int
	inblocks  chan *Block
	netDelay  func(int)
	curHeight uint64

	chain *chainTracker
	wait  *sync.WaitGroup
}

func hashPrefs(h [][32]byte) [][]byte {
	var out [][]byte
	for _, h := range h {
		c := make([]byte, 4)
		copy(c, h[:])
		out = append(out, c)
	}
	return out
}

func (m *Miner) getMiningDelay() time.Duration {
	return time.Second * 2
}

func (m *Miner) broadcast(b *Block) {
	consensus.Blockstore.Put(b)
	for _, om := range consensus.Miners {
		go func(om *Miner) {
			m.netDelay(om.id)
			om.inblocks <- b
		}(om)
	}
}

func (m *Miner) mine(done <-chan struct{}, genesis *Block) {
	m.chain.addBlock(genesis)
	m.curHeight = 1

	blockIn := time.NewTimer(m.getMiningDelay())
	for {
		select {
		case <-blockIn.C:
			// NOTE: in the real implementation, this randomness will be secure
			// randomness from the chain
			challenge := rand.Intn(consensus.TotalPower)
			if challenge < consensus.Power[m.id] {
				parents, pheight, weight := m.chain.getParentsForHeight(m.curHeight)
				// winner winner chicken dinner
				myblock := &Block{
					Height:     m.curHeight,
					Nonce:      rand.Intn(100),
					Owner:      m.id,
					Parents:    parents,
					NullBlocks: m.curHeight - (1 + pheight),
					PWeight:    weight,
					Challenge:  challenge,
				}
				h := myblock.Hash()

				pref := colors[int(m.curHeight)%len(colors)].Sprintf("[h:%d m:%d w:%d i:%d]", m.curHeight, m.id, weight, myblock.IncrWeight(consensus))
				fmt.Printf("%s mined block %x with parents: %x\n", pref, h[:4], hashPrefs(parents))
				m.broadcast(myblock)
			}
			blockIn.Reset(m.getMiningDelay())
			m.curHeight++
		case nblk := <-m.inblocks:
			if err := verifyBlock(nblk); err != nil {
				break
			}
			if nblk.Height == m.curHeight-1 || nblk.Height == m.curHeight {
				m.chain.addBlock(nblk)
			} else {
				fmt.Printf("got unexpected block of height %d when we are mining block %d\n", nblk.Height, m.curHeight)
			}
		case <-done:
			m.wait.Done()
			return
		}
	}
	panic("not reachable")
}

func verifyBlock(blk *Block) error {
	if blk.Challenge >= consensus.Power[blk.Owner] {
		return fmt.Errorf("block was not a winner")
	}

	var parents []*Block
	for _, p := range blk.Parents {
		parents = append(parents, consensus.Blockstore.Get(p))
	}

	w := parents[0].PWeight
	for _, p := range parents {
		w += p.IncrWeight(consensus)
	}
	if w != blk.PWeight {
		fmt.Println("PWeight mismatch!!")
		return fmt.Errorf("block had incorrect PWeight")
	}
	return nil
}

func (m *Miner) mine_bad(done <-chan struct{}, genesis *Block) {
	m.chain.addBlock(genesis)
	curHeight := uint64(1)

	blockIn := time.NewTimer(m.getMiningDelay())
	for {
		select {
		case <-blockIn.C:
			// NOTE: in the real implementation, this randomness will be secure
			// randomness from the chain
			challenge := rand.Intn(consensus.TotalPower)

			if challenge < consensus.Power[m.id] {
				parents, pheight, weight := m.chain.getParentsForHeight(curHeight)

				if len(parents) > 1 {
					drop := parents[len(parents)-1]
					dropblk := consensus.Blockstore.Get(drop)
					weight -= dropblk.IncrWeight(consensus)
					parents = parents[:len(parents)-1]
				}

				// winner winner chicken dinner
				myblock := &Block{
					Height:     curHeight,
					Nonce:      rand.Intn(100),
					Owner:      m.id,
					Parents:    parents,
					NullBlocks: curHeight - (1 + pheight),
					PWeight:    weight,
					Challenge:  challenge,
				}
				h := myblock.Hash()

				pref := colors[int(curHeight)%len(colors)].Sprintf("[h:%d m:%d w:%d i:%d]", curHeight, m.id, weight, myblock.IncrWeight(consensus))
				fmt.Printf("%s BAD mined block %x with parents: %x\n", pref, h[:4], hashPrefs(parents))
				m.broadcast(myblock)
			}
			blockIn.Reset(m.getMiningDelay())
			curHeight++
		case nblk := <-m.inblocks:
			if err := verifyBlock(nblk); err != nil {
				break
			}
			if nblk.Height == curHeight-1 || nblk.Height == curHeight {
				m.chain.addBlock(nblk)
			} else {
				fmt.Printf("got unexpected block of height %d when we are mining block %d\n", nblk.Height, curHeight)
			}
		case <-done:
			m.wait.Done()
			return
		}
	}
}

type candidateParentSet struct {
	s        map[string][]*Block
	height   uint64
	opts     []string
	lessFunc func(a, b []*Block) bool
}

func newCandidateParentSet(h uint64) *candidateParentSet {
	return &candidateParentSet{
		s:      make(map[string][]*Block),
		height: h,
		lessFunc: func(a, b []*Block) bool {
			return weighParentSet(a) < weighParentSet(b)
		},
	}
}

func (cps *candidateParentSet) addNewBlock(b *Block) {
	if b.Height != cps.height {
		panic("ni")
	}
	k := keyForParentSet(b.Parents)
	if cps.s[k] == nil {
		cps.opts = append(cps.opts, k)
	}
	cps.s[k] = append(cps.s[k], b)
}

func weighParentSet(blks []*Block) int {
	if len(blks) == 0 {
		return -1
	}

	var addWeight, pw int

	for i, b := range blks {
		if i == 0 {
			pw = b.PWeight
		} else if b.PWeight != pw {
			panic("blocks in same sibling set had different pweights")
		}
		addWeight += b.IncrWeight(consensus)
	}
	return addWeight + blks[0].PWeight
}

func getParentSetHashes(blks []*Block) [][32]byte {
	var out [][32]byte
	for _, b := range blks {
		out = append(out, b.Hash())
	}
	return out
}

func (cps *candidateParentSet) getBestCandidates() ([][32]byte, int) {
	if len(cps.s) == 0 {
		panic("nope")
	}
	if len(cps.s) == 1 {
		selblks := cps.s[cps.opts[0]]
		return getParentSetHashes(selblks), weighParentSet(selblks)
	}

	var bestParents []*Block

	for _, blks := range cps.s {
		if cps.lessFunc(bestParents, blks) {
			bestParents = blks
		}
	}

	fmt.Println("Chain fork detected!")

	return getParentSetHashes(bestParents), weighParentSet(bestParents)
}

func sortHashSet(h [][32]byte) {
	sort.Slice(h, func(i, j int) bool {
		return bytes.Compare(h[i][:], h[j][:]) < 0
	})
}

func keyForParentSet(parents [][32]byte) string {
	sortHashSet(parents)

	s := ""
	for _, p := range parents {
		s += string(p[:])
	}

	return s
}

type chainTracker struct {
	blks map[uint64]*candidateParentSet
}

func newChainTracker() *chainTracker {
	return &chainTracker{
		blks: make(map[uint64]*candidateParentSet),
	}
}

func (ct *chainTracker) addBlock(b *Block) {
	cps, ok := ct.blks[b.Height]
	if !ok {
		cps = newCandidateParentSet(b.Height)
		ct.blks[b.Height] = cps
	}

	cps.addNewBlock(b)
}

func (ct *chainTracker) getParentsForHeight(h uint64) ([][32]byte, uint64, int) {
	for v := h - 1; ; v-- {
		cps := ct.blks[v]
		if cps != nil {
			p, weight := cps.getBestCandidates()
			return p, v, weight
		}

		if v == 0 {
			panic("shouldnt happen")
		}
	}
}

func writeGraph(height uint64, ct *chainTracker) {
	fmt.Println("writing graph: ", height)
	fi, err := os.Create("chain.dot")
	if err != nil {
		panic(err)
	}

	defer fi.Close()

	fmt.Fprintln(fi, "digraph G {")
	fmt.Fprintln(fi, "\t{\n\t\tnode [shape=plaintext];")
	fmt.Fprint(fi, "\t\t0")
	for cur := uint64(1); cur <= height; cur++ {
		fmt.Fprintf(fi, " -> %d", cur)
	}
	fmt.Fprintln(fi, ";")
	fmt.Fprintln(fi, "\t}")

	fmt.Fprintln(fi, "\tnode [shape=box];")
	for cur := int(height); cur >= 0; cur-- {
		cps, ok := ct.blks[uint64(cur)]
		if !ok {
			continue
		}

		for _, blks := range cps.s {
			fmt.Fprintf(fi, "\t{ rank = same; %d;", cur)
			for _, b := range blks {
				fmt.Fprintf(fi, " \"b%s\";", b.ShortName())
			}
			fmt.Fprintln(fi, " }")
			for _, b := range blks {
				for _, parent := range b.Parents {
					fmt.Fprintf(fi, "\tb%s -> b%x;\n", b.ShortName(), parent[:8])
				}
			}
		}
	}

	fmt.Fprintln(fi, "}\n")
}

var consensus *Consensus

func main() {
	rand.Seed(time.Now().UnixNano())
	genesis := &Block{
		Nonce:   42,
		PWeight: 1,
	}

	numMiners := 10

	var waitWg sync.WaitGroup

	consensus = &Consensus{
		Power:      make(map[int]int),
		Blockstore: newBlockstore(),
	}
	consensus.Blockstore.Put(genesis)
	for i := 0; i < numMiners; i++ {
		pow := 10 + rand.Intn(10)
		consensus.TotalPower += pow
		consensus.Power[i] = pow
		consensus.Miners = append(consensus.Miners, &Miner{
			id:       i,
			inblocks: make(chan *Block, 32),
			chain:    newChainTracker(),
			netDelay: func(int) {
				time.Sleep(time.Duration(rand.Intn(1000)+1) * time.Millisecond)
			},
			wait: &waitWg,
		})
	}

	doneCh := make(chan struct{})

	for i, m := range consensus.Miners {
		waitWg.Add(1)
		if i%2 == 0 {
			go m.mine(doneCh, genesis)
		} else {
			go m.mine_bad(doneCh, genesis)
		}
	}

	c := make(chan os.Signal)
	signal.Notify(c, os.Interrupt)
	select {
	case <-c:
		close(doneCh)
		waitWg.Wait()
		fmt.Println("done")
		writeGraph(consensus.Miners[0].curHeight, consensus.Miners[0].chain)
	}
}
