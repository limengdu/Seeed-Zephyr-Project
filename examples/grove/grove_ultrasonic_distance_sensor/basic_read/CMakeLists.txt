cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(grove_ultrasonic_basic_read)

set(GROVE_COMMON_DIR ${CMAKE_CURRENT_LIST_DIR}/../../common)
if(NOT EXISTS ${GROVE_COMMON_DIR})
  set(GROVE_COMMON_DIR ${CMAKE_CURRENT_LIST_DIR}/common)
endif()

target_sources(app PRIVATE
  src/main.c
  ${GROVE_COMMON_DIR}/xiao_board_runtime.c
)
target_include_directories(app PRIVATE ${GROVE_COMMON_DIR})
