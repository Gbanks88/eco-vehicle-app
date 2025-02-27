# Core library CMake configuration
set(CORE_SOURCES
    src/Config.cpp
    src/Logger.cpp
    src/QABot.cpp
)

set(CORE_HEADERS
    include/Config.hpp
    include/Logger.hpp
    include/QABot.hpp
)

# Create core library
add_library(core STATIC
    ${CORE_SOURCES}
    ${CORE_HEADERS}
)

# Include directories
target_include_directories(core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Link Qt libraries
target_link_libraries(core
    PUBLIC
        Qt6::Core
        Qt6::Sql
    PRIVATE
        Qt6::Network
)

# Enable automoc for Qt
set_target_properties(core PROPERTIES
    AUTOMOC ON
    AUTORCC ON
    AUTOUIC ON
)

# Install headers
install(FILES ${CORE_HEADERS}
    DESTINATION include/core
    COMPONENT Development
)

# Install library
install(TARGETS core
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    COMPONENT Runtime
)
