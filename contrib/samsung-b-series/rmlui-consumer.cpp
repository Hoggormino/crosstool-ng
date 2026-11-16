#include <RmlUi/Core.h>
#include <cassert>
#include <cstdio>
struct System final : Rml::SystemInterface {
    double GetElapsedTime() override { return 0.0; }
    bool LogMessage(Rml::Log::Type, const Rml::String&) override { return true; }
};
int main() {
    System system;
    Rml::FontEngineInterface font;
    Rml::SetFontEngineInterface(&font);
    Rml::SetSystemInterface(&system);
    if (!Rml::Initialise()) { std::fputs("RmlUi initialization failed\n", stderr); return 1; }
    auto value = Rml::Variant(42);
    if (value.Get<int>() != 42) return 2;
    Rml::Shutdown();
    puts("RmlUi Core initialize/Variant/shutdown passed");
}
