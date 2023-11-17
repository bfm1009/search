# Generates a commands file for SLURM

import sys

f = open(f"commands.run", "w")

outputFolder = "results/exp2"
domain = "vacuum"
widths = [30, 100, 300, 1000]
thresholds = [0.15, 0.3, 0.45, 0.6]
aspects = [1, 500]
ks = [2, 3, 5]

# tiles or vacuum
if domain == "tiles" or domain == "vacuum":
    costs = ["unit", "inv", "heavy"] if domain == "tiles" else ["unit", "heavy"]
    solver = "../tiles/15md_solver" if domain == "tiles" else "../vacuum/vacuum_solver"
    instancesDir = "korf100" if domain == "tiles" else "vacuum-200-200-10"

    for instance in range(1, 101):
        for cost in costs:
            '''
            # Bead search
            for width in widths:
                f.write(f"{solver} bead -width {width} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_bead_width{width}\n")
            
            # Threshold bead search
            for threshold in thresholds:
                f.write(f"{solver} thresholdbead -threshold {threshold} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_thresholdbead_threshold{threshold}\n")
            '''

            # Rectangle search
            for aspect in aspects:
                f.write(f"{solver} rectangle -aspect {aspect} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_rectangle_aspect{aspect}\n")
            
            # Outstanding search
            for k in ks:
                f.write(f"{solver} outstanding -k {k} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_outstanding_k{k}\n")

            # Outstanding rectangle search
            f.write(f"{solver} outstandingrect -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_outstandingrect\n")
# gridscenario
elif domain == "gridscenario":
    cost = "unit"
    instanceTypes = ["orz100d", "64room"]

    for instanceType in instanceTypes:
        for instance in range(1, 101):
            # Rectangle search
            for aspect in aspects:
                f.write(f"../gridnav/scenario_solver rectangle -aspect {aspect} -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{instanceType}/{instanceType}_{instance}_{cost}_rectangle_aspect{aspect}\n")

            # Outstanding search
            for k in ks:
                f.write(f"../gridnav/scenario_solver outstanding -k {k} -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{instanceType}/{instanceType}_{instance}_{cost}_outstanding_k{k}\n")

            # Outstanding rectangle search
            f.write(f"../gridnav/scenario_solver outstandingrect -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{instanceType}/{instanceType}_{instance}_{cost}_outstandingrect\n")

f.close()