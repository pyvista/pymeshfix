cmake_minimum_required(VERSION 3.15...3.26)

project(nanobind_project LANGUAGES C CXX)
# find_package(OpenMP REQUIRED)

# Try to import all Python components potentially needed by nanobind
find_package(Python 3.10
  REQUIRED COMPONENTS Interpreter Development.Module
  OPTIONAL_COMPONENTS Development.SABIModule)

# Import nanobind through CMake's find_package mechanism
find_package(nanobind CONFIG REQUIRED)

nanobind_add_module(
  # Name of the extension
  _meshfix

  # Target the stable ABI for Python 3.12+, which reduces
  # the number of binary wheels that must be built. This
  # does nothing on older Python versions
  STABLE_ABI

  # conserve space by reusing a shared libnanobind across libraries (necessary here?)
  NB_STATIC

  src/_meshfix.cpp
  src/checkAndRepair.cpp
  src/coordinates.cpp
  src/detectIntersections.cpp
  src/edge.cpp
  src/graph.cpp
  src/heap.cpp
  src/holeFilling.cpp
  src/io.cpp
  src/jqsort.cpp
  src/list.cpp
  src/marchIntersections.cpp
  src/matrix.cpp
  src/meshfix.cpp
  src/orientation.c
  src/point.cpp
  src/tin.cpp
  src/tmesh.cpp
  src/triangle.cpp
  src/vertex.cpp

)

# Link OpenMP
# if(OpenMP_CXX_FOUND)
#   target_link_libraries(_meshfix PRIVATE OpenMP::OpenMP_CXX)
# endif()

# Compiler-specific options
if(MSVC)
  # Use MSVC optimization levels and OpenMP setup
  target_compile_options(_meshfix PRIVATE /O2 /std:c++17)
  # /openmp:llvm
else()
  # Assuming GCC or Clang
  target_compile_options(_meshfix PRIVATE -O3)
  # -fopenmp
endif()

# Install directive for scikit-build-core
install(TARGETS _meshfix LIBRARY DESTINATION pymeshfix)
