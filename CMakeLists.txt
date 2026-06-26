cmake_minimum_required(VERSION 3.14)
project(WordleSolver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build in Release mode by default for max speed
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O2")
set(CMAKE_CXX_FLAGS_DEBUG   "-g -O0 -Wall -Wextra")

# Shared object files compiled into every binary
set(COMMON_SOURCES
    src/feedback.cpp
    src/solver.cpp
)

# -----------------------------------------------------------------------
# Targets
# -----------------------------------------------------------------------

# Benchmark — run both solvers on all answers
add_executable(benchmark src/benchmark.cpp ${COMMON_SOURCES})

# Interactive CLI assistant
add_executable(wordle_cli src/cli.cpp ${COMMON_SOURCES})

# Unit tests (only needs feedback.cpp)
add_executable(test_feedback tests/test_feedback.cpp src/feedback.cpp)

# -----------------------------------------------------------------------
# Custom 'test' target to run tests after building
# -----------------------------------------------------------------------
add_custom_target(run_tests
    COMMAND test_feedback
    DEPENDS test_feedback
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMENT "Running unit tests..."
)
