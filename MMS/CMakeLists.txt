cmake_minimum_required(VERSION 3.18)

project(MMS LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find the Python installation inside the container.
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

# Locate pybind11 through the active Python installation.
execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE PYBIND11_RESULT
)

if(NOT PYBIND11_RESULT EQUAL 0)
    message(FATAL_ERROR "Could not locate pybind11")
endif()

find_package(pybind11 CONFIG REQUIRED)

# Build the Python extension.
pybind11_add_module(_core
    bindings.cpp
    AdditiveMMSSolver.cpp
)

target_compile_options(_core PRIVATE -O3)

# Place the extension inside the MMS Python package.
set_target_properties(_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
)
