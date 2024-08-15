// © 2013 the Search Authors under the MIT license. See AUTHORS for the list of authors.

#include "mdist.hpp"
#include <cstdlib>
#include <limits>
#include <vector>
#include <math.h>

TilesMdist::TilesMdist(FILE *in, const char *cost) : Tiles(in) {
	initcosts(cost);
	initmd();
	initincr();
}

TilesMdist::State TilesMdist::initialstate() {
	State s;
	s.h = 0;
	s.d = 0;
	for (unsigned int i = 0; i < Ntiles; i++) {
		if (init[i] == 0)
			s.b = i;
		else {
			s.h += costs[init[i]] * md[init[i]][i];
			s.d += md[init[i]][i];
		}
		s.ts[i] = init[i];
	}
	return s;
}

void TilesMdist::initcosts(const char *cost) {
  double mult = 10000.0;
  minCost = std::numeric_limits<long int>::max();
  costs[0] = 0;
  for(unsigned int t = 1; t < Ntiles; t++) {
	if(strcmp(cost, "heavy") == 0)
	  costs[t] = (long int) (t * mult);
	else if(strcmp(cost, "sqrt") == 0)
	  costs[t] = (long int) (sqrt(t) * mult);
	else if(strcmp(cost, "inverse") == 0)
	  costs[t] = (long int) (1.0/t * mult);
	else if(strcmp(cost, "reverse") == 0)
	  costs[t] = (long int) ((Ntiles-t) * mult);
	else if(strcmp(cost, "revinv") == 0)
	  costs[t] = (long int) (1.0/(Ntiles-t) * mult);
	else
	  costs[t] = (long int) (1 * mult);
	if(costs[t] < minCost)
	  minCost = costs[t];
  }
  
}

void TilesMdist::initmd() {
	for (unsigned int t = 1; t < Ntiles; t++) {
		int row = goalpos[t] / Width;
		int col = goalpos[t] % Width;
		for (int i = 0; i < Ntiles; i++) {
			int r = i / Width;
			int c = i % Width;

			md[t][i] = abs(r - row) + abs(c - col);
		}
	}
}

void TilesMdist::initincr() {
	for (unsigned int t = 1; t < Ntiles; t++) {
	for (unsigned int nw = 0; nw < Ntiles; nw++) {
		unsigned int next = md[t][nw];
		for (unsigned int n = 0; n <ops[nw].n; n++) {
			unsigned int old = ops[nw].mvs[n];
			incr[t][nw][old] = md[t][old] - next;
		}
	}
	}
}

TilesMdist::Cost TilesMdist::pathcost(const std::vector<State> &path, const std::vector<Oper> &ops) {
	State state = initialstate();
	Cost cost(0);

	if (ops.size() > (unsigned int) std::numeric_limits<int>::max())
		fatal("Too many actions");

	for (int i = ops.size() - 1; i >= 0; i--) {
		State copy(state);
		Edge e(*this, copy, ops[i]);
		cost += e.cost;
		assert(e.state == path[i]);
		state = e.state;
	}
	assert (isgoal(state));
	return cost;
}
