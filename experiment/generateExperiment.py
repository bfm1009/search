# Generates a commands file for SLURM

import sys

f = open(f"commands.run", "w")

outputFolder = "results/exp3"
domains = ["tiles", "vacuum", "gridscenario"]
widths = [30, 100, 300, 1000]
thresholds = [2, 4, 6]
aspects = [1, 500]
ks = [2, 4, 6]

for domain in domains:
    # tiles or vacuum
    if domain == "tiles" or domain == "vacuum":
        costs = ["unit", "inv", "heavy"] if domain == "tiles" else ["unit", "heavy"]
        solver = "../tiles/15md_solver" if domain == "tiles" else "../vacuum/vacuum_solver"
        instancesDir = "korf100" if domain == "tiles" else "vacuum-200-200-10"

        for instance in range(1, 101):
            for cost in costs:
                # Bead search
                for width in widths:
                    f.write(f"{solver} bead -width {width} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_bead_width{width}\n")
                
                # Threshold bead search
                for threshold in thresholds:
                    f.write(f"{solver} thresholdbead -threshold {threshold} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_thresholdbead_threshold{threshold}\n")

                for aspect in aspects:
                    # Rectangle search
                    f.write(f"{solver} rectangle -aspect {aspect} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_rectangle_aspect{aspect}\n")

                    # Outstanding rectangle search
                    f.write(f"{solver} outstandingrect -aspect {aspect} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_outstandingrect_aspect{aspect}\n")
                
                # Outstanding search
                for k in ks:
                    f.write(f"{solver} outstanding -k {k} -cost {cost} -mem 7.5G -walltime 300 < instances/{instancesDir}/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_outstanding_k{k}\n")
    # gridscenario
    elif domain == "gridscenario":
        cost = "unit"
        solver = "../gridnav/scenario_solver"
        instanceTypes = ["orz100d", "64room"]

        for instanceType in instanceTypes:
            for instance in range(1, 101):
                # Bead search
                for width in widths:
                    f.write(f"{solver} bead -width {width} -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_bead_width{width}\n")
                
                # Threshold bead search
                for threshold in thresholds:
                    f.write(f"{solver} thresholdbead -threshold {threshold} -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_thresholdbead_threshold{threshold}\n")
                
                for aspect in aspects:
                    # Rectangle search
                    f.write(f"{solver} rectangle -aspect {aspect} -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{instanceType}/{instanceType}_{instance}_{cost}_rectangle_aspect{aspect}\n")

                    # Outstanding rectangle search
                    f.write(f"{solver} outstandingrect -aspect {aspect} -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{instanceType}/{instanceType}_{instance}_{cost}_outstandingrect_aspect{aspect}\n")

                # Outstanding search
                for k in ks:
                    f.write(f"{solver} outstanding -k {k} -maproot instances/{instanceType}/ -entry {instance} -mem 7.5G -walltime 300 < instances/{instanceType}/{instanceType}.map.scen > ./{outputFolder}/{instanceType}/{instanceType}_{instance}_{cost}_outstanding_k{k}\n")

f.close()