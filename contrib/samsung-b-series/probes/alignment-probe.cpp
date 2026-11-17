// Exercise byte-aligned copies and the runtime helpers that promise unaligned I/O.
#include <cstdio>
#include <cstring>
#include <locale>

extern "C" int __aeabi_uread4(void*);
extern "C" int __aeabi_uwrite4(int, void*);
extern "C" long long __aeabi_uread8(void*);
extern "C" long long __aeabi_uwrite8(long long, void*);

int main()
{
    alignas(8) unsigned char source[64], destination[64];
    for (unsigned i = 0; i < sizeof(source); ++i) source[i] = i * 3 + 1;
    for (unsigned offset = 0; offset < 8; ++offset) {
        std::memset(destination, 0, sizeof(destination));
        if (__aeabi_uwrite4(0x12345678, destination + offset) != 0x12345678 ||
            __aeabi_uread4(destination + offset) != 0x12345678) return 1;
        const long long value = 0x123456789abcdefLL;
        if (__aeabi_uwrite8(value, destination + offset) != value ||
            __aeabi_uread8(destination + offset) != value) return 2;
        for (unsigned other = 0; other < 8; ++other) {
            for (unsigned length = 0; length <= 40; ++length) {
                std::memset(destination, 0, sizeof(destination));
                std::memcpy(destination + other, source + offset, length);
                if (std::memcmp(destination + other, source + offset, length)) return 3;
            }
        }
    }
    const auto& facet = std::use_facet<std::moneypunct<char>>(std::locale::classic());
    const auto positive = facet.pos_format(), negative = facet.neg_format();
    const char expected[] = {std::money_base::symbol, std::money_base::sign,
                             std::money_base::none, std::money_base::value};
    if (std::memcmp(positive.field, expected, 4) || std::memcmp(negative.field, expected, 4)) return 4;
    std::puts("PASS unaligned EABI helpers offsets 0..7; 2624 memcpy cases; classic monetary patterns");
}
