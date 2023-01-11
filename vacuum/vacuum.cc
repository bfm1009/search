// © 2013 the Search Authors under the MIT license. See AUTHORS for the list of authors.

#include "vacuum.hpp"
#include <utility>

Vacuum::Vacuum(FILE *in, const char *cost) : x0(-1), y0(-1) {
	int w, h;
	if (fscanf(in, "%d\n%d\n", &w, &h) != 2)
		fatal("Failed to read the width and height");

	map = new GridMap(w, h);
	dirt.resize(map->sz, -1);
	chargers.resize(map->sz, false);

	for (int y = 1; y < h+1; y++) {
		for (int x = 1; x < w+1; x++) {
			int c = getc(in);
			switch (c) {
			case '#':
				map->block(map->index(x, y));
				break;

			case '*':
				dirt[map->index(x, y)] = ndirt();
				dirtLocs.push_back(std::make_pair(x, y));
				break;

			case '@':
				x0 = x;
				y0 = y;
				break;

			case ':':
				chargers[map->index(x, y)] = true;
				break;

			case '_':
				break;

			default:
				fatal("Unknow character %c", c);
			}
		}
		if (y < h && getc(in) != '\n')
			fatal("Expected new line: y=%d", y);
	}
	if (x0 < 0 || y0 < 0)
		fatal("No start location");

	reverseops();
	orig_dirt = ndirt();
	if(strcmp(cost, "heavy") == 0)
	  cost_mod = 1;
	else
	  cost_mod = 0;
}

void Vacuum::reverseops() {
	unsigned int nrev = 0;
	for (unsigned int i = 0; i < map->nmvs; i++) {
	for (unsigned int j = 0; j < map->nmvs; j++) {
		if (map->mvs[i].dx != -map->mvs[j].dx || map->mvs[i].dy != -map->mvs[j].dy)
			continue;
		rev[i] = j;
		nrev++;
		break;
	} 
	}
	assert (nrev == map->nmvs);
}

Vacuum::State Vacuum::initialstate() const {
	State s;
	s.loc = map->index(x0, y0);
	s.ndirt = ndirt();
	s.dirt = std::make_shared<std::vector<bool> >(ndirt(), true);
	s.weight = 1;
	return s;
}

Vacuum::Cost Vacuum::pathcost(const std::vector<State> &path, const std::vector<Oper> &ops) {
	State state = initialstate();
	Cost cost(0);
	for (int i = ops.size() - 1; i >= 0; i--) {
		State copy(state);
		Edge e(*this, copy, ops[i]);
		assert (e.state.eq(this, path[i]));
		state = e.state;
		cost += e.cost;
	}
	assert (isgoal(state));
	return cost;
}

void Vacuum::printpath(FILE *out, const std::vector<Oper> &ops) const {
	for (int i = ops.size()-1; i >= 0; i--) {
		if (ops.at(i) <= 3)
			fprintf(out, "%s\n", map->mvs[ops.at(i)].name);
		else if (ops.at(i) == Suck)
			fprintf(out, "V\n");
		else if (ops.at(i) == Charge)
			fatal("Charge action!");
		else
			fatal("Unknown operator %d", ops[i]);
	}
}
