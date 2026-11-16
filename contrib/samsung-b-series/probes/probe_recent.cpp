#include <atomic>
#include <bit>
#include <chrono>
#include <concepts>
#include <cstdio>
#include <expected>
#include <ranges>
#include <semaphore>
#include <span>
#include <thread>
#include <vector>
static void require(bool value) { if (!value) __builtin_abort(); }
template<std::integral T> constexpr T twice(T x) { return x+x; }
static_assert(twice(21)==42);
static_assert(std::popcount(0xffu)==8);
int main() {
    int data[]={1,2,3,4};std::span<int> values(data);int sum=0;
    for (int x:values|std::views::filter([](int x){return x%2==0;})|std::views::transform([](int x){return x*2;})) sum+=x;
    require(sum==12);std::expected<int,int> e=42;require(e.has_value()&&*e==42);
    std::atomic<int> state{0};std::thread t([&]{std::this_thread::sleep_for(std::chrono::milliseconds(15));state.store(1);state.notify_one();});
    state.wait(0);require(state.load()==1);t.join();
    std::counting_semaphore<1> sem(0);require(!sem.try_acquire_for(std::chrono::milliseconds(15)));
    std::thread u([&]{std::this_thread::sleep_for(std::chrono::milliseconds(10));sem.release();});
    require(sem.try_acquire_for(std::chrono::seconds(1)));u.join();
    std::puts("C++20/23 concepts/span/ranges/expected/atomic-wait/timed-semaphore passed");
}
