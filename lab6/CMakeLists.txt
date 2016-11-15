cmake_minimum_required(VERSION 3.6)
project(lab6)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES main.c queue.c queue.h linkedlist.c linkedlist.h wsqueue.c wsqueue.h squeue.c squeue.h thread_pool.c thread_pool.h)
add_executable(lab6 ${SOURCE_FILES})