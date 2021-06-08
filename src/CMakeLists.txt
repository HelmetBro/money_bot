add_library(money_bot STATIC money.cpp)
target_link_libraries(money_bot spdlog)

add_executable(money_bot_driver main.cpp)
target_link_libraries(money_bot_driver spdlog money_bot)
