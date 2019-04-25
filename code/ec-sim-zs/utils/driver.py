# system utils
import argparse
import subprocess
import datetime
import time
import os
from os import listdir
from os.path import isfile, join
import sys

# simulation output parser 
import blocktree

# plotting
import matplotlib
# use different backend ahead of importing pyplot for running remotely
matplotlib.use('Agg')
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
    params += " -quiet"
    params += " -output={}".format(output)

    return params

def sweepByMinersAndLBP(miners, lbps, trials, rounds, sweepDir):
    data = dict()
    for lbp in lbps:
        lbpDir = sweepDir + "/lbp-" + str(lbp)
        data[lbp] = dict()
        for m in miners:
            data[lbp][m] = []
            outputDir = lbpDir + "/miner-" + str(m)
            command = "{command}{params}".format(command=PROGRAM, params=buildArgs(m,lbp,trials,rounds, outputDir))     
            print "\ntime is {time}".format(time=datetime.datetime.now())
            print command
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            out, err = p.communicate()
            print "output was {output}\n-*-*-*\nerr was {error}".format(output=out, error=err)

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
                print "Currently on {cFile}".format(cFile=f)
                tree = blocktree.BlockTree(f)
                print "Done building blocktree"
                print "\ntime is {time}".format(time=datetime.datetime.now())
                for metric in metrics:
                    if metric == "AvgHeadsPerRound":
                        data[lbp][m][metric].append(tree.AvgHeadsPerRound())
                        print "average heads per round was {avg}".format(avg= Tree.AvgHeadsPerRound())
                    if metric == "NumReorgs":
                        data[lbp][m][metric].append(tree.NumReorgs())
                        print "num reorgs was {reorgs}".format(reorgs=tree.NumReorgs())
    return data

# plotMetricSweep plots the mean value of a metric varying over the number of miners
# mining on the chain.  It plots multiple series, one for each lbp value in the
# sweep.
def plotMetricSweep(data, metric, sweepDir):
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
    fig1 = plt.gcf()
    fig1.savefig("{name}-{time}.png".format(name=sweepDir,time=milliTS()), format="png")
    plt.show()
        
                
# plot value of chain metrics through a sweep of miner number and lookback
# parameters.  metrics is a list of strings, each corresponding to a metric
# identifier.
def plotSweep(miners, lbps, metrics, sweepDir):
    # Gather data from sweep output artifacts.
    data = readSweepData(miners, lbps, metrics, sweepDir)

    # Plot data for each metric
    for metric in metrics:
        plotMetricSweep(data, metric, sweepDir)
                
def milliTS():
    return int(round(time.time() * 1000))

if __name__ == "__main__":
    # TODO -- should use argparse to set values of these slices or read from config file
    miners = [10, 50, 100, 200, 400]
    lbps = [1, 10, 20, 50, 100]
    trials = 3
    rounds = 500
    sweepDir = "/output/sweep-f"
    # sweepDir = "/home/snarky/space/ec-sim/output/sweep-f"


    # TODO -- shoulduse argparse to express which operations should be done:
    #   run simulation and output (sweepByMinersAndLBP), plot existing data 
    #   (plotMetricSweep), or load and print data (printing of data doesn't
    #   exist yet but is easy to do alongside readSweepData)

    # right now I simply comment things out and rewrite vals in this function,
    # which might be good enough for a while.

    
    print("""runs can take a while and scale quadratically in number of rounds and exponentially in number of miners. E.g.
    100 rounds, 50 miners  ===> 2.5s
    100 rounds, 200 miners ===> 45s
    100 rounds, 400 miners ===> 5m13s

    200 rounds, 50 miners  ===> 4.8s
    200 rounds, 200 miners ===> 1m52s
    200 rounds, 400 miners ===> 12m44s

    400 rounds, 50 miners  ===> 13s
    400 rounds, 200 miners ===> 6m51s
    400 rounds, 400 miners ===> 40m"""
    )

    # sweepByMinersAndLBP(miners, lbps, trials, rounds, sweepDir)
    readSweepData(miners, lbps, ["NumReorgs"], sweepDir)
    plotSweep(miners, lbps, ["NumReorgs"], sweepDir)
