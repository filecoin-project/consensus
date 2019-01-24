package main

import (
	"bytes"
	"sort"
	"sync"

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

// hashPrefs is a helper function that returns the prefixes of each of the
// given hashes, for pretty printing
func hashPrefs(h [][32]byte) [][]byte {
	var out [][]byte
	for _, h := range h {
		c := make([]byte, 4)
		copy(c, h[:])
		out = append(out, c)
	}
	return out
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
