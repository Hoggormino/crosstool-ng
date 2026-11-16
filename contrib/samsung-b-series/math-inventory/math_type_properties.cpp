#include <limits>
#include <type_traits>
static_assert(sizeof(double)==8 && sizeof(long double)==8, "size");
static_assert(alignof(double)==alignof(long double), "alignment");
static_assert(std::numeric_limits<double>::radix==2 && std::numeric_limits<long double>::radix==2, "radix");
static_assert(std::numeric_limits<double>::digits==53 && std::numeric_limits<long double>::digits==53, "precision");
static_assert(std::numeric_limits<double>::min_exponent==-1021 && std::numeric_limits<long double>::min_exponent==-1021, "min exponent");
static_assert(std::numeric_limits<double>::max_exponent==1024 && std::numeric_limits<long double>::max_exponent==1024, "max exponent");
static_assert(std::numeric_limits<double>::is_iec559 && std::numeric_limits<long double>::is_iec559, "IEEE 754");
static_assert(!std::is_same<double,long double>::value, "distinct C++ types");
