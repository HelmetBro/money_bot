# RapidJson for reading json data
set (CMAKE_COMPILE_OPTIONS "-Wpedantic;-Wall;-Wextra")
set (RAPIDJSON_BUILD_DOC  OFF CACHE INTERNAL "Turn off tests")
set (RAPIDJSON_BUILD_EXAMPLES OFF CACHE INTERNAL "Turn off tests")
set (RAPIDJSON_BUILD_TESTS  OFF CACHE INTERNAL "Turn off tests")
set (RAPIDJSON_BUILD_THIRDPARTY_GTEST OFF CACHE INTERNAL "Turn off tests")
FetchContent_Declare(
  rapidjson
  GIT_REPOSITORY https://github.com/Tencent/rapidjson.git
  GIT_TAG        v1.1.0
)

# This is a header only library, should be exposed via include directories
FetchContent_MakeAvailable(rapidjson)

# spdlog for logging
FetchContent_Declare(
    spdlog
  GIT_REPOSITORY https://github.com/gabime/spdlog.git
  GIT_TAG        v1.8.5
)

FetchContent_MakeAvailable(spdlog)