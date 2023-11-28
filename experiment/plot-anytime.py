#!/usr/bin/python3

import subprocess
import sys
from os import mkdir
import os.path
from math import log
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
from pylatex import Document, Figure, SubFigure, Package
import scipy.stats as stat
from statistics import median
from matplotlib import lines
import copy

import utils
#import plot_configs

import warnings
warnings.filterwarnings("ignore", message="Attempted to set non-positive left xlim on a log-scaled axis.\nInvalid limit will be ignored.")
warnings.filterwarnings("ignore", message="Attempting to set identical bottom == top == 0 results in singular transformations; automatically expanding.")
warnings.filterwarnings("ignore", message="The PostScript backend does not support transparency; partially transparent artists will be rendered opaque.")
warnings.filterwarnings("ignore")

def makeSection(resultsFolder, doc, domain, dataset, cost, algs, dup, save, nInst=100, beams=False):
    
    data = utils.read_data(resultsFolder, dataset, cost, algs, dup, 1, nInst)
    costs = data.costs
    times = data.cpu_times
    sol_lengths = data.sol_lengths
    expanded = data.expanded
    num_sols = data.num_sols
    common = data.common
    mem_fails = data.mem_fails
    deadend_fails = data.deadend_fails
    sol_lengths = data.sol_lengths
    incumbent_sols = data.incumbent_sols
    
    path = "plots/"+dataset
    try:
        if save:
            mkdir(path)
    except:
        pass

    dash_list = [x for x in lines.lineStyles.keys()][:4]*10
    dash_list[0], dash_list[1] = dash_list[1], dash_list[0]
    
    plotWidth = "1.75in"

    cmap = plt.get_cmap("tab20c") #plt.get_cmap("tab20")

    algColors = {}
    algDashes = {}
    algOffset = 0
    argvalOffset = 0
    for alg, arg, argvals, dups, *extra in algs:
        extra = tuple(extra)
        for argval in argvals:
            key = (alg,argval,dups,extra)
            if alg == "arastar" and arg == "-wsched":
                algColors[key] = cmap(6)
                algDashes[key] = dash_list[6]
            elif alg == "arastar" and argval == "2.5":
                algColors[key] = cmap(7)
                algDashes[key] = dash_list[7]
            elif alg == "arastar" and argval == "10":
                algColors[key] = cmap(12)
                algDashes[key] = dash_list[12]
            elif alg == "rectangle" and argval == "1":
                algColors[key] = cmap(4)
                algDashes[key] = dash_list[4]
            elif alg == "rectangle" and argval == "500":
                algColors[key] = cmap(5)
                algDashes[key] = dash_list[5]
            elif alg == "cab":
                algColors[key] = cmap(8)
                algDashes[key] = dash_list[8]
            elif alg == "aees":
                algColors[key] = cmap(0)
                algDashes[key] = dash_list[0]
            else:
                algColors[key] = cmap(algOffset + argvalOffset)
                algDashes[key] = dash_list[1 if argvalOffset == 0 else 0 if argvalOffset == 1 else argvalOffset]
                argvalOffset += 1
        algOffset += 4
        argvalOffset = 0
    
    time_data = get_all_sol_times(incumbent_sols)

    min_time = time_data[0]
        
    time_data = [min_time]+[x for x in time_data[:-1] if x >= min_time]
    
    algQualities = defaultdict(list)
    algDots = defaultdict(tuple)
    algCoverages = defaultdict(list)
    inst_solved = defaultdict(list)

    if domain in utils.unit_sols and cost == "unit":
        best_sols = utils.unit_sols[domain]
    elif dataset in utils.unit_sols and cost == "unit":
        best_sols = utils.unit_sols[dataset]
    else:
        best_sols = get_best_sols(incumbent_sols)
    
    with doc.create(Figure(position="h!")) as fig:

        dupString = ["dup dropping", "dup reopening"][dup]
        fig.add_caption(get_domain_label(dataset, cost))


        anytime_algs = algs
        
        beam_algs = algs


        
        algCosts = defaultdict(list)
        algQualities = defaultdict(list)
        algDots = defaultdict(tuple)
        count = 0
        line_list = []
        sortvals = []


        ## Average solution quality over time (anytime)
        algs = anytime_algs
        
        print("anytime alg quality")

        nAlgs = len(algs)
        
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            algkey = (alg, dups, extra)

            for argval in argvals:
                key = (alg,argval,dups,extra)

                temp_incumbents = copy.deepcopy(incumbent_sols[key])
                for i in range(nInst):
                    temp_incumbents[i].reverse()

                algQualities[key].append(0)
                algCoverages[key].append(0)
                
                for time in time_data[1:]:
                    cost_pcts = []
                    coverage = 0
                    for i in range(nInst):
                        sols = temp_incumbents[i]

                        next_sol = None
                        while len(sols) > 0 and sols[-1].wall_time <= time:
                            next_sol = sols.pop()
                        if next_sol != None and next_sol.cost > 0:
                            cost_pcts.append(sol_quality(next_sol.cost, best_sols[i]))
                            sols.append(next_sol)
                            coverage += 1
                        else:
                            cost_pcts.append(0)

                    algQualities[key].append(sum(cost_pcts) / float(nInst))
                    algQualities[key].append(sum(cost_pcts) / float(nInst))
                    
                    algCoverages[key].append(coverage)
                    algCoverages[key].append(coverage)

                    if key not in algDots and coverage == nInst:
                        algDots[key] = (time, sum(cost_pcts) / float(nInst))
                        

                sv = algQualities[key][-1]
                sortvals.append(sv)
                color = algColors[key]
                label = get_label(alg, argval, extra, dataset, cost)
            
                l, = plt.plot(sorted(time_data[1:]+time_data[:-1]), algQualities[key][:-1], algDashes[key], label=label, zorder=count, alpha=0.75, color=color)
                line_list.append(l)
                if key in algDots:
                    plt.scatter(algDots[key][0], algDots[key][1], color=color)
                count += 1

        plt.xlabel("Time (seconds)", fontsize = 14)
        plt.ylabel("Average quality", fontsize = 14)
        #plt.title("Average solution quality over time "+"("+dataset+", "+cost+")\n across "+str(nInst)+" instances", fontsize = 14)
        if domain == "100pancake" and cost == "heavy":
            leg = plt.legend(handles=utils.sort_lines(line_list, sortvals))
        #leg.set_title(get_domain_label(dataset, cost), prop={"weight":"bold"})
        #plt.xlim(0, time_max)
        plt.xscale("log")
        #plt.yscale("log")
        if save:
            plt.savefig(path+"/anytime-quality-"+cost+".pdf", bbox_inches='tight',pad_inches = 0.01)
        fig.add_plot(width=plotWidth)
        plt.clf()



        
        ## Coverage for all anytime algorithms
        print("anytime alg coverage")
        
        count = 0
        line_list = []
        sortvals = []
        
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            algkey = (alg, dups, extra)

            for argval in argvals:
                key = (alg,argval,dups,extra)
                
                sv = algCoverages[key][-1]
                sortvals.append(sv)
                color = algColors[key]
                label = get_label(alg, argval, extra, dataset, cost)

                l, = plt.plot(sorted(time_data[1:]+time_data[:-1]), algCoverages[key][:-1], algDashes[key], label=label, zorder=count, alpha=0.75, color=color)
                line_list.append(l)
                count += 1
    
        plt.xlabel("Time (seconds)", fontsize = 14)
        plt.ylabel("Number of instances solved", fontsize = 14)
        #plt.title("Number of instances solved over time "+"("+dataset+", "+cost+")\n across "+str(nInst)+" instances", fontsize = 14)
        #leg = plt.legend(handles=utils.sort_lines(line_list, sortvals))
        #leg.set_title(get_domain_label(dataset, cost), prop={"weight":"bold"})
        #plt.xlim(0, time_max)
        plt.xscale("log")
        #plt.yscale("log")
        if save:
            plt.savefig(path+"/anytime-coverage-"+cost+".pdf", bbox_inches='tight',pad_inches = 0.01)
        fig.add_plot(width=plotWidth)
        plt.clf()


        
        
        ## Solution cost across only instances solved by all algorithms
        print("anytime alg costs")

        algs = anytime_algs

        noARA = []
        only10ARA = []

        

        #nolog = ["50pancake", "70pancake", "100pancake"]

        exclude = {}
        exclude_pct = 0.2
        
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            for argval in argvals:
                key = (alg,argval,dups,extra)

                exclude[key] = True
                inst_count = 0
                for i in range(nInst):
                    if len(incumbent_sols[key][i]) > 0 and incumbent_sols[key][i][0].cost > 0:
                        inst_count += 1

                if inst_count > (nInst * exclude_pct):
                    exclude[key] = False
                else:
                    print("excluding", key)
                    

        # calculate whether an instance was solved by all at a given time
        all_incumbents = copy.deepcopy(incumbent_sols)
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)

            for argval in argvals:
                key = (alg,argval,dups,extra)

                if exclude[key]:
                    continue

                temp_incumbents = all_incumbents[key]

                for i in range(nInst):
                    temp_incumbents[i].reverse()

        
        allSolved = defaultdict(bool)

        for time in time_data[1:]:
            for i in range(nInst):
                timeKey = (time, i)
                allSolved[timeKey] = True
                for alg, arg, argvals, dups, *extra in algs:
                    extra = tuple(extra)

                    for argval in argvals:
                        key = (alg,argval,dups,extra)

                        if exclude[key]:
                            continue

                        temp_incumbents = all_incumbents[key]
                        sols = temp_incumbents[i]

                        next_sol = None
                        while len(sols) > 0 and sols[-1].wall_time <= time:
                            next_sol = sols.pop()
                        if next_sol != None and next_sol.cost > 0:
                            sols.append(next_sol)
                        else:
                            allSolved[timeKey] = False
    
        count = 0
        line_list = []
        sortvals = []

        temp_time_data = copy.deepcopy(time_data[1:])

        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            algkey = (alg, dups, extra)

            for argval in argvals:
                key = (alg,argval,dups,extra)

                if exclude[key]:
                    continue

                temp_incumbents = copy.deepcopy(incumbent_sols[key])
                for i in range(nInst):
                    temp_incumbents[i].reverse()
                
                for time in time_data[1:]:
                    costs = []
                    solvedInsts = 0
                    for i in range(nInst):
                        sols = temp_incumbents[i]

                        timeKey = (time, i)

                        if not allSolved[timeKey]:
                            continue

                        solvedInsts += 1
                        
                        next_sol = None
                        while len(sols) > 0 and sols[-1].wall_time <= time:
                            next_sol = sols.pop()
                        if next_sol != None and next_sol.cost > 0:
                            costs.append(next_sol.cost)
                            sols.append(next_sol)
                            coverage += 1

                    if solvedInsts > 0:
                        costAvg = sum(costs) / float(solvedInsts)
                        algCosts[key].append(costAvg)
                        algCosts[key].append(costAvg)
                    elif time in temp_time_data:
                        temp_time_data.remove(time)
                        
                try:
                    sv = algCosts[key][-1]
                    sortvals.append(sv)
                except:
                    print(key)
                color = algColors[key]
                label = get_label(alg, argval, extra, dataset, cost)

                l, = plt.plot(sorted(temp_time_data+temp_time_data[:-1]), algCosts[key][:-1], algDashes[key], label=label, zorder=count, alpha=0.75, color=color)
                line_list.append(l)
                count += 1
    
        plt.xlabel("Time (seconds)", fontsize = 14)
        #plt.xlim(left=time_data[0])
        if False in exclude.values():
            key = [x for x in exclude.keys() if not exclude[x]][0]
            plt.scatter(time_data[0], algCosts[key][0], alpha=0.0)
        else:
            print("No algorithms solved any instances.")
        for key, value in exclude.items():
            if value == True:
                color = algColors[key]
                alg,argval,dups,extra = key[0], key[1], key[2], key[3]
                label = get_label(alg, argval, extra, dataset, cost)
                l, = plt.plot([], [], algDashes[key], label=label, zorder=count, alpha=0.75, color=color)
                line_list.append(l)
                count += 1
        #if not dataset in nolog:
        #    plt.ylabel("Solution cost (log)", fontsize = 14)
        #    plt.yscale("log")
        #else:
        plt.ylabel("Solution cost", fontsize = 14)
        #plt.title("Avg sol cost for insts solved by all "+"("+dataset+", "+cost+")\n across "+str(nInst)+" instances", fontsize = 14)
        leg = plt.legend()#handles=utils.sort_lines(line_list, sortvals))
        leg.set_title(get_domain_label(dataset, cost), prop={"weight":"bold"})
        #plt.xlim(0, time_max)
        plt.xscale("log")
        if save:
            plt.savefig(path+"/anytime-solved_cost-"+cost+".pdf", bbox_inches='tight',pad_inches = 0.01)
        fig.add_plot(width=plotWidth)
        plt.clf()


        line_list = []
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            algkey = (alg, dups, extra)

            for argval in argvals:
                key = (alg,argval,dups,extra)
                color = algColors[key]
                label = get_label(alg, argval, extra, dataset, cost)
                l, = plt.plot([], [], algDashes[key], label=label, alpha=0.75, color=color)
                line_list.append(l)
        leg = plt.legend()
        #leg.set_title(get_domain_label(dataset, cost), prop={"weight":"bold"})
        legfig = leg.figure
        legfig.canvas.draw()
        bbox = leg.get_window_extent().transformed(legfig.dpi_scale_trans.inverted())
        if save:
            legfig.savefig(path+"/"+cost+"-legend.pdf", dpi="figure", bbox_inches=bbox)

        plt.clf()

                
        
        # stop the function before beam plots when not needed
        if not beams:
            return
    
        ## Average solution quality over time (beam)
        algs = beam_algs

        print("beam algs")

        algQualities = defaultdict(list)
        algDots = defaultdict(tuple)
        count = 0
        line_list = []
        sortvals = []
        
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            algkey = (alg, dups, extra)

            for argval in argvals:
                key = (alg,argval,dups,extra)

                temp_incumbents = copy.deepcopy(incumbent_sols[key])
                for i in range(nInst):
                    temp_incumbents[i].reverse()

                algQualities[key].append(0)
                
                for time in time_data[1:]:
                    cost_pcts = []
                    solved_all = True
                    for i in range(nInst):
                        sols = temp_incumbents[i]

                        next_sol = None
                        while len(sols) > 0 and sols[-1].wall_time <= time:
                            next_sol = sols.pop()
                        if next_sol != None and next_sol.cost > 0:
                            cost_pcts.append(sol_quality(next_sol.cost, best_sols[i]))
                            sols.append(next_sol)
                        else:
                            cost_pcts.append(0)
                            solved_all = False

                    algQualities[key].append(sum(cost_pcts) / float(nInst))
                    algQualities[key].append(sum(cost_pcts) / float(nInst))

                    if key not in algDots and solved_all:
                        algDots[key] = (time, sum(cost_pcts) / float(nInst))
                        

                sv = algQualities[key][-1]
                sortvals.append(sv)
                color = algColors[key]
                label = get_label(alg, argval, extra, dataset, cost)
            
                l, = plt.plot(sorted(time_data[1:]+time_data[:-1]), algQualities[key][:-1], algDashes[key], label=label, zorder=count, alpha=0.75, color=color)
                line_list.append(l)
                if key in algDots:
                    plt.scatter(algDots[key][0], algDots[key][1], color=color)
                count += 1
    
        plt.xlabel("Time (seconds)", fontsize = 14)
        plt.ylabel("Average quality", fontsize = 14)
        #plt.title("Average solution quality over time "+"("+dataset+", "+cost+")\n across "+str(nInst)+" instances", fontsize = 14)
        leg = plt.legend(handles=utils.sort_lines(line_list, sortvals))
        leg.set_title(get_domain_label(dataset, cost), prop={"weight":"bold"})
        #plt.xlim(0, time_max)
        plt.xscale("log")
        #plt.yscale("log")
        if save:
            plt.savefig(path+"/triangle-beam-quality-"+cost+".pdf", bbox_inches='tight',pad_inches = 0.01)
        fig.add_plot(width=plotWidth)
        plt.clf()


def get_domain_label(dataset, cost):
    d = dataset
    if dataset == "tiles":
        d = "15 puzzle"
    elif dataset == "24tiles":
        d = "24 puzzle"
    elif dataset  ==  "20bw":
        return "20 blocks"
    elif dataset == "20bwdp":
        return "20 blocks (deep)"
    elif dataset == "vacuum":
        d = "vacuum 200x200 10"
    elif dataset == "vacuum-large":
        d = "vacuum 500x500 20"
    elif dataset == "vacuum-larger":
        d = "vacuum 500x500 60"

    return d + " (" + cost + ")"
        

def get_best_sols(incumbent_sols):
    lst = []
    
    for i in range(nInst):
        lst.append(0)
        for v in incumbent_sols.values():
            if len(v[i]) > 0 and v[i][-1].cost != 0:
                if lst[-1] == 0:
                    lst[-1] = v[i][-1].cost
                else:
                    lst[-1] = min(lst[-1], v[i][-1].cost)
    
    return lst

def get_all_sol_times(incumbent_sols):
    lst = []
    
    for v in incumbent_sols.values():
        for i in range(nInst):
            for incumbent in v[i]:
                lst.append(incumbent.wall_time)

    lst = list(set(lst))
    lst = sorted(lst)
    return lst
        
def get_label(alg, argval, extra, dataset, cost):
    argval = str(argval)
    if alg in ["beam", "beam-h", "bead"]:
        if cost == "unit":
            label = "bead"+"-"+argval
        else:
            label = alg+"-"+argval
    elif alg in ["arastar"] and argval != "":
        label = "ARA*"+"(w="+argval+",Δ="+str(extra[1])+")"
    elif alg == "arastar" and argval == "":
        label = "ARA*"+"(w={5,3,2,1.5,1})"
    elif alg == "triangle" and argval != "":
        label = alg+"("+argval+")"
    elif alg in ["thresholdbead", "rectangle", "outstanding", "outstandingrect"]:
        label = alg+"-"+argval
    elif alg == "cab":
        label = "CABS"
    elif alg == "aees":
        label = "AEES"
    else:
        label = alg

    return label


def sol_quality(sol_cost, best_cost):
    if sol_cost == 0 or best_cost == 0:
        return 0
    else:
        return best_cost / sol_cost

if __name__ == "__main__":

    save = False
    resultsFolder = ""
    if len(sys.argv) - 1 < 1:
        print("usage: python3 plot-anytime.py [resultsFolder] <-save>")
        exit()
    else:
        resultsFolder = sys.argv[1]
        if "-save" in sys.argv:
            save = True
    
    doc = Document('plots')

    doc.packages.append(Package("fullpage"))
    
    try:
        if save: 
            mkdir("plots")
    except:
        pass

    # ALL DOMAINS
    """
    domains = [
        ("tiles", "tiles"),
        ("24tiles", "24tiles"),
        ("50pancake", "50pancake"),
        ("70pancake", "70pancake"),
        ("100pancake", "100pancake"),
        ("20bwdp", "20bwdp"),
        ("20bw", "20bw"),
        ("vacuum", "vacuum"),
        ("vacuum-large", "vacuum-large"),
        ("vacuum-larger", "vacuum-larger"),
        ("plat2d", "plat2d"),
        ("traffic", "traffic"),
        ("gridscenario", "64room"),
        ("gridscenario", "orz100d"),
        ("gridnav", "gridnav")
    ]
    """


    # GRIDS ONLY
    """
    domains = [
        ("gridscenario", "64room"),
        ("gridscenario", "orz100d"),
        ("gridnav", "gridnav")
    ]
    """

    domains = [
        #("tiles", "tiles"),
        ("gridscenario", "64room"),
        ("gridscenario", "orz100d"),
        #("vacuum", "vacuum"),
        #("pancake", "pancake")
    ]
    costs_dict = {
        "tiles": ["unit", "inv", "heavy"],
        "gridscenario": ["unit"],
        "vacuum": ["unit", "heavy"],
        "pancake": ["unit", "heavy"]
    }

    #slopes = ["500"]
    #aspects = ["1", "100", "200", "500"]
    widths = [30, 100, 300, 1000]
    thresholds = [2, 4, 6]
    aspects = [1, 500]
    ks = [2, 4, 6]
    algs = [
        #("bead", "width", widths, True),
        #("thresholdbead", "threshold", thresholds, True),
        ("rectangle", "aspect", aspects, True),
        ("outstanding", "k", ks, True),
        ("outstandingrect", "aspect", aspects, True)
    ]

    '''alg_dict = {
        ("tiles", "unit"): algs,
        ("tiles", "inv"): algs,
        ("tiles", "heavy"): algs,
        ("64room", "unit"): algs,
        ("orz100d", "unit"): algs,
        ("vacuum", "unit"): algs,
        ("vacuum", "heavy"): algs
    }'''


    #alg_dict = plot_configs.alg_dict_depth_firsts
    #alg_dict = plot_configs.alg_dict_all

    
    # FOR USE WHEN COMPARING RECTANGLE PARAMS
    #alg_dict = {key: [("rectangle","-aspect",aspects,True)] for key in alg_dict.keys()}


    for domain, dataset in domains:
        #widths = utils.domain_widths[domain][3:]
        costs = costs_dict[domain] #utils.costs[domain]
        nInst = 100 #utils.domain_instances[domain]
        print(dataset)

        for cost in costs:

            algs_reopen = algs#alg_dict[(dataset, cost)]
            
            print(dataset + " " + cost + " (dup reopening)")

            makeSection(resultsFolder, doc, domain, dataset, cost, algs_reopen, True, save, nInst)
            
    doc.generate_pdf('plots/plots-anytime', clean_tex=True)



    
