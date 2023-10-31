import sys
import utils
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def plot(domain, cst, algs, nInst=100, startInst=1):

    # Grabs the data from many output files for all algorithms in algs list.
    data = utils.read_data("results", domain, cst, algs, True, 1, nInst)

    # Grabs specific data from the results loaded in.
    # Change these to plot different data.
    # Don't forget to change axis labels, too!
    xdata = data.cpu_times
    ydata = data.costs
    xlabel = "CPU time"
    ylabel = "solution cost"

    algXdata = defaultdict(list)
    algYdata = defaultdict(list)
    for alg, arg, argvals, dups, *extra in algs:
        algValidData = []
        extra = tuple(extra)
        algkey = (alg, dups, extra)
        for argval in argvals:
            key = (alg,argval,dups,extra)

            # Grabs data to be plotted and averages across all instances.
            xList = xdata[key]
            yList = ydata[key]

            # Remove data points where no solution found
            nosol = []
            for i in range(len(yList)):
                y = yList[i]
                if y <= 0:
                    nosol.append(i)
            if len(nosol) > 0:
                xList = np.delete(xList, nosol)
                yList = np.delete(yList, nosol)
                print(f"Deleted {len(nosol)} bad data points for {alg}-{argval}")
            
            algValidData.append(len(xList))
            algXdata[algkey] += [sum(xList)/len(xList)]
            algYdata[algkey] += [sum(yList)/len(yList)]

        # Plot a line for current algorithm.
        plt.plot(algXdata[algkey], algYdata[algkey], label=alg)
        
        # Add marks at each data point for the current algorithm.
        plt.scatter(algXdata[algkey], algYdata[algkey])
        plt.scatter(algXdata[algkey], algYdata[algkey], marker='o', facecolors="none", edgecolors='r', s=[(1 - (n / nInst)) * 1000 for n in algValidData])
        plt.scatter(algXdata[algkey], algYdata[algkey], marker='o', facecolors="none", edgecolors='grey', s=[1000 if n < nInst else 0 for n in algValidData], linestyle="--")

        # Label each point with its argval if this algorithm takes an argument
        for i, argval in enumerate(argvals):
            plt.annotate(argval, (algXdata[algkey][i], algYdata[algkey][i]))

        plt.xscale("log")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
    plt.legend()
    plt.savefig("graph.png")


if __name__ == "__main__":
    domain = sys.argv[1]
    cst = sys.argv[2]
    
    startInst = 1

    nInst = utils.domain_instances[domain]
    widths = [30, 100, 300, 1000]
    thresholds = [0.15, 0.3, 0.45, 0.6]

    # List of algorithms and their parameters.
    algs = [("bead","width",widths,True),
            ("thresholdbead","threshold",thresholds,True)]

    # Plots for each algorithm.
    plot(domain, cst, algs, nInst=nInst, startInst=startInst)
