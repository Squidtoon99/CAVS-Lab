cmake_minimum_required(VERSION 3.16)
project(vehicle_monorepo VERSION 1.0.0 LANGUAGES C CXX)

if(PROJECT_SOURCE_DIR STREQUAL PROJECT_BINARY_DIR)
  message(FATAL_ERROR
    "\nIn-source builds are forbidden!"
    "\nPlease create a build directory and run CMake from there, e.g.:"
    "\n  mkdir build && cd build && cmake .."
  )
endif()

set(CMAKE_CXX_STANDARD 17)
SET(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_compile_options(-Wall -Wextra)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(BUILD_ARM "Build for ARM target architecture (Raspberry PI)" OFF)
option(BUILD_SIMULATION "Build components in simulation mode" OFF)
option(BUILD_TESTING "Build monorepo test suites" OFF)

message(STATUS "--- Monorepo Configuration ---")
message(STATUS "BUILD_ARM:        ${BUILD_ARM}")
message(STATUS "BUILD_SIMULATION: ${BUILD_SIMULATION}")
message(STATUS "BUILD_TESTING:    ${BUILD_TESTING}")
message(STATUS "------------------------------")

if(NOT BUILD_ARM)
    find_package(fastcdr REQUIRED)
    find_package(foonathan_memory REQUIRED)
    find_package(fastdds REQUIRED)
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cpm_lib/CMakeLists.txt")
    add_subdirectory(cpm_lib)
endif()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/mid_level_controller/CMakeLists.txt")
    add_subdirectory(mid_level_controller)
endif()

