cmake_minimum_required(VERSION 3.15)
project(pylibde265 LANGUAGES C CXX)

# Find Python and pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 REQUIRED)

# libde265 configuration
set(ENABLE_ENCODER OFF CACHE BOOL "Enable libde265 encoder")
set(ENABLE_DECODER ON CACHE BOOL "Enable libde265 decoder")
set(ENABLE_SDL OFF CACHE BOOL "Enable libde265 SDL")
set(BUILD_SHARED_LIBS OFF CACHE BOOL "Build static libde265 for embedding")

# Add libde265 subdirectory
add_subdirectory(libde265)

# Find NumPy include path
execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import numpy; print(numpy.get_include(), end='')"
    OUTPUT_VARIABLE NUMPY_INCLUDE_PATH
    RESULT_VARIABLE NUMPY_STATUS
)

if(NOT NUMPY_STATUS EQUAL 0)
    message(FATAL_ERROR "Could not find numpy include path")
endif()

# _de265 extension
pybind11_add_module(_de265 src/pylibde265/de265_pybind.cpp)
target_link_libraries(_de265 PRIVATE de265)
target_compile_definitions(_de265 PRIVATE LIBDE265_STATIC_BUILD)
target_include_directories(_de265 PRIVATE 
    ${NUMPY_INCLUDE_PATH}
    ${PROJECT_SOURCE_DIR}/libde265
    ${PROJECT_SOURCE_DIR}/libde265/libde265
    ${PROJECT_BINARY_DIR}/libde265  # for generated libde265/de265-version.h
)
# Ensure the de265 target can also see the generated header correctly
target_include_directories(de265 PRIVATE ${PROJECT_BINARY_DIR}/libde265)

# _visualize extension
pybind11_add_module(_visualize src/pylibde265/visualize_pybind.cpp)
target_link_libraries(_visualize PRIVATE de265)
target_compile_definitions(_visualize PRIVATE LIBDE265_STATIC_BUILD)
target_include_directories(_visualize PRIVATE 
    ${NUMPY_INCLUDE_PATH}
    ${PROJECT_SOURCE_DIR}/libde265
    ${PROJECT_SOURCE_DIR}/libde265/libde265
    ${PROJECT_BINARY_DIR}/libde265  # for generated de265-version.h
)

if(MSVC)
    target_compile_options(_de265 PRIVATE /openmp)
    target_compile_options(_visualize PRIVATE /openmp)
else()
    find_package(OpenMP)
    if(OpenMP_FOUND)
        target_link_libraries(_de265 PRIVATE OpenMP::OpenMP_CXX)
        target_link_libraries(_visualize PRIVATE OpenMP::OpenMP_CXX)
    endif()
endif()

# Install to the package directory
install(TARGETS _de265 _visualize DESTINATION pylibde265)
