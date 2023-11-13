#!/bin/sh
#SBATCH --job-name=search                    # Job name
#SBATCH --mail-type=END                      # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=bryan.mckenney@unh.edu   # Where to send mail	                          
#SBATCH --ntasks=1                           # Run 1 task per node
#SBATCH --array=1-1800                        # Array range
#SBATCH --no-kill
#SBATCH -p compute
#SBATCH -o ./slurmOutput/%a.out
eval "$(head -${SLURM_ARRAY_TASK_ID} ./commands.run | tail -1)"