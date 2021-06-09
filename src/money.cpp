/*
using this to test wrappers and stuff. feel free to add a bunch of crap here
*/

#include "money_bot/money_bot.h"

#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

int foo()
{
    const char* json = "{\"test\":2}";
    rapidjson::Document d;
    d.Parse(json);

    // 2. Modify it by DOM.
    rapidjson::Value& s = d["test"];
    return s.GetInt();
}
