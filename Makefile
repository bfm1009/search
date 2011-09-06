CXX=g++
FLAGS=-Wall -Werror -g -pg
CXXFLAGS=$(FLAGS)
CFLAGS=$(FLAGS)

OBJS=\
	utils/fatal.o\
	utils/time.o\
	utils/datafile.o\
	utils/testing.o\
	utils/hash.o\
	utils/rand.o\

TMPLS=\
	search/openlist.hpp\
	search/idastar.hpp\
	search/astar.hpp\
	\
	structs/intpq.hpp\
	structs/binheap.hpp\
	structs/htable.hpp\

HDRS=\
	incl/utils.hpp\
	incl/search.hpp\

HDRS+=$(TMPLS)

BINS=

all: everything

include structs/Make.inc
include utils/Make.inc
include tiles/Make.inc

everything: $(TMPLS:.hpp=.hpp.gch) $(BINS)

%.hpp.gch: %.hpp
	$(CXX) $(CXXFLAGS) -c $^

clean:
	rm -f $(OBJS) $(BINS) $(TMPLS:.hpp=.hpp.gch)