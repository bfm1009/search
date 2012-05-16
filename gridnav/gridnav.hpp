#pragma once

#include "gridmap.hpp"
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <cassert>

struct GridNav {

	struct Cost {
		Cost() { }

		explicit Cost(int u, int s = 0) : units(u), sqrts(s) { compute(); }

		Cost &operator=(const Cost &o) {
			units = o.units;
			sqrts = o.sqrts;
			val = o.val;
			return *this;
		}

		Cost &operator+=(const Cost &o) {
			units += o.units;
			sqrts += o.sqrts;
			compute();
			return *this;
		}

		Cost &operator-=(const Cost &o) {
			units -= o.units;
			sqrts -= o.sqrts;
			compute();
			return *this;
		}

		operator double() { return val; }

		Cost operator+(const Cost &o) const {
			return Cost(units + o.units, sqrts + o.sqrts);
		}

		Cost operator-(const Cost &o) const {
			return Cost(units - o.units, sqrts - o.sqrts);
		}

		bool operator<(const Cost &o) const {
			return val < o.val;
		}

		bool operator>(const Cost &o) const {
			return val > o.val;
		}

		bool operator==(const Cost &o) const {
			return units == o.units && sqrts == o.sqrts;
		}

		bool operator!=(const Cost &o) const {
			return !(*this == o);
		}

		bool operator>=(const Cost &o) const {
			return !(*this < o);
		}

		bool operator<=(const Cost &o) const {
			return !(*this > o);
		}

	private:

		void compute() {
			val = units + sqrts * sqrt(2);
		}

		int units, sqrts;
		double val;
	};

	typedef int Oper;	// Index into the ops arrays.
	enum { Nop = -1 };

	GridNav(GridMap*, unsigned int, unsigned int,
		unsigned int, unsigned int);

	struct State {
		State &operator=(const State &o) {
 			loc = o.loc;
 			return *this;
		}

		State() { }

		State (const State &o) : loc(o.loc) { }

		State(unsigned int l) : loc(l) { }

	private:
		friend struct GridNav;
		unsigned int loc;
	};

	struct PackedState {
		unsigned int loc;

		bool operator==(const PackedState &o) const {
			return o.loc == loc;
		}
	};

	State initialstate() const;

	unsigned long hash(PackedState &p) {
		return p.loc;
	}

	Cost h(State &s) const {
		if (map->nmvs > 4)
			return octiledist(s.loc, finish);
		return manhattan(s.loc, finish);
	}

	Cost d(State &s) const {
		if (map->nmvs > 4)
			return octilecells(s.loc, finish);
		return manhattan(s.loc, finish);
	}

	bool isgoal(State &s) const {
		return s.loc == finish;
	}

	struct Operators {
		Operators(const GridNav &d, const State &s) : n(0) {
			for (unsigned int i = 0; i < d.map->nmvs; i++) {
				if (d.map->ok(s.loc, d.map->mvs[i]))
					ops[n++] = i;
			}
		}

		unsigned int size() const {
			return n;
		}

		Oper operator[](unsigned int i) const {
			return ops[i];
		}

	private:
		unsigned int n;
		Oper ops[8];
	};

	struct Edge {
		Cost cost;
		Oper revop;
		State state;

		Edge(const GridNav &d, State &s, Oper op) :
				revop(d.rev[op]),
				state(s.loc + d.map->mvs[op].delta) {
			assert (state.loc < d.map->sz);
			if (d.map->mvs[op].cost == 1.0)
				cost = Cost(1, 0);
			else
				cost = Cost(0, 1);
		}
	};

	void pack(PackedState &dst, State &src) const {
		dst.loc = src.loc;
	}

	State &unpack(State &buf, PackedState &pkd) const {
		buf.loc = pkd.loc;
		return buf;
	}

	void dumpstate(FILE *out, State &s) const {
		std::pair<int,int> coord = map->coord(s.loc);
		fprintf(out, "%u, %u\n", coord.first, coord.second);
	}

	// pathcost returns the cost of the given path.
	Cost pathcost(const std::vector<State>&, const std::vector<Oper>&) const;

	unsigned int start, finish;
	GridMap *map;

	// rev holds the index of the reverse of each operator
	int rev[8];

private:

	// manhattan returns the Manhattan distance.
	Cost manhattan(int l0, int l1) const {
		std::pair<int,int> c0 = map->coord(l0), c1 = map->coord(l1);
		return Cost(abs(c0.first - c1.first) + abs(c0.second - c1.second), 0);
	}

	// octiledist returns an admissible heuristic estimate for eight-way grids.
	Cost octiledist(int l0, int l1) const {
		std::pair<int,int> c0 = map->coord(l0), c1 = map->coord(l1);
		int dx = abs(c0.first - c1.first);
		int dy = abs(c0.second - c1.second);
		int diag = dx < dy ? dx : dy;
		int straight = dx < dy ? dy : dx;
		return Cost(straight - diag, diag);
	}

	// octilecells returns an admissible distance estimate for eight-way grids.
	Cost octilecells(unsigned int l0, unsigned int l1) const {
		std::pair<int,int> c0 = map->coord(l0), c1 = map->coord(l1);
		int dx = abs(c0.first - c1.first);
		int dy = abs(c0.second - c1.second);
		return Cost(dx < dy ? dy : dx, 0);
	}

	// reverseops computes the reverse operators
	void reverseops();
};
