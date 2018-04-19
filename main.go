package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"math/rand"
	"sort"
	"time"

	"github.com/fatih/color"
)

var colors = []*color.Color{
	color.New(color.BgCyan, color.FgBlack),
	color.New(color.BgHiYellow, color.FgBlack),
	color.New(color.BgMagenta, color.FgBlack),
	color.New(color.BgGreen, color.FgBlack),
	color.New(color.BgHiYellow, color.FgBlack),
	color.New(color.BgHiRed),
	color.New(color.BgHiMagenta, color.FgBlack),
}

type Block struct {
	Parents    [][32]byte
	Owner      int
	Height     uint64
	Nonce      int
	NullBlocks uint64
	PWeight    int
}

func (b *Block) IncrWeight(c *Consensus) int {
	return 10 + ((c.Power[b.Owner] * 100) / c.TotalPower)
}

func (b *Block) Hash() [32]byte {
	d, _ := json.Marshal(b)
	return sha256.Sum256(d)
}

type Consensus struct {
	Power      map[int]int
	TotalPower int
	Miners     []*Miner
}

type Message struct {
	Type  string
	Power uint64
	Block *Block
}

type Miner struct {
	id       int
	inblocks chan *Block
	netDelay func(int)

	chain *chainTracker
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
	for _, om := range consensus.Miners {
		go func(om *Miner) {
			m.netDelay(om.id)
			om.inblocks <- b
		}(om)
	}
}

func (m *Miner) mine(genesis *Block) {
	m.chain.addBlock(genesis)
	curHeight := uint64(1)

	blockIn := time.NewTimer(m.getMiningDelay())
	for {
		select {
		case <-blockIn.C:
			// NOTE: in the real implementation, this randomness will be secure
			// randomness from the chain
			if rand.Intn(consensus.TotalPower) < consensus.Power[m.id] {
				parents, pheight, weight := m.chain.getParentsForHeight(curHeight)
				// winner winner chicken dinner
				myblock := &Block{
					Height:     curHeight,
					Nonce:      rand.Intn(100),
					Owner:      m.id,
					Parents:    parents,
					NullBlocks: curHeight - (1 + pheight),
					PWeight:    weight,
				}
				h := myblock.Hash()
				colors[int(curHeight)%len(colors)].Printf("[h:%d m:%d w:%d] mined block %x with parents: %x", curHeight, m.id, weight, h[:4], hashPrefs(parents))
				color.Unset()
				fmt.Println()
				m.broadcast(myblock)
			}
			blockIn.Reset(m.getMiningDelay())
			curHeight++
		case nblk := <-m.inblocks:
			if nblk.Height == curHeight-1 || nblk.Height == curHeight {
				m.chain.addBlock(nblk)
			} else {
				fmt.Printf("got unexpected block of height %d when we are mining block %d\n", nblk.Height, curHeight)
			}
		}
	}
}

type candidateParentSet struct {
	s      map[string][]*Block
	height uint64
	opts   []string
}

func newCandidateParentSet(h uint64) *candidateParentSet {
	return &candidateParentSet{
		s:      make(map[string][]*Block),
		height: h,
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

func (cps *candidateParentSet) getBestCandidates() ([][32]byte, int) {
	if len(cps.s) == 0 {
		panic("nope")
	}
	if len(cps.s) == 1 {
		sel := cps.opts[0]
		var out [][32]byte
		var addWeight int

		var pw int
		for i, b := range cps.s[sel] {
			if i == 0 {
				pw = b.PWeight
			} else if b.PWeight != pw {
				panic("blocks in same sibling set had different pweights")
			}
			out = append(out, b.Hash())
			addWeight += b.IncrWeight(consensus)
		}
		return out, addWeight + cps.s[sel][0].PWeight
	}
	fmt.Println("Chain fork detected!")
	panic("don't handle this yet")
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

var consensus *Consensus

func main() {
	rand.Seed(time.Now().UnixNano())
	genesis := &Block{
		Nonce:   42,
		PWeight: 1,
	}

	numMiners := 10

	consensus = &Consensus{Power: make(map[int]int)}
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
		})
	}

	for _, m := range consensus.Miners {
		go m.mine(genesis)
	}

	select {}
}
