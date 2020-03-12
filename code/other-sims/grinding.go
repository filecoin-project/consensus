package main

import (
	"fmt"
	"runtime"

	"github.com/atgjack/prob"
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
	ph    *prob.Poisson
	pa    *prob.Poisson
}

func NewInfo(e int, power float64, kmax, null, sims int) *Info {
	ph, _ := prob.NewPoisson((1.0 - power) * float64(e))
	pa, _ := prob.NewPoisson(power * float64(e))
	return &Info{
		E:     e,
		Power: power,
		Kmax:  kmax,
		Null:  null,
		Sims:  sims,
		ph:    &ph,
		pa:    &pa,
	}
}

func (i *Info) Rate() float64 {
	return i.Power * float64(i.E)
}

func run_sim(info *Info, sim func() int) []int {
	results := make([]int, info.Sims)
	numCPUs := runtime.NumCPU()
	work := make(chan bool, info.Sims)
	resultsCh := make(chan int, info.Sims)

	worker := func() {
		for _ = range work {
			resultsCh <- sim()
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

func nogrinding(info *Info, draw func() float64) []int {
	onesim := func() int {
		sum := 0
		for i := 0; i < info.Kmax; i++ {
			sum += int(draw())
		}
		return int(sum)
	}
	return run_sim(info, onesim)
}

func grind_node(node *Node, info *Info) []Node {
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
			won := int(info.pa.Random())
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

func grind_once(info *Info) int {
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
			res = append(res, grind_node(&n, info)...)
		}
		nodes = res
	}
	return max_weight
}

func grind(info *Info) []int {
	return run_sim(info, func() int { return grind_once(info) })
}

func weight(chain []int) float64 {
	sum := 0
	for _, n := range chain {
		sum += n
	}
	return float64(sum) / float64(len(chain))
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

type SimulResult struct {
	HonestWeight  float64
	NoGrindWeight float64
	GrindWeight   float64
	GrindSuccess  float64
}

func run(info *Info) *SimulResult {
	honest := nogrinding(info, info.ph.Random)
	attacker_nogrind := nogrinding(info, info.pa.Random)
	//succ := prob_success(attacker_nogrind, honest_nogrind)
	//fmt.Printf("-> attacker's success: %.3f\n", succ)

	attacker_grind := grind(info)
	succ_grinding := prob_success(attacker_grind, honest)
	//fmt.Printf("-> attacker grinding success: %.5f\n", succ_grinding)
	return &SimulResult{
		HonestWeight:  weight(honest),
		NoGrindWeight: weight(attacker_nogrind),
		GrindWeight:   weight(attacker_grind),
		GrindSuccess:  succ_grinding,
	}
}

func run_multiple(infos ...*Info) {
	fmt.Printf("e,attacker,kmax,null,honestw,nogrindw,grindingw,prob_success\n")
	for _, info := range infos {
		res := run(info)
		fmt.Printf("%d,%.3f,%d,%d,%.3f,%.3f,%.3f,%.3f\n", info.E, info.Power, info.Kmax, info.Null, res.HonestWeight, res.NoGrindWeight, res.GrindWeight, res.GrindSuccess)
	}
}

func main() {
	infos := []*Info{}
	for _, kmax := range []int{2, 5, 6, 7, 8, 9, 10, 11, 12, 13} {
		if kmax <= 5 {
			infos = append(infos, NewInfo(5, 1.0/3.0, kmax, 1, 1000))
		} else {
			infos = append(infos, NewInfo(5, 1.0/3.0, kmax, 5, 1000))
		}
	}
	run_multiple(infos...)
}
