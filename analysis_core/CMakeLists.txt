cmake_minimum_required (VERSION 2.6)

project (analysis_core)

find_package(Threads REQUIRED)

set(CMAKE_CXX_FLAGS "-O2 -pthread -Wall -Wextra -Wno-unused-variable")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(analysis_core main.cpp)
target_link_libraries(analysis_core stdc++fs)
target_link_libraries(analysis_core boost_program_options)
