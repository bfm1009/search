import heapq
from collections import namedtuple, defaultdict
import traceback

weights = [100000, 100, 50, 20, 15, 10, 7, 5, 4, 3, 2.5, 2, 1.75, 1.5, 1.3, 1.2, 1.15, 1.1, 1.05,1.01, 1.001, 1.0005, 1]

costs = {"20bw": ["unit"],
         "20bwdp": ["unit"],
         "50bw": ["unit"],
         "50bwdp": ["unit"],
         "48tiles": ["unit"],#, "heavy", "sqrt", "reverse", "inverse", "revinv"],
         "24tiles": ["unit", "heavy", "sqrt", "reverse", "inverse", "revinv"],
         "tiles": ["unit", "heavy", "sqrt", "reverse", "inverse", "revinv"],
         "8tiles": ["unit", "heavy", "sqrt", "reverse", "inverse", "revinv"],
         "11tiles": ["unit", "heavy", "sqrt", "reverse", "inverse", "revinv"],
         "gridnav": ["Unit", "Life"],
         "gridscenario": ["octile"],
         "plat2d": ["unit"],
         "traffic": ["unit"],
         "vacuum-200-200-7": ["unit", "heavy"],
         "vacuum": ["unit", "heavy"],
         "vacuum-large": ["unit", "heavy"],
         "vacuum-larger": ["unit", "heavy"],
         "12pancake": ["unit", "heavy"],
         "20pancake": ["unit", "heavy"],
         "50pancake": ["unit", "heavy"],
         "70pancake": ["unit", "heavy"],
         "100pancake": ["unit", "heavy"],
         "synth_tree": ["unit"]}

exec_files = {"20bw": "20bw_solver",
              "20bwdp": "20bwdp_solver",
              "50bw": "50bw_solver",
              "50bwdp": "50bwdp_solver",
              "48tiles": "48md_solver",
              "24tiles": "24md_solver",
              "tiles": "15md_solver",
              "8tiles": "8md_solver",
              "11tiles": "11md_solver",
              "gridscenario": "scenario_solver",
              "gridnav": "gridnav_solver",
              "traffic": "traffic_solver",
              "plat2d": "plat2d_solver",
              "vacuum-200-200-7": "vacuum_solver",
              "vacuum": "vacuum_solver",
              "vacuum-large": "vacuum_solver",
              "vacuum-larger": "vacuum_solver",
              "12pancake": "12pancake_solver",
              "20pancake": "20pancake_solver",
              "50pancake": "50pancake_solver",
              "70pancake": "70pancake_solver",
              "100pancake": "100pancake_solver",
              "synth_tree": "synth_tree_solver"}

domain_dir = {"20bw": "blocksworld",
              "20bwdp": "blocksworld",
              "50bw": "blocksworld",
              "50bwdp": "blocksworld",
              "48tiles": "tiles",
              "24tiles": "tiles",
              "tiles": "tiles",
              "8tiles": "tiles",
              "11tiles": "tiles",
              "gridscenario": "gridnav",
              "gridnav": "gridnav",
              "traffic": "traffic",
              "plat2d": "plat2d",
              "vacuum-200-200-7": "vacuum",
              "vacuum": "vacuum",
              "vacuum-large": "vacuum",
              "vacuum-larger": "vacuum",
              "12pancake": "pancake",
              "20pancake": "pancake",
              "50pancake": "pancake",
              "70pancake": "pancake",
              "100pancake": "pancake",
              "synth_tree": "synth_tree"}


domain_instances = {"20bw": 100,
                    "20bwdp": 100,
                    "50bw": 100,
                    "50bwdp": 100,
                    "48tiles": 99,
                    "24tiles": 50,
                    "tiles": 100,
                    "8tiles": 100,
                    "11tiles": 10,
                    "gridscenario": 100,
                    "gridnav": 100,
                    "traffic": 25,
                    "plat2d": 100,
                    "vacuum-200-200-7": 10,
                    "vacuum": 100,
                    "vacuum-large": 100,
                    "vacuum-larger": 100,
                    "12pancake": 49,
                    "20pancake": 50,
                    "50pancake": 100,
                    "70pancake": 100,
                    "100pancake": 50,
                    "synth_tree": 100}

domain_widths = {"20bw": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "20bwdp": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "50bw": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "50bwdp": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "48tiles": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "24tiles": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "tiles": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "8tiles": [1000, 300, 100, 30, 10, 3],
                 "11tiles": [3000, 1000, 300, 100, 30, 10, 3],
                 "gridscenario": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "gridnav": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "traffic": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "plat2d": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "12pancake": [3000, 1000, 300, 100, 30, 10, 3],
                 "20pancake": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "50pancake": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "70pancake": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "100pancake": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "synth_tree": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "vacuum-larger": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "vacuum-large": [100000, 30000, 10000, 3000, 1000, 300, 100, 30],
                 "vacuum": [3000, 1000, 300, 100, 30, 10, 3],
                 "vacuum-200-200-7": [1000, 300, 100, 30, 10, 3]}

unit_sols = {"24tiles": [95, 96, 97,98, 100, 101, 104, 108, 113, 114, 106, 109, 101, 111, 103, 96, 109, 110, 106, 92, 103, 95, 104, 107, 81, 105, 99, 98, 88, 92, 99, 97, 106, 102, 98, 90, 100, 96, 104, 82, 106, 108, 104, 93, 101, 100, 92, 107, 100, 113],
             "tiles": [57, 55, 59, 56, 56, 52, 52, 50, 46, 59, 57, 45, 46, 59, 62, 42, 66, 55, 46, 52, 54, 59, 49, 54, 52, 58, 53, 52, 54, 47, 50, 59, 60, 52, 55, 52, 58, 53, 49, 54, 54, 42, 64, 50, 51, 49, 47, 49, 59, 53, 56, 56, 64, 56, 41, 55, 50, 51, 57, 66, 45, 57, 56, 51, 47, 61, 50, 51, 53, 52, 44, 56, 49, 56, 48, 57, 54, 53, 42, 57, 53, 62, 49, 55, 44, 45, 52, 65, 54, 50, 57, 57, 46, 53, 50, 49, 44, 54, 57, 54]}


try:
    from dataclasses import dataclass, field
    @dataclass
    class Solution:
        cost: float
        wall_time: float
        expanded: int
        generated: int
    @dataclass
    class Data:
        costs: defaultdict = field(default_factory=lambda: defaultdict(list))
        sol_lengths: defaultdict = field(default_factory=lambda: defaultdict(list))
        cpu_times: defaultdict = field(default_factory=lambda: defaultdict(list))
        wall_times: defaultdict = field(default_factory=lambda: defaultdict(list))
        expanded: defaultdict = field(default_factory=lambda: defaultdict(list))
        generated: defaultdict = field(default_factory=lambda: defaultdict(list))
        num_sols: defaultdict = field(default_factory=lambda: defaultdict(list))
        incumbent_sols: defaultdict = field(default_factory=lambda: defaultdict(list))
        mem_fails: defaultdict = field(default_factory=lambda: defaultdict(int))
        deadend_fails: defaultdict = field(default_factory=lambda: defaultdict(int))
        common: list = field(default_factory=list)
        init_h: list = field(default_factory=list)
        nInst: int = 100
except:
    class Solution:
        def __init__(self, cost, wall_time, expanded, generated):
            self.cost = cost
            self.wall_time = wall_time
            self.expanded = expanded
            self.generated = generated
    class Data:
        def __init__(self, nInst):
            self.costs = defaultdict(list)
            self.sol_lengths = defaultdict(list)
            self.cpu_times = defaultdict(list)
            self.wall_times = defaultdict(list)
            self.expanded = defaultdict(list)
            self.generated = defaultdict(list)
            self.num_sols = defaultdict(list)
            self.incumbent_sols = defaultdict(list)
            self.mem_fails = defaultdict(int)
            self.deadend_fails = defaultdict(int)
            self.common = []
            self.init_h = []
            self.nInst = 100
    
def read_data(results_dir, domain, cst, algs, dup, startInst=1, nInst=100, firstSol=False):
    data = Data(nInst=nInst)
    for i in range(startInst, startInst+nInst):
        file = str(i)
        fail = False
        init_h = None
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            dupString = ["-dropdups", ""][dups]
            if len(extra) == 0:
                extra_opt = ""
                extra_val = ""
            else:
                extra_opt = extra[0]
                extra_val = extra[1]
                
            for argval in argvals:
                
                if alg in ["monobead-n", "monobeam-n"] and len(extra)==0:
                    extra_opt = "-n"
                    extra_val = str(argval//2)
                    
                key = (alg, argval, dups, extra)
                underscore = "_" if arg != "" else ""
                filename = f"{results_dir}/{domain}/{domain}_{file}_{cst}_{alg}{underscore}{arg}{argval}" #results_dir+"/"+domain+"/"+str(file)+alg+dupString+arg+str(argval)+"-"+cst+extra_opt+extra_val
                infile = open(filename, "r")
                lines = infile.readlines()
                if init_h is None:
                    if len([x for x in lines if "initial heuristic" in x]) == 0:
                        #print("no initial h line in", filename)
                        pass
                    else:
                        init_h_line = [x for x in lines if "initial heuristic" in x][0]
                        init_h = float(init_h_line.split("\"")[3])
                if len([x for x in lines if "total nodes expanded" in x]) == 0:
                    print("no expansion line in file", filename)
                expanded_line = [x for x in lines if "total nodes expanded" in x][0]
                expanded = float(expanded_line.split("\"")[3])
                    
                generated_line = [x for x in lines if "total nodes generated" in x][0]
                generated = float(generated_line.split("\"")[3])
                time_line = [x for x in lines if "total raw cpu time" in x][0]
                cpu_time = float(time_line.split("\"")[3])
                wall_time_line = [x for x in lines if "total wall time" in x][0]
                wall_time = float(wall_time_line.split("\"")[3])
                try:
                    sol_lines = [x for x in lines if "incumbent" in x]
                    incumbent_sols = get_incumbent_sols(sol_lines)
                    num_sol = len(sol_lines)
                    cost_lines = [x for x in lines if "final sol cost" in x]
                    if firstSol and len(incumbent_sols) > 0: # first solution
                        cost = incumbent_sols[0].cost
                        wall_time = incumbent_sols[0].wall_time
                    elif len(cost_lines) > 0:
                        cost_line = cost_lines[0]
                        cost = float(cost_line.split("\"")[3])
                    elif len(incumbent_sols) > 0:
                        cost = incumbent_sols[-1].cost
                    else:
                        cost = -1

                    length_lines = [x for x in lines if "final sol length" in x]
                    length_line = length_lines[0]
                    length = float(length_line.split("\"")[3])
                    if cost <= 0:
                        mem_line = [x for x in lines if "out of memory" in x]
                        if len(mem_line) > 0 and "true" in mem_line[0]:
                            data.mem_fails[key] += 1
                        else:
                            data.deadend_fails[key] += 1
                except Exception as e:
                    print("exception for", alg, file)
                    print(e)
                    #print(traceback.format_exc())
                    cpu_time = 60*5
                    wall_time = 60*5
                    cost = 0
                    length = 0
                    num_sol = 0
                    fail = True
                    incumbent_sols = []
                if cost <= 0:
                    cost = 0
                    length = 0
                    num_sol = 0
                    fail = True

                if len(incumbent_sols) == 0:
                    incumbent_sols = [Solution(cost=cost,
                                               wall_time=wall_time,
                                               expanded=expanded,
                                               generated=generated)]
                data.costs[key].append(cost)
                data.sol_lengths[key].append(length)
                data.cpu_times[key].append(cpu_time)
                data.wall_times[key].append(wall_time)
                data.expanded[key].append(expanded)
                data.generated[key].append(generated)
                data.num_sols[key].append(num_sol)
                data.incumbent_sols[key].append(incumbent_sols)
        data.init_h.append(init_h)
        data.common.append(not fail)
        
    return data


def get_incumbent_sols(sol_lines): 
    if len(sol_lines) == 0 or len(sol_lines) == 1:
        return []
    sols = []
    sol_header = [x.strip().strip('"') for x in sol_lines[0].split('\t')]
    sol_lines = sol_lines[1:]
    cost_ind = sol_header.index("incumbent solution cost")
    time_ind = -1 if "incumbent wall time" not in sol_header else sol_header.index("incumbent wall time")
    exp_ind = sol_header.index("incumbent nodes expanded")
    gen_ind = sol_header.index("incumbent nodes generated")
    for sol_line in sol_lines:
        sol_info = sol_line.split('\t')
        sol = Solution(cost=float(sol_info[cost_ind]),
                       wall_time=float(sol_info[time_ind]),
                       expanded=int(sol_info[exp_ind]),
                       generated=int(sol_info[gen_ind]))
        sols.append(sol)
    return sols


            
try:
    from dataclasses import dataclass, field
    @dataclass
    class HstarData:
        good_lost: defaultdict = field(default_factory=lambda: defaultdict(list))
        state_h: defaultdict = field(default_factory=lambda: defaultdict(list))
        state_d: defaultdict = field(default_factory=lambda: defaultdict(list))
        used_states: defaultdict = field(default_factory=lambda: defaultdict(list))
        used_g: defaultdict = field(default_factory=lambda: defaultdict(list))
        used_depth: defaultdict = field(default_factory=lambda: defaultdict(list))
        unused_states: defaultdict = field(default_factory=lambda: defaultdict(list))
        unused_g: defaultdict = field(default_factory=lambda: defaultdict(list))
        unused_depth: defaultdict = field(default_factory=lambda: defaultdict(list))
        insts: list = field(default_factory=list)
except:
    class HstarData:
        def __init__(self):
            self.good_lost = defaultdict(list)
            self.used_states = defaultdict(list)
            self.unused_states = defaultdict(list)
            self.used_g = defaultdict(list)
            self.used_depth = defaultdict(list)
            self.unused_g = defaultdict(list)
            self.unused_depth = defaultdict(list)
            self.state_h = defaultdict(list)
            self.state_d = defaultdict(list)
            self.insts = []

# read an 8-puzzle state
def read_tile(l):
    s = ""
    for line in l:
        for t in line.split():
            s = s + t + " "
    return s[:-1]

def read_node_vals(l):
    g = float(l[0].split()[1])
    h = float(l[1].split()[1])
    d = float(l[2].split()[1])

    return g, h, d

widths = [100000, 30000, 10000, 3000, 1000, 300, 100, 30]

algs_unit = [("monobeam","-width",widths,True),
             ("beam","-width",widths,True)]

algs_non_unit = [("monobead","-width",widths,True),
                 ("bead","-width",widths,True)]

algs_reopen = [("monobeam","-width",widths,True),
               ("monobead","-width",widths,True),
               #("phc","-width",widths,True),
               #("phcd","-width",widths,True),
               ("beam","-width",widths,True),
               ("bead","-width",widths,True)]
algs_drop = [("monobeam","-width",widths,False),
             ("monobead","-width",widths,False),
             #("phc","-width",widths,False),
             #("phcd","-width",widths,False),
             ("beam","-width",widths,False),
             ("bead","-width",widths,False)]

# analyze_hstar("results-dump", "opt_costs", "8tiles", "unit", algs_reopen, True, [1042, 2042, 3042])

# read h* data and use it to analyze the nodes selected/not selected
# NOTE: currently only works for 8-puzzle
def analyze_hstar(dumps_dir, hstar_dir, domain, cst, algs, dup, insts=[]):
    cols = 3
    
    # grab h* data
    hstars = {}
    infile = open(hstar_dir+"/"+domain+"/"+cst, "r")
    lines = infile.readlines()
    for i in range(0, len(lines), cols+1):
        state = read_tile(lines[i:i+3])
        hstar = float(lines[i+3])
        hstars[state] = hstar
        
    
    # process dumps
    analysis = HstarData(insts = insts)
    for i in range(len(insts)):
        file = str(insts[i])
        for alg, arg, argvals, dups, *extra in algs:
            extra = tuple(extra)
            dupString = ["-dropdups", ""][dups]
            for argval in argvals:
                key = (alg, argval, dups, extra)
                analysis.good_lost[key].append([])
                infile = open(dumps_dir+"/"+domain+"/"+str(file)+alg
                              +dupString+arg+str(argval)
                              +"-"+cst, "r")
                lines = infile.readlines()

                # proceed through depth levels
                depth = 0
                l = 0
                while not lines[l].startswith("depth: "):
                    l += 1

                l += 2
                while l < len(lines):
                    depth += 1
                    # gather used states
                    used_hstars = []
                    while l < len(lines) and not lines[l].startswith("unused states:"):
                        t = read_tile(lines[l:l+cols])
                        l += cols
                        g, h, d = read_node_vals(lines[l:l+3])
                        analysis.used_states[key].append(t)
                        analysis.state_h[t] = h
                        analysis.state_d[t] = d
                        analysis.used_g[(key, t)] = g
                        analysis.used_depth[(key, t)] = depth
                        l += 4
                        if t in hstars:
                            used_hstars.append(hstars[t])
                        else:
                            print("BAD USED STATE:", t)
                            print("file:", dumps_dir+"/"+domain+"/"+str(file)+alg
                              +dupString+arg+str(argval)
                              +"-"+cst)

                    # gather unused states
                    l += 1
                    unused_hstars = []
                    while l < len(lines) and not lines[l].startswith("depth: "):
                        t = read_tile(lines[l:l+cols])
                        l += cols
                        g, h, d = read_node_vals(lines[l:l+3])
                        analysis.unused_states[key].append(t)
                        analysis.state_h[t] = h
                        analysis.state_d[t] = d
                        analysis.unused_g[(key, t)] = g
                        analysis.unused_depth[(key, t)] = depth
                        l += 4
                        if t in hstars:
                            unused_hstars.append(hstars[t])
                        else:
                            print("BAD UNUSED STATE:", t)
                            print("file:", dumps_dir+"/"+domain+"/"+str(file)+alg
                              +dupString+arg+str(argval)
                              +"-"+cst)

                    # determine statistics for used/unused states
                    better = []
                    q_used = [-x for x in used_hstars]
                    heapq.heapify(q_used)
                    q_unused = [x for x in unused_hstars]
                    heapq.heapify(q_unused)

                    while q_unused and q_used:
                        used = -1 * heapq.heappop(q_used)
                        unused = heapq.heappop(q_unused)

                        if unused < used:
                            better.append(unused)
                        else:
                            break
                    
                    analysis.good_lost[key][i].append(len([x for x in better]))
                    
                    l += 2
                #print(alg, "lost", good_lost)

    return analysis


def sort_lines(lines, sort_vals, ascend=False):
    pairs = list(zip(sort_vals, lines))
    pairs.sort(key=lambda x: x[0], reverse=(not ascend))
    return [x[1] for x in pairs]
    
try:
    from dataclasses import dataclass, field
    @dataclass
    class BeamDumpData:
        state_h: defaultdict = field(default_factory=lambda: defaultdict(list))
        state_d: defaultdict = field(default_factory=lambda: defaultdict(list))
        used_states: defaultdict = field(default_factory=lambda: defaultdict(list))
        used_g: defaultdict = field(default_factory=lambda: defaultdict(list))
        used_depth: defaultdict = field(default_factory=lambda: defaultdict(list))
        unused_states: defaultdict = field(default_factory=lambda: defaultdict(list))
        unused_g: defaultdict = field(default_factory=lambda: defaultdict(list))
        unused_depth: defaultdict = field(default_factory=lambda: defaultdict(list))
        insts: list = field(default_factory=list)
except:
    class BeamDumpData:
        def __init__(self):
            self.used_states = defaultdict(list)
            self.unused_states = defaultdict(list)
            self.used_g = defaultdict(list)
            self.used_depth = defaultdict(list)
            self.unused_g = defaultdict(list)
            self.unused_depth = defaultdict(list)
            self.state_h = defaultdict(list)
            self.state_d = defaultdict(list)
            self.insts = []


#algs_reopen = [("beam","-width",[100],True)]

def read_beam_dump(dumps_dir, domain, cst, algs, dup, insts=[]):
    cols = 4
    
    # process dumps
    analysis = BeamDumpData(insts = insts)
    for i in range(len(insts)):
        file = str(insts[i])
        for alg, arg, argvals, dups in algs:
            dupString = ["-dropdups", ""][dups]
            for argval in argvals:
                key = (alg, argval, dups)
                infile = open(dumps_dir+"/"+domain+"/"+str(file)+alg
                              +dupString+arg+str(argval)
                              +"-"+cst, "r")
                lines = infile.readlines()

                # proceed through depth levels
                depth = 0
                l = 0
                while not lines[l].startswith("depth: "):
                    l += 1

                l += 2
                while l < len(lines):
                    depth += 1
                    # gather used states
                    while l < len(lines) and not lines[l].startswith("unused states:"):
                        t = read_tile(lines[l:l+cols])
                        l += cols
                        g, h, d = read_node_vals(lines[l:l+3])
                        analysis.unused_states[key].append(t)
                        analysis.state_h[t] = h
                        analysis.state_d[t] = d
                        analysis.unused_g[(key, t)] = g
                        analysis.unused_depth[(key, t)] = depth
                        l += 4

                    # gather unused states
                    l += 1
                    while l < len(lines) and not lines[l].startswith("depth: "):
                        t = read_tile(lines[l:l+cols])
                        l += cols
                        g, h, d = read_node_vals(lines[l:l+3])
                        analysis.used_states[key].append(t)
                        analysis.state_h[t] = h
                        analysis.state_d[t] = d
                        analysis.used_g[(key, t)] = g
                        analysis.used_depth[(key, t)] = depth
                        l += 4
                
                    
                    l += 2
                #print(alg, "lost", good_lost)

    return analysis
