add_library(analysis STATIC
    # Add source files here
)

target_include_directories(analysis PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(analysis PRIVATE
    core
    Qt${QT_VERSION_MAJOR}::Core
)
