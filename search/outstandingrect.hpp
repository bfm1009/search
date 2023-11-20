// Copyright © 2023 the Search Authors under the MIT license. See AUTHORS for the list of authors.
// Additional author: Bryan McKenney                                                                   
#pragma once                                                                    
#include "../search/search.hpp"                                                 
#include "../utils/pool.hpp"
#include "../structs/binheap.hpp"
#include <list>
#include <iostream>
#include <limits>
                                                                                
template <class D> struct OutstandingRectSearch : public SearchAlgorithm<D> {

	typedef typename D::State State;
	typedef typename D::PackedState PackedState;                                
	typedef typename D::Cost Cost;                                              
	typedef typename D::Oper Oper;
  

	struct Node {
		int openind;
		Node *parent;
		PackedState state;
		Oper op, pop;
		int d, depth;
		Cost f, g, h;
		double discrep;
  
		Node() : openind(-1), discrep(std::numeric_limits<double>::max()) {
		}

		static ClosedEntry<Node, D> &closedentry(Node *n) {
			return n->closedent;
		}

		static PackedState &key(Node *n) {
			return n->state;
		}

		/* Set index of node on open list. */
		static void setind(Node *n, int i) {
			n->openind = i;
		}

		/* Get index of node on open list. */
		static int getind(const Node *n) {
			return n->openind;
		}

		/* Indicates whether Node a has better value than Node b. */
		static bool pred(Node *a, Node *b) {
			if (a->discrep == b->discrep) {
				if (a->f == b->f)
					return a->h < b->h;
				return a->f < b->f;
			}
			return a->discrep < b->discrep;
		}

    private:
		ClosedEntry<Node, D> closedent;
    
	};

	struct DepthNode {
		int heapind;
		DepthNode *next;
		int depth, dBest, expansions;
		OpenList<Node, Node, double> *openlist;
  
		DepthNode(int depth) : heapind(-1), next(NULL), depth(depth),
			dBest(std::numeric_limits<int>::max()), expansions(0), openlist(new OpenList<Node, Node, double>()) {}

		~DepthNode() {
			delete openlist;
		}

		/*
		 * Add node to open list
		 * and return whether or not it has a new best d.
		 */
		bool addToOpenlist(Node *n, DepthNode *lockedDepth) {
			bool dBestChanged = false;
			if (n->d < dBest) {
				dBest = n->d;
				dBestChanged = true;
			}
			if (this != lockedDepth) calcDiscrep((void*) &dBest, n);
			openlist->push(n);
			return dBestChanged;
		}

		/* Calculate the discrepancy score of each node in the open list. */
		void calcDiscreps(BinHeap<DepthNode, DepthNode*> &openlists) {
			openlist->foreach((void*) &dBest, &DepthNode::calcDiscrep);
			openlists.update(heapind);
		}

		/* Set index of DepthNode on heap. */
		static void setind(DepthNode *n, int i) {
			n->heapind = i;
		}

		/* Get index of DepthNode on heap. */
		static int getind(const DepthNode *n) {
			return n->heapind;
		}

		/* Indicates whether DepthNode a has better value than DepthNode b. */
		static bool pred(DepthNode *a, DepthNode *b) {
			Node *aBestNode = a->openlist->front();
			Node *bBestNode = b->openlist->front();
			if (!aBestNode) return false;
			if (!bBestNode) return true;
			if (aBestNode->discrep == bBestNode->discrep) {
				//if (a->expansions == b->expansions)
					return a->depth < b->depth;
				//return a->expansions < b->expansions;
			}
			return aBestNode->discrep < bBestNode->discrep;
		}

	private:
		/* Calculate the discrepancy score of a node. */
		static void calcDiscrep(void *dBestPtr, Node *n) {
			int dBest = *((int*) dBestPtr);
			n->discrep = n->d - dBest;
		}
	};
  

	OutstandingRectSearch(int argc, const char *argv[]) :
		SearchAlgorithm<D>(argc, argv), closed(30000001) {
		dropdups = false;
		dump = false;
		aspect = 1;

		for (int i = 0; i < argc; i++) {
			if (strcmp(argv[i], "-dropdups") == 0)
				dropdups = true;
			if (strcmp(argv[i], "-dump") == 0)
				dump = true;
			if (i < argc - 1 && strcmp(argv[i], "-aspect") == 0)
				aspect = atoi(argv[++i]);
		}
    
		nodes = new Pool<Node>();
	}

	~OutstandingRectSearch() {
		delete nodes;
	}

	Node *dedup(D &d, Node *n) {

	  if(cand && n->f >= cand->g) {
		nodes->destruct(n);
		return NULL;
	  }
	  
	  unsigned long hash = n->state.hash(&d);
	  Node *dup = closed.find(n->state, hash);
	  if(!dup) {
		closed.add(n, hash);
	  } else {
		SearchAlgorithm<D>::res.dups++;
		if(!dropdups && n->g < dup->g) {
		  SearchAlgorithm<D>::res.reopnd++;
					
		  dup->f = dup->f - dup->g + n->g;
		  dup->g = n->g;
		  dup->d = n->d;
		  dup->parent = n->parent;
		  dup->op = n->op;
		  dup->pop = n->pop;
		} else {
		  nodes->destruct(n);
		  return NULL;
		}
	  }

	  return n;
	}

	void search(D &d, typename D::State &s0) {
		this->start();
		closed.init(d);

		Node *n0 = init(d, s0);
		closed.add(n0);
		
		if(dump) {
		  fprintf(stderr, "depth,expnum,state,g\n");
		  fprintf(stderr, "0,%lu,", SearchAlgorithm<D>::res.expd);
		  State buf, &state = d.unpack(buf, n0->state);
		  d.dumpstate(stderr, state);
		  fprintf(stderr, ",%f\n", (float)n0->g);
		}

		depth = 0;
		open_count = 0;
		sol_count = 0;
		iteration = 1;
		addDepthLevel();
		expand(d, n0, s0, lockedDepth);
		addDepthLevel();

		dfrowhdr(stdout, "incumbent", 5, "num", "nodes expanded",
			"nodes generated", "solution cost", "wall time");
    
		while (!SearchAlgorithm<D>::limit()) {
			DepthNode *curDepth = openlists.frontUnsafe();

			// End search if search space has been exhausted
			if (curDepth->openlist->empty()) break;

			// Expand nodes until new depth
			while (curDepth->next) {
				expandBestNodeAtDepth(d, curDepth);
				curDepth = curDepth->next;
			}

			// Expand nodes at new depths
			for (int i = 0; i < aspect; i++) {
				addDepthLevel();

				for (int j = 0; j < iteration; j++) {
					expandBestNodeAtDepth(d, curDepth);
					if (curDepth->openlist->empty()) break;
				}

				curDepth = curDepth->next;
			}

			iteration++;
		}

		if(cand)
		  solpath<D, Node>(d, cand, this->res);

		this->finish();
	}

	virtual void reset() {
		SearchAlgorithm<D>::reset();
		closed.clear();
		delete nodes;
		nodes = new Pool<Node>();
	}

	virtual void output(FILE *out) {
		SearchAlgorithm<D>::output(out);
		closed.prstats(stdout, "closed ");
		dfpair(stdout, "open lists created", "%d", openlists.size());
		dfpair(stdout, "open list type", "%s", openlists.frontUnsafe()->openlist->kind());
		dfpair(stdout, "node size", "%u", sizeof(Node));
	}


private:

    void expandBestNodeAtDepth(D &d, DepthNode *depthLevel) {
		Node *n = NULL;
		OpenList<Node, Node, double> *open = depthLevel->openlist;
		
		while (!n && !open->empty()) {
			n = dedup(d, open->pop());
			openlists.update(depthLevel->heapind);
			open_count--;
		}

		if (n) {
			State buf, &state = d.unpack(buf, n->state);
			if(dump) {
				fprintf(stderr, "%d,%lu,", depthLevel->depth,
					SearchAlgorithm<D>::res.expd);
				d.dumpstate(stderr, state);
				fprintf(stderr, ",%f\n", (float)n->g);
			}
			expand(d, n, state, depthLevel->next);
			depthLevel->expansions++;
		}
    }

  void expand(D &d, Node *n, State &state, DepthNode *nextDepth) {
		//cout << "expanding node at depth " << nextDepth->depth - 1 << endl;

		SearchAlgorithm<D>::res.expd++;
		bool dBestChanged = false;

		typename D::Operators ops(d, state);
		for (unsigned int i = 0; i < ops.size(); i++) {
			if (ops[i] == n->pop)
				continue;
			SearchAlgorithm<D>::res.gend++;
			bool changed = considerkid(d, n, state, ops[i], nextDepth);
			dBestChanged = dBestChanged || changed;
		}

		// Update discrepancy scores at next depth if necessary
		if (dBestChanged && nextDepth != lockedDepth)
			nextDepth->calcDiscreps(openlists);

		// Update position of next depth in openlists heap
		openlists.update(nextDepth->heapind);
	}

  bool considerkid(D &d, Node *parent, State &state, Oper op, DepthNode *nextDepth) {
		Node *kid = nodes->construct();
		assert (kid);
		typename D::Edge e(d, state, op);
		kid->g = parent->g + e.cost;
		d.pack(kid->state, e.state);

		kid->h = d.h(e.state);
		kid->f = kid->g + kid->h;
		kid->d = d.d(e.state);
		kid->parent = parent;
		kid->op = op;
		kid->pop = e.revop;
		
		State buf, &kstate = d.unpack(buf, kid->state);
		if (d.isgoal(kstate) && (!cand || kid->g < cand->g)) {
		  
		  if(dump) {
			fprintf(stderr, "%d,%lu,", nextDepth->depth - 1,
					SearchAlgorithm<D>::res.expd);
			d.dumpstate(stderr, kstate);
			fprintf(stderr, ",%f\n", (float)kid->g);
		  }
		
		  cand = kid;
		  sol_count++;
		  dfrow(stdout, "incumbent", "uuugg", sol_count, this->res.expd,
				this->res.gend, (float)cand->g,
				walltime() - this->res.wallstart);
		  return false;
		} else if(cand && cand->g <= kid->f) {
		  nodes->destruct(kid);
		  return false;
		}

		open_count++;
		bool dBestChanged = nextDepth->addToOpenlist(kid, lockedDepth);
		return dBestChanged;
	}

	Node *init(D &d, State &s0) {
		Node *n0 = nodes->construct();
		d.pack(n0->state, s0);
		n0->d = d.d(s0);
		n0->g = Cost(0);
		n0->h = d.h(s0);
		n0->f = n0->h;
		n0->pop = n0->op = D::Nop;
		n0->parent = NULL;
		cand = NULL;
		lockedDepth = NULL;
		return n0;
	}

	/* Unlock the deepest depth, then add another depth level. */
	void addDepthLevel() {
		DepthNode *newDeepest;

		if (!lockedDepth) // Depth = 0
			newDeepest = new DepthNode(1);
		else {
			newDeepest = new DepthNode(lockedDepth->depth + 1);
			lockedDepth->next = newDeepest;
			lockedDepth->calcDiscreps(openlists);
		}

		openlists.push(newDeepest);
		lockedDepth = newDeepest;
		depth++;
	}

	int aspect;
	int iteration;
    bool dropdups;
    bool dump;
    BinHeap<DepthNode, DepthNode*> openlists;
 	ClosedList<Node, Node, D> closed;
	Pool<Node> *nodes;
	Node *cand;
	DepthNode *lockedDepth;
	int depth;
	int open_count;
	int sol_count;
};
