import argparse
import subprocess
import importlib
import json_parse
import os
from os import listdir
from os.path import isfile, join

PROGRAM = "./ec-sim-zs"

def buildArgs(miners=-1, lbp=-1, trials=-1, rounds=-1, output="../output"):
    params = ""
    if rounds > 0:
        params += " -rounds={}".format(rounds)
    if miners > 0:
        params += " -miners={}".format(miners)
    if lbp > 0:
        params += " -lbp={}".format(lbp)
    if trials > 0:
        params += " -trials={}".format(trials)
    params += " -output={}".format(output)

    return params

def forksByNumberOfMiners():
    miners = range(1, 1000, 50)
    lbps = range(1, 200, 5)
    miners = 10
    lbp = 1
    trials = 2
    rounds = 500

    outputDir="output/forks-by-minersNum"

    command = "{command}{params}".format(command=PROGRAM, params=buildArgs(miners,lbp,trials,rounds, outputDir))
    print command
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    print "output was {output}\n-*-*-*\nerr was {error}".format(output=out, error=err)
    
    onlyfiles = [join(outputDir, f) for f in listdir(outputDir) if isfile(join(outputDir, f))]
    for f in onlyfiles:
        Tree = blocktree.BlockTree(f)
        print(Tree.RatioUsefulBlocks())

if __name__ == "__main__":
    forksByNumberOfMiners()

    
