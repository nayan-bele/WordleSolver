# Makefile — Simple alternative to CMake (no cmake required)
# Usage:
#   make           # Build everything
#   make test      # Build + run unit tests
#   make clean     # Remove binaries

CXX      = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra

# Shared sources
COMMON = src/feedback.cpp src/solver.cpp

# -----------------------------------------------------------------------
# Targets
# -----------------------------------------------------------------------
.PHONY: all test clean

all: benchmark wordle_cli test_feedback

benchmark: src/benchmark.cpp $(COMMON)
	$(CXX) $(CXXFLAGS) -o benchmark src/benchmark.cpp $(COMMON)

wordle_cli: src/cli.cpp $(COMMON)
	$(CXX) $(CXXFLAGS) -o wordle_cli src/cli.cpp $(COMMON)

test_feedback: tests/test_feedback.cpp src/feedback.cpp
	$(CXX) $(CXXFLAGS) -I. -o test_feedback tests/test_feedback.cpp src/feedback.cpp

test: test_feedback
	@echo "\nRunning unit tests..."
	@./test_feedback

clean:
	rm -f benchmark wordle_cli test_feedback
