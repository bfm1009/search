# Generates a commands file for SLURM

import sys

f = open(f"commands.run", "w")

memGB = 7.5
time = 300
nInsts = 100
outputFolder = "results/exp3"
domains = [
    ("tiles", ["unit", "inv", "heavy"], "../tiles/15md_solver", "korf100"),
    ("vacuum", ["unit", "heavy"], "../vacuum/vacuum_solver", "vacuum-200-200-10"),
    ("pancake", ["unit", "heavy"], "../pancake/70pancake_solver", "70pancake"),
    ("orz100d", ["unit"], "../gridnav/scenario_solver", "orz100d"),
    ("64room", ["unit"], "../gridnav/scenario_solver", "64room")
]
algs = [
    ("bead", "width", [30, 100, 300, 1000]),
    ("thresholdbead", "threshold", [30, 100, 150]),
    ("rectangle", "aspect", [1, 500]),
    ("outstandingrect", "aspect", [1, 500]),
    ("outstanding", "k", [20, 200, 2000])
]

for domain, costs, solver, instancesDir in domains:
    for instance in range(1, nInsts + 1):
        for cost in costs:
            for alg, arg, argvals in algs:
                for argval in argvals:
                    if domain == "orz100d" or domain == "64room":
                        inst = f"-maproot instances/{domain}/ -entry {instance} < instances/{domain}/{domain}.map.scen"
                    else:
                        inst = f"< instances/{instancesDir}/{instance}"
                    
                    f.write(f"{solver} {alg} -{arg} {argval} -cost {cost} -mem {memGB}G -walltime {time} {inst} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_{alg}_{arg}{argval}\n")

f.close()