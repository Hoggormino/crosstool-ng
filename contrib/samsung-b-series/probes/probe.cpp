#include <atomic>
#include "probe_types.h"
#include <cassert>
#include <cstdio>
#include <optional>
#include <pthread.h>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <tuple>
#include <variant>
#include <vector>
#include <unistd.h>
static std::atomic<unsigned> dtors{0}, initializations{0}, unwinds{0};
struct Local { Local() { ++initializations; usleep(20000); } unsigned value = 42; };
static Local& local() { static Local x; return x; }
struct TLS { unsigned value = 0; ~TLS() { ++dtors; } };
thread_local TLS tls;
constexpr int fib(int n) { return n < 2 ? n : fib(n-1)+fib(n-2); }
static_assert(fib(10) == 55);
struct Cleanup { ~Cleanup() { ++unwinds; } };
__attribute__((noinline)) static void throw_owned() {
    Cleanup cleanup;
    std::vector<std::string> temporary(32, "unwind allocation");
    throw std::runtime_error("owned exception");
}
static void *worker(void *) {
    assert(local().value == 42); tls.value = 19;
    return reinterpret_cast<void *>(static_cast<unsigned long>(tls.value));
}
int main() {
    std::optional<std::string> s{std::string("modern")};
    std::variant<int,std::string> v{*s};
    std::string_view view{std::get<std::string>(v)}; assert(view == "modern");
    auto [x,y] = std::make_tuple(17,25); assert(x+y == 42);
    std::vector<std::string> values(128,std::string(256, 'x')); assert(values.back().size()==256);
    Child child; Base plain; assert(owned_dynamic_cast(&child)->value==17); assert(owned_dynamic_cast(&plain)==nullptr);
    try { throw_owned(); }
    catch(const std::exception& e) { assert(std::string_view(e.what())=="owned exception"); }
    assert(unwinds.load()==1);
    pthread_t a,b; assert(!pthread_create(&a,nullptr,worker,nullptr)); assert(!pthread_create(&b,nullptr,worker,nullptr));
    void *result=nullptr; assert(!pthread_join(a,&result)); assert(result==reinterpret_cast<void*>(19));
    assert(!pthread_join(b,&result)); assert(dtors.load()==2); assert(initializations.load()==1);
    std::thread c([]{ assert(local().value==42); tls.value=7; }); c.join(); assert(dtors.load()==3);
    std::atomic<unsigned> u{5}; assert(u.fetch_add(7)==5); assert(u.load()==12);
    unsigned expect=12; assert(u.compare_exchange_strong(expect,42));
    printf("C++17/STL/EH/RTTI/pthread/static/TLS-dtor/atomic32 passed; lock_free32=%d string_size=%u mutex_size=%u\n", u.is_lock_free(), (unsigned)sizeof(std::string), (unsigned)sizeof(pthread_mutex_t));
}
