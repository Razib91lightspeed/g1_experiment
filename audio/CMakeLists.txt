cmake_minimum_required(VERSION 3.16)
project(g1_speak LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SDK_DIR "$ENV{HOME}/Desktop/razib/unitree_sdk2_official")

set(SDK_LIB_DIR "${SDK_DIR}/lib/x86_64")
set(DDS_LIB_DIR "${SDK_DIR}/thirdparty/lib/x86_64")

find_package(Threads REQUIRED)

add_executable(g1_speak g1_speak.cpp)

target_include_directories(g1_speak PRIVATE
    "${SDK_DIR}/include"
    "${SDK_DIR}/thirdparty/include"
    "${SDK_DIR}/thirdparty/include/ddsc"
    "${SDK_DIR}/thirdparty/include/ddscxx"
)

target_link_libraries(g1_speak PRIVATE
    "${SDK_LIB_DIR}/libunitree_sdk2.a"
    "${DDS_LIB_DIR}/libddscxx.so"
    "${DDS_LIB_DIR}/libddsc.so"
    Threads::Threads
)

set_target_properties(g1_speak PROPERTIES
    BUILD_RPATH "${DDS_LIB_DIR}"
)
