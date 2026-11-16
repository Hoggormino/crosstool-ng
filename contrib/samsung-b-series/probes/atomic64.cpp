#include <atomic>
#include <cassert>
#include <cstdio>
#include <cstdint>
int main() {
    std::atomic<std::uint64_t> a{0x100000000ull};
    assert(a.fetch_add(7)==0x100000000ull); assert(a.load()==0x100000007ull);
    std::uint64_t expected=0x100000007ull;
    assert(a.compare_exchange_strong(expected,0x200000000ull));
    printf("atomic64 operations passed in QEMU; is_lock_free=%d\n", a.is_lock_free());
}
