import sys
import utils
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def plot(domain, cst, algs, algStyles, nInst=100, startInst=1):

    # Grabs the data from many output files for all algorithms in algs list.
    data = utils.read_data("results/exp3", domain, cst, algs, True, 1, nInst, True)

    # Grabs specific data from the results loaded in.
    # Change these to plot different data.
    # Don't forget to change axis labels, too!
    xdata = data.wall_times
    ydata = data.costs
    xlabel = "wall time"
    ylabel = "solution cost"

    algXdata = defaultdict(list)
    algYdata = defaultdict(list)
    for alg, arg, argvals, dups, *extra in algs:
        color = algStyles[alg][0]
        linestyle = algStyles[alg][1]
        extra = tuple(extra)
        algkey = (alg, dups, extra)
        for argval in argvals:
            key = (alg,argval,dups,extra)

            # Grabs data to be plotted and averages across all instances.
            xList = xdata[key]
            yList = ydata[key]

            # Do not plot this argval if didn't solve all instances
            nosol = []
            for i in range(len(yList)):
                y = yList[i]
                if y <= 0:
                    nosol.append(i + 1)
            if len(nosol) > 0:
                print(f"{alg}-{argval} failed to find solution on instances {nosol}")
            else:
                algXdata[algkey] += [sum(xList)/len(xList)]
                algYdata[algkey] += [sum(yList)/len(yList)]

        # Plot a line for current algorithm.
        plt.plot(algXdata[algkey], algYdata[algkey], label=alg, color=color, linestyle=linestyle)
        
        # Add marks at each data point for the current algorithm.
        plt.scatter(algXdata[algkey], algYdata[algkey], color=color)

        # Label each point with its argval if this algorithm takes an argument
        #for i, argval in enumerate(argvals):
        #    plt.annotate(argval, (algXdata[algkey][i], algYdata[algkey][i]))

    plt.title(f"{domain} ({cst})")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.legend()
    plt.savefig(f"plots/{domain}-{cst}.pdf", bbox_inches = "tight", pad_inches = 0)


if __name__ == "__main__":
    domain = sys.argv[1]
    cst = sys.argv[2]
    
    startInst = 1

    nInst = 100 #utils.domain_instances[domain]
    widths = [30, 100, 300, 1000]
    aspects = [1, 500]
    thresholds = [2, 4, 6] #[30, 100, 150]
    ks = [2, 20, 200, 2000]

    # List of algorithms and their parameters.
    algs = [
        ("bead", "width", widths, True),
        ("thresholdbead", "threshold", thresholds, True),
        ("rectangle", "aspect", aspects, True),
        ("outstanding", "k", ks, True),
        ("outstandingrect", "aspect", aspects, True)
    ]

    # Dictionary of algorithms to their line color/styles.
    cmap = plt.get_cmap("tab20c")

    algStyles = {
        "rectangle": [cmap(0), "--"],
        "outstanding": [cmap(4), ":"],
        "outstandingrect": [cmap(8), (0, (3, 1, 1, 1))],
        "bead": [cmap(12), "-"],
        "thresholdbead": [cmap(16), "-."]
    }

    # Plots for each algorithm.
    plot(domain, cst, algs, algStyles, nInst=nInst, startInst=startInst)
