cmake_minimum_required(VERSION 3.15)
project(eco_vehicle_project VERSION 1.0.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Find required packages
find_package(Threads REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(Boost COMPONENTS system filesystem REQUIRED)
find_package(nlohmann_json 3.2.0 REQUIRED)

# Include directories
include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
    ${Python3_INCLUDE_DIRS}
)

# Add subdirectories
add_subdirectory(src)

# Main components
add_library(eco_vehicle_core STATIC
    src/environmental/air_processing.cpp
    src/automation/automation_bot.cpp
    src/circuit/CircuitAnalyzer.cpp
    src/circuit/CircuitVisualizer.cpp
    src/monitoring/system_monitor.cpp
    src/analysis/survey_analyzer.cpp
)

# Python bindings
add_library(eco_vehicle_python SHARED
    src/automation/automation_bindings.cpp
)

target_link_libraries(eco_vehicle_python
    PRIVATE
    eco_vehicle_core
    ${Python3_LIBRARIES}
)

# Main executable
add_executable(eco_vehicle src/main.cpp)

# Link libraries
target_link_libraries(eco_vehicle
    PRIVATE
    eco_vehicle_core
    Threads::Threads
)

# Installation
install(TARGETS eco_vehicle eco_vehicle_core eco_vehicle_python
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

# Testing
enable_testing()
add_subdirectory(tests)

