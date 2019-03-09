# system utils
import argparse
import subprocess
import os
from os import listdir
from os.path import isfile, join

# simulation output parser 
import blocktree

# plotting
import matplotlib.pyplot as plt

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
        print(Tree.AvgHeadsPerRound())


def sweepByMinersAndLBP(miners, lbps, trials, rounds, sweepDir):
    data = dict()
    for lbp in lbps:
        lbpDir = sweepDir + "/lbp-" + str(lbp)
        data[lbp] = dict()
        for m in miners:
            data[lbp][m] = []
            outputDir = lbpDir + "/miner-" + str(m)
            command = "{command}{params}".format(command=PROGRAM, params=buildArgs(m,lbp,trials,rounds, outputDir))     
            print command
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            out, err = p.communicate()
            print "output was {output}\n-*-*-*\nerr was {error}".format(output=out, error=err)
            onlyfiles = [join(outputDir, f) for f in listdir(outputDir) if isfile(join(outputDir, f))]
            for f in onlyfiles:
                tree = blocktree.BlockTree(f)
                print(tree.AvgHeadsPerRound())

# readSweepData traverses the directories of a sweep output, runs metrics on 
# the outputs and returns a map data[lbp][minerNum][metric] to data series.
def readSweepData(miners, lbps, metrics, sweepDir):
    data = dict() # data[lbp][minerNum][metric] is a list of metrics
    for lbp in lbps:
        lbpDir = sweepDir + "/lbp-" + str(lbp) 
        data[lbp] = dict()
        for m in miners:
            outputDir = lbpDir + "/miner-" + str(m)
            data[lbp][m] = dict()
            for metric in metrics:
                data[lbp][m][metric] = []
            # traverse files
            onlyfiles = [join(outputDir, f) for f in listdir(outputDir) if isfile(join(outputDir, f))]
            for f in onlyfiles:
                tree = blocktree.BlockTree(f)
                for metric in metrics:
                    if metric == "AvgHeadsPerRound":
                        data[lbp][m][metric].append(tree.AvgHeadsPerRound())
    return data

# plotMetricSweep plots the mean value of a metric varying over the number of miners
# mining on the chain.  It plots multiple series, one for each lbp value in the
# sweep.
def plotMetricSweep(data, metric):
    lbps = sorted([lbp for lbp in data])
    for lbp in lbps:
        series = []
        minerNums = sorted([m for m in data[lbp]])
        for m in minerNums:
            trialValues = data[lbp][m][metric]
            series.append(sum(trialValues) / len(trialValues))
        plt.plot(minerNums, series, 'x-')
    plt.xlabel("Number of miners")
    plt.ylabel(metric)
    plt.legend(["k="+str(lbp) for lbp in sorted(lbps)] , loc='upper right')
    plt.title(metric + " varied over miner number and lookback parameter k")
    plt.show()
        
                
# plot value of chain metrics through a sweep of miner number and lookback
# parameters.  metrics is a list of strings, each corresponding to a metric
# identifier.
def plotSweep(miners, lbps, metrics, sweepDir):
    # Gather data from sweep output artifacts.
    data = readSweepData(miners, lbps, metrics, sweepDir)

    # Plot data for each metric
    for metric in metrics:
        plotMetricSweep(data, metric)
                

if __name__ == "__main__":
    miners = [10, 50, 100, 500]
    lbps = [5, 10, 50]
    trials = 2
    rounds = 500
    sweepDir = "output/sweep"

#    sweepByMinersAndLBP(miners, lbps, trials, rounds, sweepDir)
    plotSweep(miners, lbps, ["AvgHeadsPerRound"], sweepDir)


    
