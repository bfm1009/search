# Generates a commands file for SLURM

import sys

f = open(f"commands.run", "w")

instances = range(1, 101)
aspects = [1]
ks = [2, 5]

for instance in instances:
    for aspect in aspects:
        f.write(f"../tiles/15md_solver rectangle -aspect {aspect} -cost heavy -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./results/{instance}_rectangle_aspect{aspect}\n")
    for k in ks:
        f.write(f"../tiles/15md_solver outstanding -k {k} -cost heavy -mem 7.5G -walltime 300 < /home/aifs2/group/data/tiles_instances/korf/4/4/{instance} > ./results/{instance}_outstanding_k{k}\n")

f.close()