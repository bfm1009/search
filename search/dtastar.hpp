#pragma once
#include "../search/search.hpp"
#include "../utils/geom2d.hpp"
#include "../utils/pool.hpp"
#include <vector>

template <class D>
class Dtastar : public SearchAlgorithm<D> {
private:

	typedef typename D::PackedState PackedState;
	typedef typename D::Operators Operators;
	typedef typename D::State State;
	typedef typename D::Cost Cost;
	typedef typename D::Oper Oper;
	typedef typename D::Edge Edge;

	class Graph {
	public:

		Graph(SearchAlgorithm<D> &s, unsigned int sz) : nodes(sz), search(s) {
		}

		struct Node;

		struct Out {
			Out(Node *n, double c, Oper o) : node(n), cost(c), op(o) {
			}

			Node *node;
			double cost;
			Oper op;
		};

		struct Node {
			double h;
			bool isgoal;
			bool expd;	// Have we generated successors yet?
			std::vector<Out> succs;
			PackedState state;

		private:

			friend class Pool<Node>;
			friend class Graph;

			Node() : expd(false) {
			}

			ClosedEntry<Node, D> closedEnt;
		};

		static PackedState &key(Node *n) {
			return n->state;
		}

		static ClosedEntry<Node, D> &closedentry(Node *n) {
			return n->closedEnt;
		}

		// Node returns the node representing this state.
		Node *node(D &d, State &state) {
			Node *n = pool.construct();	
			d.pack(n->state, state);

			unsigned long hash = n->state.hash(&d);
			Node *found = nodes.find(n->state, hash);

			if (found) {
				pool.destruct(n);
				return found;
			}

			n->h = d.h(state);
			n->isgoal = d.isgoal(state);
			nodes.add(n, hash);
			return n;
		}

		// Succs returns the successors of the given node, either by
		// returning their cached values or by generating them.
		std::vector<Out>&succs(D &d, Node *n) {
			if (n->expd)
				return n->succs;

			search.res.expd++;

			State buf, &s = d.unpack(buf, n->state);
			Operators ops(d, s);
			for (unsigned int i = 0; i < ops.size(); i++) {
				search.res.gend++;

				Edge e(d, s, ops[i]);
				Node *k = node(d, e.state);
				n->succs.emplace_back(k, e.cost, ops[i]);
			}

			n->expd = true;
			return n->succs;
		}

		void clear() {
			for (auto n : nodes)
				pool.destruct(n);
			nodes.clear();
		}

	private:
		Pool<Node> pool;
		ClosedList<Graph, Node, D> nodes;

		// The search algorithm for counting expansions, generations, duplicates, etc.
		SearchAlgorithm<D> &search;
	};

	// Lss is a resumable A* search, defining the local search space beneath a node.
	class Lss {
	public:

		typedef typename Graph::Node GraphNode;

		struct Node {
			long openind, learnind;
			double g, f;
			Oper op;
			Node *parent;
			bool closed, updated;
			GraphNode *node;

		private:

			friend class Lss;
			friend class Pool<Node>;

			Node() : openind(-1), learnind(-1), closed(false), updated(false) {
			}

			ClosedEntry<Node, D> closedEnt;
		};

		static PackedState &key(Node *n) {
			return n->node->state;
		}

		static ClosedEntry<Node, D> &closedentry(Node *n) {
			return n->closedEnt;
		}

		// F orders nodes in increasing order of f, tie-breaking on high g.
		class F {
		public:
			static void setind(Node *n, long i) {
				n->openind = i;
			}

			static bool pred(Node *a, Node *b) {
				if (a->f == b->f)
					return a->g > b->g;
				return a->f < b->f;
			}
		};

		Lss(Dtastar<D> &s, Graph &g, GraphNode *c, GraphNode *rt, double g0, Oper o) :
			goal(NULL), root(rt), op(o), cur(c), nodes(s.lookahead), nclosed(0), search(s), graph(g) {

			Node *r = pool.construct();
			r->g = g0;
			r->f = root->h;
			r->parent = NULL;
			r->op = op;
			r->node = root;
			if (root->isgoal)
				goal = r;
			open.push(r);
		}

		// Expand performs no more than N expansions, returning true
		// if there are more nodes to be expanded and false otherwise.
		// If a goal is expanded then expand returns early.  If a goal was
		// expanded on a previous call then it return immediately.
		bool expand(D &d, unsigned int N) {
			if (open.empty() || (goal && goal->closed))
				return !open.empty();

			unsigned int expd = 0;
			while (!open.empty() && expd < N && !search.limit()) {
				Node *n = *open.pop();

				nclosed += !n->closed;
				n->closed = true;

				if (n->node->isgoal) {
					assert (goal);
					assert (goal == n || geom2d::doubleeq(goal->g, n->g));
					break;
				}

				expd++;
				for (auto e : graph.succs(d, n->node)) {
					if (e.node == cur || (n->parent && e.node == n->parent->node))
						continue;

					unsigned long hash = e.node->state.hash(&d);
					Node *k = nodes.find(e.node->state, hash);
					double g = n->g + e.cost;

					if (!k) {
						k = pool.construct();
						k->node = e.node;
						nodes.add(k, hash);
					} else if (k->g <= g) {
						continue;
					}

					k->parent = n;
					k->op = e.op;
					k->g = g;
					k->f = g + k->node->h;
					open.pushupdate(k, k->openind);

					if (k->node->isgoal && (!goal || k->g < goal->g))
						goal = k;
				}
			}

			return !open.empty();
		}

		// H orders nodes in increasing order on h.
		class H {
		public:
			static void setind(Node *n, long i) {
				n->learnind = i;
			}

			static bool pred(Node *a, Node *b) {
				return a->node->h < b->node->h;
			}
		};

		static void setind(Lss *l, long i) {
		}

		static bool pred(Lss *a, Lss *b) {
			auto af = a->fg();
			auto bf = b->fg();
			if (af.first == bf.first)
				return af.second > bf.second;
			return af.first < bf.first;
		}

		std::pair<double, double> fg() {
			if (open.empty() && !goal)
				return std::make_pair(geom2d::Infinity, geom2d::Infinity);
			if (open.empty())
				return std::make_pair(goal->g, goal->g);
			Node *front = *open.front();
			return std::make_pair(front->f, front->g);
		}

		// Goal is the cheapest goal that has been generated, or NULL
		// if no goal was generated.  If goal->closed is true then the
		// goal was expanded, and this is the optimal solution from the
		// root of this search.
		Node *goal;

		// Root is the root of this node.
		GraphNode *root;

		// Op is the operator generating the root of this tree from
		// the current node.
		Oper op;

	private:

		GraphNode *cur;

		Pool<Node> pool;
		BinHeap<F, Node*> open;
		ClosedList<Lss, Node, D> nodes;
		unsigned int nclosed;

		// The search algorithm used to check the limit.
		Dtastar<D> &search;
		Graph &graph;
	};

	typedef typename Graph::Node Node;

public:

	Dtastar(int argc, const char *argv[]) :
		SearchAlgorithm<D>(argc, argv),
		graph(*this, 30000001),
		lookahead(0) {

		for (int i = 0; i < argc; i++) {
			if (i < argc - 1 && strcmp(argv[i], "-lookahead") == 0)
				lookahead = strtoul(argv[++i], NULL, 10);
		}

		if (lookahead < 1)
			fatal("Must specify a lookahead ≥1 using -lookahead");
	}

	~Dtastar() {
	}

	void reset() {
		SearchAlgorithm<D>::reset();
		steps.clear();
		graph.clear();
	}

	virtual void output(FILE *out) {
		SearchAlgorithm<D>::output(out);
		dfpair(out, "num steps", "%lu", (unsigned long) steps.size());
		if (steps.size() != 0) {
			double mint = steps.front().time;
			double maxt = steps.front().time;

			unsigned int minl = steps.front().length;
			unsigned int maxl = steps.front().length;
			unsigned long nmoves = steps.front().length;

			for (unsigned int i = 1; i < steps.size(); i++) {
				double dt = steps[i].time - steps[i-1].time;
				if (dt < mint)
					mint = dt;
				if (dt > maxt)
					maxt = dt;

				unsigned int l = steps[i].length;
				if (l < minl)
					minl = l;
				if (l > maxl)
					maxl = l;
				nmoves += l;
			}
			dfpair(out, "first emit cpu time", "%f", steps.front().time);
			dfpair(out, "min step cpu time", "%f", mint);
			dfpair(out, "max step cpu time", "%f", maxt);
			dfpair(out, "mean step cpu time", "%f", (steps.back().time-steps.front().time)/steps.size());
			dfpair(out, "min step length", "%u", minl);
			dfpair(out, "max step length", "%u", maxl);
			dfpair(out, "mean step length", "%g", nmoves / (double) steps.size());
		}
	}

	void search(D &d, State &s0) {
		this->start();

		Node *cur = graph.node(d, s0);

		while (!cur->isgoal && !this->limit()) {
			auto p = step(d, cur);
			cur = p.second;
			this->res.ops.push_back(p.first);
			steps.emplace_back(cputime() - this->res.cpustart, 1);
		}
		this->finish();

		if (!cur->isgoal) {
			this->res.ops.clear();
			return;
		}

		// Rebuild the path from the operators.
		graph.clear();
		this->res.path.push_back(s0);
		for (auto o : this->res.ops) {
			State copy = this->res.path.back();
			Edge e(d, copy, o);
			this->res.path.push_back(e.state);
		}

		PackedState pkd;
		d.pack(pkd, this->res.path.back());
		assert (pkd.eq(&d, cur->state));

		assert (d.isgoal(this->res.path.back()));
		std::reverse(this->res.ops.begin(), this->res.ops.end());
		std::reverse(this->res.path.begin(), this->res.path.end());
	}

	std::pair<Oper, Node*> step(D &d, Node *cur) {
		BinHeap<Lss, Lss*> lss;
		for (auto s : graph.succs(d, cur))
			lss.push(new Lss(*this, graph, cur, s.node, s.cost, s.op));

		for (unsigned int e = 0; e < lookahead && !this->limit(); e++) {
			Lss *l = *lss.front();

			if (l->goal && l->goal->closed)
				break;

			l->expand(d, 1);
 			lss.update(0);
		}

		Lss *best = *lss.front();
		auto fg = best->fg();
		cur->h = fg.first * 1.10;	// best + 10%

		auto p = std::make_pair(best->op, best->root);

		for (auto l : lss.data())
			delete l;

		return p;
	}

private:

	struct Step {
		Step(double t, unsigned int l) : time(t), length(l) {
		}

		double time;
		unsigned int length;
	};

	std::vector<Step> steps;

	Graph graph;
	unsigned int lookahead;
};
