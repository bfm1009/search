#pragma once

#include <cstdio>
#include <vector>
#include <signal.h>

#include "../structs/intpq.hpp"
#include "../structs/binheap.hpp"

#include "closedlist.hpp"

double walltime();
double cputime();
void dfpair(FILE *f, const char *key, const char *fmt, ...);

// A SearchStats structure contains statistical information
// collected during a run of a search algorithm.
struct SearchStats {
	double wallstrt, cpustrt;
	double wallend, cpuend;
	unsigned long expd, gend, reopnd, dups;

	SearchStats();

	// start must be called by the search in order to
	// begin collecting statistical information.
	void strt();

	// finish must be called by the search in order to
	// stop collecting information.
	void fin();

	// output prints the statistical information to the given
	// file in datafile format.
	void output(FILE*);

	// add accumulated the statistical information from
	// the given search statistics in the receiver.
	void add(SearchStats &other) {
		expd += other.expd;
		gend += other.gend;
		reopnd += other.reopnd;
		dups += other.dups;

		double wt = wallend - wallstrt;
		double ct = cpuend - cpustrt;
		wallstrt = cpustrt = 0;
		wallend = wt + (other.wallend - other.wallstrt);
		cpuend = ct + (other.cpuend - other.cpustrt);
	}
};

// A Limit structure contains information about when a
// search algorithm should be stopped because it has
// hit a user specified limit.
struct Limit {

	Limit();

	Limit(int, const char*[]);

	// reached returns true when the given statistics
	// reports that the given limit has been reached.
	bool reached(SearchStats &r) {
		return timeup ||
			(expd > 0 && r.expd >= expd) ||
			(gend > 0 && r.gend >= gend);
	}

	// output prints the limit to the given file in datafile
	// format.
	void output(FILE*);

	// start must be called at the beginning of a search
	// that would like to use the limit.
	void start();

	// finish must be called when a search, using the limit
	// has finished.
	void finish();

	unsigned long expd, gend, mem, cputime, walltime;
	volatile sig_atomic_t timeup;
private:
	void memlimit(const char*);
	void timelimit(const char*);
};

// SearchNode is a structure that encapsulates information that
// is shared between many search algorithms' node structures.
// A SearchNode contains parent node and operator information
// for constructing a solution path.  It also implements the operations
// for a closed list and both a bucked and priority queue open list.
template <class D> struct SearchNode {
private:
	ClosedEntry<SearchNode, D> closedent;

public:
	int ind;
	typename D::PackedState packed;
	typename D::Cost g;
	typename D::Oper op;
	typename D::Oper pop;
	SearchNode *parent;

	SearchNode() : ind(-1) { }

	// setind sets index field to the given value.
	static void setind(SearchNode *n, int i) { n->ind = i; }
	
	// getind returns the value of the index field.
	static int getind(SearchNode *n) { return n->ind; }

	// entry returns a reference to the closed list entry of the
	// given node.
	static ClosedEntry<SearchNode, D> &closedentry(SearchNode *n) {
		return n->closedent;
	}

	// key returns the hash table key value for the given node.
	// The key is the packed state representation from the
	// search domain.
	static typename D::PackedState &key(SearchNode *n) {
		return n->packed;
	}

	// update updates the g, parent, op and pop fields of
	// the receiver to match that of another node.
	void update(const SearchNode &other) {
		g = other.g;
		parent = other.parent;
		op = other.op;
		pop = other.pop;
	}

	// update updates the corresponding fields of the given node.
	void update(const typename D::Cost &g, SearchNode *parent,
			const typename D::Oper &op,
			const typename D::Oper &pop) {
		this->g = g;
		this->parent = parent;
		this->op = op;
		this->pop = pop;
	}
};

// An OpenList holds nodes and returns them ordered by some
// priority.  The Ops class has a pred method which accepts
// two Nodes and returns true if the 1st node is a predecessor
// of the second.
template <class Ops, class Node, class Cost> class OpenList {
public:
	const char *kind() { return "binary heap"; }

	void push(Node *n) { heap.push(n); }

	Node *pop() {
		boost::optional<Node*> p = heap.pop();
		if (!p)
			return NULL;
		return *p;
	}

	void pre_update(Node *n) { }

	void post_update(Node *n) {
		if (n->ind < 0)
			heap.push(n);
		else
			heap.update(Ops::getind(n));
	}

	bool empty() { return heap.empty(); }

	bool mem(Node *n) { return n->ind != -1; }

	void clear() { heap.clear(); }

private:
	struct Heapops {
 		static bool pred(Node *a, Node *b) { return Ops::pred(a, b); }

		static void setind(Node *n, int i) { Ops::setind(n, i); }
	};
	BinHeap<Heapops, Node*> heap;
};

typedef int IntOpenCost;

// The Ops struct has prio and tieprio methods,
// both of which return ints.  The list is sorted in increasing order
// on the prio key then secondary sorted in decreasing order on
// the tieprio key.
template <class Ops, class Node> class OpenList <Ops, Node, IntOpenCost> {

	struct Maxq {
		Maxq() : fill(0), max(0), bkts(100)  { }

		void push(Node *n, unsigned long p) {
			if (bkts.size() <= p)
				bkts.resize(p+1);

			if (p > max)
				max = p;

			Ops::setind(n, bkts[p].size());
			bkts[p].push_back(n);
			fill++;
		}

		Node *pop() {
			for ( ; bkts[max].empty() && max > 0; max--)
				;
			Node *n = bkts[max].back();
			bkts[max].pop_back();
			Ops::setind(n, -1);
			fill--;
			return n;
		}

		void rm(Node *n, unsigned long p) {
			assert (p < bkts.size());
			std::vector<Node*> &bkt = bkts[p];

			unsigned int i = Ops::getind(n);
			assert (i < bkt.size());

			if (bkt.size() > 1) {
				bkt[i] = bkt[bkt.size() - 1];
				Ops::setind(bkt[i], i);
			}

			bkt.pop_back();
			Ops::setind(n, -1);
			fill--;
		}

		bool empty() { return fill == 0; }

		unsigned long fill;
		unsigned int max;
		std::vector< std::vector<Node*> > bkts;
	};

	unsigned long fill;
	unsigned int min;
	std::vector<Maxq> qs;

public:
	OpenList() : fill(0), min(0), qs(100) { }

	static const char *kind() { return "2d bucketed"; }

	void push(Node *n) {
		unsigned long p0 = Ops::prio(n);
 
		if (qs.size() <= p0)
			qs.resize(p0+1);

		if (p0 < min)
			min = p0;

		qs[p0].push(n, Ops::tieprio(n));
		fill++;
	}

	Node *pop() {
		for ( ; min < qs.size() && qs[min].empty() ; min++)
			;
		fill--;
		return qs[min].pop();		
	}

	void pre_update(Node*n) {
		if (Ops::getind(n) < 0)
			return;
		assert ((unsigned long) Ops::prio(n) < qs.size());
		qs[Ops::prio(n)].rm(n, Ops::tieprio(n));
		fill--;
	}

	void post_update(Node *n) {
		assert (Ops::getind(n) < 0);
		push(n);
	}

	bool empty() { return fill == 0; }

	bool mem(Node *n) { return Ops::getind(n) >= 0; }

	void clear() {
		qs.clear();
		min = 0;
	}
};

// A Result is returned from a completed search.  It contains
// statistical information about the search along with the
// solution cost and solution path if a goal was found.
template <class D> struct Result : public SearchStats {
	std::vector<typename D::State> path;
	std::vector<typename D::Oper> ops;

	Result() { }

	// Sets the cost and solution path of the result to that of
	// the given goal node.
	void goal(D &d, SearchNode<D> *goal) {
		ops.clear();
		path.clear();
		for (SearchNode<D> *n = goal; n; n = n->parent) {
			typename D::State buf, &state = d.unpack(buf, n->packed);
			path.push_back(state);
			if (n->parent)
				ops.push_back(n->op);
		}
	}

	// output writes information to the given file in
	// datafile format.
	void output(FILE *f) {
		dfpair(f, "state size", "%u", sizeof(typename D::State));
		dfpair(f, "packed state size", "%u", sizeof(typename D::PackedState));
		dfpair(f, "final sol length", "%lu", (unsigned long) path.size());
		SearchStats::output(f);
	}

	// add accumulates information from another Result
	// in the receiver.  The path infromation is not accumulated.
	void add(Result<D> &other) {
		SearchStats::add(other);
	}
};

template <class D> class SearchAlgorithm {
public:
	SearchAlgorithm(int argc, const char *argv[]) : lim(argc, argv) { }

	virtual ~SearchAlgorithm() { }

	virtual void search(D &, typename D::State &) = 0;

	virtual void reset() {
		res = Result<D>();
	}

	virtual void output(FILE *f) {
		lim.output(f);
		res.output(f);
	}

	void start() {
		res.strt();
		lim.start();
	}

	void finish() {
		res.fin();
		lim.finish();
	}

	Result<D> res;
	Limit lim;

protected:
	bool limit() { return lim.reached(res); }
};
