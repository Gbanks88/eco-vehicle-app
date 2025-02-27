cmake_minimum_required(VERSION 3.16)
project(EcoVehicleMonitor VERSION 1.0.0 LANGUAGES CXX)

# Configure C++ standard and Qt features
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Enable optimization flags
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# Configure GPU acceleration
if(APPLE)
    message(STATUS "CUDA is not supported on macOS. Using Metal for GPU acceleration instead.")
    set(ENABLE_CUDA OFF)
    # Configure Metal framework
    find_library(METAL_LIBRARY Metal)
    find_library(METALKIT_LIBRARY MetalKit)
    if(METAL_LIBRARY AND METALKIT_LIBRARY)
        add_definitions(-DUSE_METAL)
        message(STATUS "Metal framework found")
    endif()
else()
    option(ENABLE_CUDA "Enable CUDA support" OFF)
    if(ENABLE_CUDA)
        message(STATUS "Checking for CUDA...")
        find_package(CUDA)
        if(CUDA_FOUND)
            enable_language(CUDA)
            set(CMAKE_CUDA_STANDARD 14)
            set(CMAKE_CUDA_STANDARD_REQUIRED ON)
            add_definitions(-DWITH_CUDA)
            message(STATUS "CUDA found: ${CUDA_VERSION}")
        else()
            message(WARNING "CUDA requested but not found")
        endif()
    endif()
endif()

# Find Qt packages
set(QT_VERSION_MAJOR 5)

# Required Qt components
set(QT_COMPONENTS
    Core
    Gui
    Widgets
    Network
    Concurrent
    OpenGL
    Sql
    Multimedia
    MultimediaWidgets
    Quick
)

# Find Qt and required components
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS ${QT_COMPONENTS})

# Optional Qt components
set(QT_OPTIONAL_COMPONENTS
    Charts
    3DCore
    3DRender
    3DInput
    3DExtras
    DataVisualization
    Designer
    UiTools
    Test
    QuickControls2
    Positioning
    Location
    Sensors
    SerialPort
    StateMachine
    WebSockets
)

# Try to find optional components
foreach(COMPONENT ${QT_OPTIONAL_COMPONENTS})
    find_package(Qt${QT_VERSION_MAJOR}${COMPONENT} QUIET)
endforeach()

# Find other packages
option(WITH_OPENCV "Enable OpenCV support" OFF)
if(WITH_OPENCV)
    find_package(OpenCV)
    if(OpenCV_FOUND)
        add_definitions(-DWITH_OPENCV)
        message(STATUS "OpenCV found: ${OpenCV_VERSION}")
    endif()
endif()
option(WITH_TORCH "Enable LibTorch support" OFF)
if(WITH_TORCH)
    find_package(Torch)
    if(Torch_FOUND)
        add_definitions(-DWITH_TORCH)
        message(STATUS "LibTorch found: ${Torch_VERSION}")
    endif()
endif()
find_package(Eigen3 REQUIRED)
find_package(Boost REQUIRED COMPONENTS system filesystem)
find_package(OpenSSL REQUIRED)
find_package(ZLIB REQUIRED)
option(WITH_PROTOBUF "Enable Protocol Buffers support" OFF)
if(WITH_PROTOBUF)
    find_package(Protobuf)
    if(Protobuf_FOUND)
        add_definitions(-DWITH_PROTOBUF)
        message(STATUS "Protobuf found: ${Protobuf_VERSION}")
    endif()
endif()

# Optional packages
option(WITH_VTK "Enable VTK support" OFF)
if(WITH_VTK)
    find_package(VTK)
    if(VTK_FOUND)
        add_definitions(-DWITH_VTK)
        message(STATUS "VTK found: ${VTK_VERSION}")
    endif()
endif()

option(WITH_PCL "Enable PCL support" OFF)
if(WITH_PCL)
    find_package(PCL)
    if(PCL_FOUND)
        add_definitions(-DWITH_PCL)
        message(STATUS "PCL found: ${PCL_VERSION}")
    endif()
endif()

option(WITH_OPENVINO "Enable OpenVINO support" OFF)
if(WITH_OPENVINO)
    find_package(OpenVINO)
    if(OpenVINO_FOUND)
        add_definitions(-DWITH_OPENVINO)
        message(STATUS "OpenVINO found: ${OpenVINO_VERSION}")
    endif()
endif()

# Autodesk packages
set(AUTODESK_SDK_ROOT "$ENV{AUTODESK_SDK_ROOT}" CACHE PATH "Path to Autodesk SDK root")
set(FUSION360_SDK_ROOT "$ENV{FUSION360_SDK_ROOT}" CACHE PATH "Path to Fusion 360 SDK root")

# Verify SDK paths
if(NOT EXISTS ${AUTODESK_SDK_ROOT})
    message(WARNING "Autodesk SDK root not found at ${AUTODESK_SDK_ROOT}")
    set(AUTODESK_SDK_FOUND FALSE)
else()
    set(AUTODESK_SDK_FOUND TRUE)
endif()

if(NOT EXISTS ${FUSION360_SDK_ROOT})
    message(WARNING "Fusion360 SDK root not found at ${FUSION360_SDK_ROOT}")
    set(FUSION360_SDK_FOUND FALSE)
else()
    set(FUSION360_SDK_FOUND TRUE)
endif()

# Handle Qt version
if(NOT Qt${QT_VERSION_MAJOR}_FOUND)
    message(WARNING "Qt${QT_VERSION_MAJOR} not found, trying Qt5")
    set(QT_VERSION_MAJOR 5)
    find_package(Qt${QT_VERSION_MAJOR} REQUIRED)
endif()

# Add LinguistTools for translations
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS LinguistTools)

# Find Autodesk Platform Services (APS) SDK
find_path(APS_INCLUDE_DIR
    NAMES aps/auth/OAuth.h
    PATHS ${AUTODESK_SDK_ROOT}/include
    DOC "APS include directory"
)

find_library(APS_LIBRARY
    NAMES aps_sdk
    PATHS ${AUTODESK_SDK_ROOT}/lib
    DOC "APS library"
)

# Find Fusion 360 SDK
find_path(FUSION360_INCLUDE_DIR
    NAMES adsk/core/Application.h
    PATHS ${FUSION360_SDK_ROOT}/include
    DOC "Fusion 360 include directory"
)

find_library(FUSION360_LIBRARY
    NAMES fusion360_api
    PATHS ${FUSION360_SDK_ROOT}/lib
    DOC "Fusion 360 library"
)

# Package handling
if(APS_INCLUDE_DIR AND APS_LIBRARY)
    set(APS_FOUND TRUE)
    message(STATUS "Found Autodesk Platform Services SDK")
else()
    set(APS_FOUND FALSE)
    message(WARNING "Autodesk Platform Services SDK not found")
endif()

if(FUSION360_INCLUDE_DIR AND FUSION360_LIBRARY)
    set(FUSION360_FOUND TRUE)
    message(STATUS "Found Fusion 360 SDK")
else()
    set(FUSION360_FOUND FALSE)
    message(WARNING "Fusion 360 SDK not found")
endif()

# Configure translations
set(TS_FILES
    resources/i18n/app_en.ts
    resources/i18n/app_es.ts
    resources/i18n/app_fr.ts
    resources/i18n/app_de.ts
    resources/i18n/app_ja.ts
    resources/i18n/app_zh.ts
)

# Create commands to generate QM files
if(${QT_VERSION_MAJOR} EQUAL 6)
    qt6_create_translation(QM_FILES ${CMAKE_SOURCE_DIR}/src ${TS_FILES})
else()
    qt5_create_translation(QM_FILES ${CMAKE_SOURCE_DIR}/src ${TS_FILES})
endif()

# Add subdirectories
add_subdirectory(src)

# Configure resources
qt_add_resources(RESOURCES
    resources/resources.qrc
)

# Main executable
add_executable(${PROJECT_NAME} 
    src/main.cpp
    ${RESOURCES}
)

# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Gui
    Qt${QT_VERSION_MAJOR}::Widgets

    # Metal framework on macOS
    $<$<PLATFORM_ID:Darwin>:${METAL_LIBRARY}>
    $<$<PLATFORM_ID:Darwin>:${METALKIT_LIBRARY}>
    Qt${QT_VERSION_MAJOR}::Network
    Qt${QT_VERSION_MAJOR}::Concurrent
    Qt${QT_VERSION_MAJOR}::OpenGL
    Qt${QT_VERSION_MAJOR}::Sql
    Qt${QT_VERSION_MAJOR}::Multimedia
    Qt${QT_VERSION_MAJOR}::MultimediaWidgets
    Qt${QT_VERSION_MAJOR}::Quick
    Qt6::Network
    Qt6::Concurrent
    Qt6::OpenGL
    Qt6::3DCore
    Qt6::3DRender
    Qt6::3DInput
    Qt6::3DExtras
    Qt6::DataVisualization
    Qt6::Designer
    Qt6::UiTools
    monitoring
    visualization
    core
)

# Install rules
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
