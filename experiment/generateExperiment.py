# Generates a commands file for SLURM

import sys

f = open(f"commands.run", "w")

instances = range(1, 101)
widths = [30, 100, 300, 1000]
thresholds = [0.15, 0.3, 0.45, 0.6]
aspects = [1, 500]
ks = [2, 3, 5]

for instance in instances:
    for width in widths:
        f.write(f"../tiles/15md_solver bead -width {width} -cost heavy -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./results/{instance}_bead_width{width}\n")
    for threshold in thresholds:
        f.write(f"../tiles/15md_solver thresholdbead -threshold {threshold} -cost heavy -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./results/{instance}_thresholdbead_threshold{threshold}\n")
    #for aspect in aspects:
    #    f.write(f"../tiles/15md_solver rectangle -aspect {aspect} -cost heavy -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./results/{instance}_rectangle_aspect{aspect}\n")
    #for k in ks:
    #    f.write(f"../tiles/15md_solver outstanding -k {k} -cost heavy -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./results/{instance}_outstanding_k{k}\n")

f.close()