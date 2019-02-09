import argparse

def forksByNumberOfMiners():
    miners = range(1, 1000, 50)
    lbps = range(1, 200, 5)
    trials = 3
    rounds = 500

    output="../output/forks-by-minersNum"
    

if __name__ == "__main__":
    forksByNumberOfMiners()
