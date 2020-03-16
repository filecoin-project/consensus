package main

import (
	crypto_rand "crypto/rand"
	"encoding/binary"
	"fmt"
	"runtime"

	xrand "golang.org/x/exp/rand"

	"gonum.org/v1/gonum/stat/distuv"
)

type Node struct {
	Weight int
	Won    int
	Slot   int
}

type Info struct {
	Kmax  int
	Null  int
	Sims  int
	Power float64
	E     int
}

type Distribution interface {
	Rand() float64
}

func (i *Info) HonestDistribution() Distribution {
	return &distuv.Poisson{
		Lambda: float64(i.E) * (1 - i.Power),
		Src:    newSeed(),
	}
}

func (i *Info) AttackerDistribution() Distribution {
	return &distuv.Poisson{
		Lambda: float64(i.E) * (i.Power),
		Src:    newSeed(),
	}
}
func NewInfo(e int, power float64, kmax, null, sims int) *Info {
	return &Info{
		E:     e,
		Power: power,
		Kmax:  kmax,
		Null:  null,
		Sims:  sims,
	}
}

func (i *Info) Rate() float64 {
	return i.Power * float64(i.E)
}

func run_sim(info *Info, sim func(Distribution) int, newRand func() Distribution) []int {
	results := make([]int, info.Sims)
	numCPUs := runtime.NumCPU()
	work := make(chan bool, info.Sims)
	resultsCh := make(chan int, info.Sims)

	worker := func() {
		for _ = range work {
			resultsCh <- sim(newRand())
		}
	}
	for i := 0; i < numCPUs; i++ {
		go worker()
	}

	for i := 0; i < info.Sims; i++ {
		work <- true
	}
	close(work)
	for i := 0; i < info.Sims; i++ {
		results[i] = <-resultsCh
	}
	return results
}

func nogrinding(info *Info, newRand func() Distribution) []int {
	onesim := func(d Distribution) int {
		sum := 0
		for i := 0; i < info.Kmax; i++ {
			sum += int(d.Rand())
		}
		return int(sum)
	}
	return run_sim(info, onesim, newRand)
}

func grind_node(node *Node, info *Info, d Distribution) []Node {
	if node.Slot >= info.Kmax {
		return []Node{}
	}
	var results = []Node{}
	for null := 0; null < info.Null; null++ {
		newslot := node.Slot + null + 1
		if newslot >= info.Kmax {
			return results
		}

		for trial := 0; trial < node.Won; trial++ {
			won := int(d.Rand())
			if won == 0 {
				continue
			}

			results = append(results, Node{
				Won:    won,
				Weight: node.Weight - null + won - trial,
				Slot:   newslot,
			})
		}
	}
	return results
}

func grind_once(info *Info, d Distribution) int {
	firstnode := Node{
		Won:    1,
		Weight: 0,
		Slot:   -1,
	}
	nodes := []Node{firstnode}
	max_weight := 0
	for len(nodes) > 0 {
		// find max
		for _, n := range nodes {
			if n.Weight > max_weight {
				max_weight = n.Weight
			}
		}
		// run grinding
		res := []Node{}
		for _, n := range nodes {
			res = append(res, grind_node(&n, info, d)...)
		}
		nodes = res
	}
	return max_weight
}

func grind(info *Info) []int {
	return run_sim(info, func(d Distribution) int { return grind_once(info, d) }, info.AttackerDistribution)
}

func average_weight(chain []int) float64 {
	sum := 0
	for _, n := range chain {
		sum += n
	}
	return float64(sum)
}

func prob_success(attacker, honest []int) float64 {
	better := 0
	for i := 0; i < len(attacker); i++ {
		if attacker[i] >= honest[i] {
			better++
		}
	}
	return float64(better) / float64(len(attacker))
}

func expected_honestweight(info *Info) float64 {
	exp := float64(info.E) * info.Power
	return exp * float64(info.Kmax)
}

type SimulResult struct {
	HonestWeight  float64
	NoGrindWeight float64
	GrindWeight   float64
	GrindSuccess  float64
}

func run(info *Info) *SimulResult {
	honest := nogrinding(info, info.HonestDistribution)
	attacker_nogrind := nogrinding(info, info.AttackerDistribution)
	attacker_grind := grind(info)
	succ_grinding := prob_success(attacker_grind, honest)
	//attack_weight := weight(attacker_grind)
	//honest_exp_weight := expected_honestweight(info)

	//fmt.Printf("-> attacker weight: %.5f\n", weight(attacker_grind))
	return &SimulResult{
		HonestWeight:  average_weight(honest),
		NoGrindWeight: average_weight(attacker_nogrind),
		GrindWeight:   average_weight(attacker_grind),
		GrindSuccess:  succ_grinding,
	}
}

func run_multiple(infos ...*Info) {
	fmt.Printf("e,attacker,kmax,null,honestw,nogrindw,grindingw,prob_success\n")
	for _, info := range infos {
		res := run(info)
		fmt.Printf("%d,%.3f,%d,%d,%.3f,%.3f,%.3f,%.8f\n", info.E, info.Power, info.Kmax, info.Null, res.HonestWeight, res.NoGrindWeight, res.GrindWeight, res.GrindSuccess)
	}
}

func main() {
	infos := []*Info{}
	power := 1.0 / 3.0
	//power := 1.0 / 10.0
	for _, kmax := range []int{2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15} {
		if kmax <= 5 {
			infos = append(infos, NewInfo(5, power, kmax, 1, 1))
		} else {
			infos = append(infos, NewInfo(5, power, kmax, 5, 1))
		}
	}
	run_multiple(infos...)
}

func newSeed() xrand.Source {
	var b [8]byte
	_, err := crypto_rand.Read(b[:])
	if err != nil {
		panic("cannot seed math/rand package with cryptographically secure random number generator")
	}
	return xrand.NewSource(uint64(binary.LittleEndian.Uint64(b[:])))
}
