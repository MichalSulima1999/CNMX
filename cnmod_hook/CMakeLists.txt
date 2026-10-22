cmake_minimum_required(VERSION 3.16)
project(cnmod_hook VERSION 1.0.0 LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# MinHook (z .tools - to samo zrodlo co EtapC.dll)
set(MH_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../.tools/minhook-master")

add_library(cnmod_hook SHARED
    src/main.cpp
    ${MH_DIR}/src/buffer.c
    ${MH_DIR}/src/hook.c
    ${MH_DIR}/src/trampoline.c
    ${MH_DIR}/src/hde/hde32.c
    ${MH_DIR}/src/hde/hde64.c
)

target_include_directories(cnmod_hook PRIVATE include ${MH_DIR}/include ${MH_DIR}/src)

if(MSVC)
    target_compile_options(cnmod_hook PRIVATE /EHsc /W3 /DNDEBUG)
else()
    target_compile_options(cnmod_hook PRIVATE -O2 -DNDEBUG)
    target_link_options(cnmod_hook PRIVATE -static -s)
endif()

# Tylko x86 (gra jest 32-bitowa)
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(WARNING "cnmod_hook musi byc zbudowany jako 32-bit (x86)!")
endif()

set_target_properties(cnmod_hook PROPERTIES
    OUTPUT_NAME "cnmod_hook"
)
