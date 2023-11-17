# Generates a commands file for SLURM

import sys

f = open(f"commands.run", "w")

outputFolder = "results/exp2"
domain = "gridscenario"
widths = [30, 100, 300, 1000]
thresholds = [0.15, 0.3, 0.45, 0.6]
aspects = [1, 500]
ks = [2, 3, 5]

# tiles
if domain == "tiles":
    costs = ["unit", "inv", "heavy"]

    for instance in range(1, 101):
        for cost in costs:
            '''
            # Bead search
            for width in widths:
                f.write(f"../tiles/15md_solver bead -width {width} -cost {cost} -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_bead_width{width}\n")
            
            # Threshold bead search
            for threshold in thresholds:
                f.write(f"../tiles/15md_solver thresholdbead -threshold {threshold} -cost {cost} -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_thresholdbead_threshold{threshold}\n")
            '''

            # Rectangle search
            for aspect in aspects:
                f.write(f"../tiles/15md_solver rectangle -aspect {aspect} -cost {cost} -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_rectangle_aspect{aspect}\n")
            
            # Outstanding search
            for k in ks:
                f.write(f"../tiles/15md_solver outstanding -k {k} -cost {cost} -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_outstanding_k{k}\n")

            # Outstanding rectangle search
            f.write(f"../tiles/15md_solver outstandingrect -cost {cost} -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./{outputFolder}/{domain}/{domain}_{instance}_{cost}_outstandingrect\n")
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