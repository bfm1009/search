// Copyright © 2013 the Search Authors under the MIT license. See AUTHORS for the list of authors.
#include <cstdio>
#include "../search/search.hpp"

void dfrowhdr(FILE*, const char*, unsigned int, ...);
void dfrow(FILE*, const char*, const char*, ...);

template <class D> class DFSstar : public SearchAlgorithm<D> {

public:

	typedef typename D::State State;
	typedef typename D::Cost Cost;
	typedef typename D::Oper Oper;

	DFSstar(int argc, const char *argv[]) :
		SearchAlgorithm<D>(argc, argv) { }

	void search(D &d, State &s0) {
		this->start();
		numsols = 0;
		bound = d.h(s0);
		dfrowhdr(stdout, "iter", 4, "iter no", "iter bound",
			"iter expd", "iter gend");

		i = 0;
		while (!dfs(d, s0, D::Nop, Cost(0)) && !SearchAlgorithm<D>::limit()) {

			dfrow(stdout, "iter", "dguu", (long) i, (double) bound,
				SearchAlgorithm<D>::res.expd, SearchAlgorithm<D>::res.gend); 

			bound = (Cost)(bound * 2);
			i++;
		}

		if(numsols > 0) {
			rebuild_sol(d, s0, D::Nop, Cost(0));
		}

		this->finish();
	}

private:
	bool dfs(D &d, State &s, Oper pop, Cost g) {
		Cost f = g + d.h(s);

		if (f <= bound && d.isgoal(s)) {
			if (numsols == 0) {
				dfrow(stdout, "iter", "dguu", (long) i, (double) bound,
					  SearchAlgorithm<D>::res.expd,
					  SearchAlgorithm<D>::res.gend); 
				rowhdr();
			}

			if(numsols == 0 || f < bound) {
				numsols++;
				row(numsols, f);
				bound = f;
			}
			
			return true;
		}

		if (f > bound) {
			return false;
		}

		this->res.expd++;

		typename D::Operators ops(d, s);
		bool solved = false;
		for (unsigned int n = 0; n < ops.size(); n++) {
			if (this->limit())
				return false;
			if (ops[n] == pop)
				continue;

			this->res.gend++;
			bool goal = false;
			{	// Put the transition in a new scope so that
				// it is destructed before we test for a goal.
				typename D::Edge e(d, s, ops[n]);
				goal = dfs(d, e.state, e.revop, g + e.cost);
			}

			if (goal) {
			  solved = true;
			}
		}

		return solved;
	}

	// rowhdr outputs the incumbent solution row header line.
	void rowhdr() {
		dfrowhdr(stdout, "incumbent", 6, "num", "nodes expanded",
			"nodes generated", "solution bound", "solution cost",
			"wall time");
	}

	// row outputs an incumbent solution row.
	void row(unsigned long n, Cost cost) {
		dfrow(stdout, "incumbent", "uuuggg", n, this->res.expd,
			  this->res.gend, bound, cost,
			walltime() - this->res.wallstart);
	}

	bool rebuild_sol(D &d, State &s, Oper pop, Cost g) {
		Cost f = g + d.h(s);

		if (f <= bound && d.isgoal(s)) {
			this->res.path.push_back(s);
			return true;
		}

		if (f > bound) {
			return false;
		}

		this->res.expd++;

		typename D::Operators ops(d, s);
		for (unsigned int n = 0; n < ops.size(); n++) {
			if (this->limit())
				return false;
			if (ops[n] == pop)
				continue;

			this->res.gend++;
			bool goal = false;
			{	// Put the transition in a new scope so that
				// it is destructed before we test for a goal.
				// If a goal was found then we want the
				// transition reverted so that we may push
				// the parent state onto the path.
				typename D::Edge e(d, s, ops[n]);
				goal = rebuild_sol(d, e.state, e.revop, g + e.cost);
			}

			if (goal) {
				this->res.path.push_back(s);
				this->res.ops.push_back(ops[n]);
				return true;
			}
		}

		return false;
	}
	
	Cost bound;
	int i;
	int numsols;
};
