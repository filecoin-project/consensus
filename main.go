package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"math/rand"
	"sort"
	"time"
)

type Block struct {
	Parents    [][32]byte
	Owner      int
	Height     uint64
	Nonce      int
	NullBlocks uint64
}

func (b *Block) Hash() [32]byte {
	d, _ := json.Marshal(b)
	return sha256.Sum256(d)
}

type Consensus struct {
	Power      map[uint64]uint64
	TotalPower uint64
}

type Message struct {
	Type  string
	Power uint64
	Block *Block
}

type Miner struct {
	id         int
	mypower    int
	totalpower int
	inblocks   chan *Block
	broadcast  func(b *Block)

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
	return time.Second * 5
}

func (m *Miner) mine(genesis *Block) {
	m.chain.addBlock(genesis)
	curHeight := uint64(1)

	blockIn := time.NewTimer(m.getMiningDelay())
	for {
		select {
		case <-blockIn.C:
			if rand.Intn(m.totalpower) < m.mypower {
				parents, pheight := m.chain.getParentsForHeight(curHeight)
				// winner winner chicken dinner
				myblock := &Block{
					Height:     curHeight,
					Nonce:      rand.Intn(100),
					Owner:      m.id,
					Parents:    parents,
					NullBlocks: curHeight - (1 + pheight),
				}
				h := myblock.Hash()
				fmt.Printf("[h:%d m:%d] mined block %x with parents: %x\n", curHeight, m.id, h[:4], hashPrefs(parents))
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

func (cps *candidateParentSet) getBestCandidates() [][32]byte {
	if len(cps.s) == 0 {
		panic("nope")
	}
	if len(cps.s) == 1 {
		sel := cps.opts[0]
		var out [][32]byte
		for _, b := range cps.s[sel] {
			out = append(out, b.Hash())
		}
		return out
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

func (ct *chainTracker) getParentsForHeight(h uint64) ([][32]byte, uint64) {
	for v := h - 1; ; v-- {
		cps := ct.blks[v]
		if cps != nil {
			return cps.getBestCandidates(), v
		}

		if v == 0 {
			panic("shouldnt happen")
		}
	}
}

func main() {
	rand.Seed(time.Now().UnixNano())
	genesis := &Block{
		Nonce: 42,
	}

	numMiners := 10

	var totalPow int
	var miners []*Miner
	for i := 0; i < numMiners; i++ {
		pow := 10 + rand.Intn(10)
		totalPow += pow
		m := &Miner{
			id:       i,
			mypower:  pow,
			inblocks: make(chan *Block, 32),
			chain:    newChainTracker(),
		}
		miners = append(miners, m)
	}

	for _, m := range miners {
		m.broadcast = func(b *Block) {
			for _, m := range miners {
				m.inblocks <- b
			}
		}
		m.totalpower = totalPow
	}

	for _, m := range miners {
		go m.mine(genesis)
	}

	select {}
}
