# Add libraries
add_subdirectory(core)
add_subdirectory(analysis)
add_subdirectory(autodesk)
add_subdirectory(design)
add_subdirectory(fusion360)
add_subdirectory(gui)
add_subdirectory(modeling)
add_subdirectory(monitoring)
add_subdirectory(repository)
add_subdirectory(requirements)
add_subdirectory(visualization)

# Create main library
add_library(app_lib STATIC
    main.cpp
)

target_link_libraries(app_lib PRIVATE
    core
    monitoring
    visualization
    ui
)
