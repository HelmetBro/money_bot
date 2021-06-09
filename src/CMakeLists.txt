# Build the Moneybot library
add_library(money_bot STATIC money.cpp)
target_link_libraries(money_bot PUBLIC spdlog)
target_include_directories(money_bot PUBLIC "${rapidjson_SOURCE_DIR}/include")

message(STATUS "${rapidjson_SOURCE_DIR}/include")

# Build the moneybot driver
add_executable(money_bot_driver main.cpp)
target_link_libraries(money_bot_driver spdlog money_bot)
