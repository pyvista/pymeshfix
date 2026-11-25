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

  # Split mode (runtime from nanobind-backend) allows abi3 below 3.12 and abi3t
  STABLE_ABI
  FREE_THREADED
  BACKEND_MODULE nanobind_backend

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
  src/orientation.c
  src/point.cpp
  src/tin.cpp
  src/tmesh.cpp
  src/triangle.cpp
  src/vertex.cpp

)

# Compiler-specific options
if(MSVC)
  # Use MSVC optimization levels and OpenMP setup
  target_compile_options(_meshfix PRIVATE /O2 /std:c++17)
else()
  # Assuming GCC or Clang
  target_compile_options(_meshfix PRIVATE -O3)
endif()

# Install directive for scikit-build-core
install(TARGETS _meshfix LIBRARY DESTINATION pymeshfix)
