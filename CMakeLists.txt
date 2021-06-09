cmake_minimum_required(VERSION 3.15)

project(
    money_bot
    LANGUAGES CXX)

# No weird extensions and use latest language
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)

# Different targets into differnt folders
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

# Useful CMake Modules
include(FetchContent)  # To download dependencies
include(CTest)         # To handle testing

# Add the dependencies
include(dependencies/CMakeLists.txt)

# Including the sources
include_directories(include)
add_subdirectory(src)

# Testing only available if this is the main app
# Emergency override MODERN_CMAKE_BUILD_TESTING provided as well
if(BUILD_TESTING)
  add_subdirectory(tests)
endif()
