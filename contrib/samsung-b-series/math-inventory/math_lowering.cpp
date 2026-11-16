#include <cmath>
extern "C" long double sinl(long double);
extern "C" long double roundl(long double);
__attribute__((noinline)) long double cpp_sin(long double x) { return std::sin(x); }
__attribute__((noinline)) long double builtin_sin(long double x) { return __builtin_sinl(x); }
__attribute__((noinline)) long double declared_sin(long double x) { return sinl(x); }
__attribute__((noinline)) long double builtin_sqrt(long double x) { return __builtin_sqrtl(x); }
__attribute__((noinline)) long double builtin_round(long double x) { return __builtin_roundl(x); }
__attribute__((noinline)) long double declared_round(long double x) { return roundl(x); }
