add_library(autodesk STATIC
    # Add source files here
)

target_include_directories(autodesk PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${APS_INCLUDE_DIR}
)

target_link_libraries(autodesk PRIVATE
    core
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Network
)
