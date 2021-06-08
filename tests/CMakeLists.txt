# Use Google Test for testing
FetchContent_Declare(
    doctest
  GIT_REPOSITORY https://github.com/onqtam/doctest.git
  GIT_TAG        2.4.6
)
FetchContent_MakeAvailable(doctest)

# Add testing sources
add_executable(test_foo test_foo.cpp)
target_link_libraries(test_foo doctest spdlog money_bot)
add_test(test_foo test_foo)