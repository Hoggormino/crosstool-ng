// Owned C++/GNU-C ABI, branch, environment and special-value contracts.
#include <complex>
#include <algorithm>
#include <cmath>
#include <cfenv>
#include <cfloat>
#include <cstdio>
#include <limits>
#include <initializer_list>
#include <type_traits>
static int checks,failures;
static void check(const char* name,bool ok){++checks;if(!ok){++failures;std::printf("FAIL %s\n",name);}}
template<class T> bool signed_equal(T x,T y){return x==y&&(x!=0||std::signbit(x)==std::signbit(y));}
template<class T> bool close(T x,T y){return std::fabs(x-y)<=4*std::numeric_limits<T>::epsilon()*std::max(T(1),std::fabs(y));}
template<class T> void contracts(){
 using C=std::complex<T>;volatile T vz=0,vo=1,vt=std::numeric_limits<T>::min();T z=vz,o=vo,t=vt;
 const T pi2=T(1.57079632679489661923132169163975144L);
 for(T sy:{z,-z}){
  C a=std::acos(C(o,sy));check("acos endpoint",signed_equal(a.real(),z)&&signed_equal(a.imag(),-sy));
  a=std::acosh(C(o,sy));check("acosh endpoint",signed_equal(a.real(),z)&&signed_equal(a.imag(),sy));
  a=std::asin(C(T(2),sy));check("asin branch",close(a.real(),pi2)&&std::signbit(a.imag())==std::signbit(sy)&&a.imag()!=0);
  a=std::acos(C(T(2),sy));check("acos branch",signed_equal(a.real(),z)&&std::signbit(a.imag())!=std::signbit(sy)&&a.imag()!=0);
  a=std::acosh(C(T(-2),sy));check("acosh branch",a.real()>0&&close(std::fabs(a.imag()),2*pi2)&&std::signbit(a.imag())==std::signbit(sy));
  a=std::atanh(C(T(2),sy));check("atanh branch",a.real()>0&&close(std::fabs(a.imag()),pi2)&&std::signbit(a.imag())==std::signbit(sy));
 }
 for(int mode:{FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO}){
  std::fesetround(mode);std::feclearexcept(FE_ALL_EXCEPT);std::feraiseexcept(FE_DIVBYZERO);
  for(auto fn:{static_cast<C(*)(const C&)>(&std::asin<T>),static_cast<C(*)(const C&)>(&std::asinh<T>),static_cast<C(*)(const C&)>(&std::atan<T>),static_cast<C(*)(const C&)>(&std::atanh<T>)}){
   C a=fn(C(t,t));check("tiny components",signed_equal(a.real(),t)&&signed_equal(a.imag(),t));
   check("rounding restored",std::fegetround()==mode);check("incoming flags preserved",std::fetestexcept(FE_DIVBYZERO)!=0);
  }
 }
 std::fesetenv(FE_DFL_ENV);volatile T vl=T(1e10);C a=std::tan(C(vl,-vl));check("finite complex tan limit",std::isfinite(a.real())&&a.imag()==-o);
 a=std::tanh(C(vl,-vl));check("finite complex tanh limit",a.real()==o&&std::isfinite(a.imag()));
 volatile T inf=std::numeric_limits<T>::infinity(),nan=std::numeric_limits<T>::quiet_NaN();
 for(T sy:{z,-z}){
  std::feclearexcept(FE_ALL_EXCEPT);a=std::tanh(C(sy,inf));check("tanh zero infinity",signed_equal(a.real(),sy)&&std::isnan(a.imag()));check("tanh infinity invalid",std::fetestexcept(FE_INVALID)!=0);
  a=std::tanh(C(sy,nan));check("tanh zero NaN",signed_equal(a.real(),sy)&&std::isnan(a.imag()));
  a=std::tan(C(inf,sy));check("tan infinity zero",std::isnan(a.real())&&signed_equal(a.imag(),sy));
  a=std::tan(C(nan,sy));check("tan NaN zero",std::isnan(a.real())&&signed_equal(a.imag(),sy));
 }
 std::fesetenv(FE_DFL_ENV);
}
extern "C" __complex__ float owned_cacosf(__complex__ float) __asm__("cacosf");
static void call_cacosf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_cacosf;
  __complex__ float r=fn(z);
  check("C ABI acos",close(__real__ r,(float)1.57079632679489661923L)&&signed_equal(__imag__ r,-tiny));
}
extern "C" __complex__ float owned_cacoshf(__complex__ float) __asm__("cacoshf");
static void call_cacoshf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_cacoshf;
  __complex__ float r=fn(z);
  check("C ABI acosh",signed_equal(__real__ r,(float)tiny)&&close(__imag__ r,(float)1.57079632679489661923L));
}
extern "C" __complex__ float owned_casinf(__complex__ float) __asm__("casinf");
static void call_casinf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_casinf;
  __complex__ float r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(float)tiny)&&signed_equal(__imag__ r,(float)tiny));
}
extern "C" __complex__ float owned_casinhf(__complex__ float) __asm__("casinhf");
static void call_casinhf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_casinhf;
  __complex__ float r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(float)tiny)&&signed_equal(__imag__ r,(float)tiny));
}
extern "C" __complex__ float owned_catanf(__complex__ float) __asm__("catanf");
static void call_catanf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_catanf;
  __complex__ float r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(float)tiny)&&signed_equal(__imag__ r,(float)tiny));
}
extern "C" __complex__ float owned_catanhf(__complex__ float) __asm__("catanhf");
static void call_catanhf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_catanhf;
  __complex__ float r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(float)tiny)&&signed_equal(__imag__ r,(float)tiny));
}
extern "C" __complex__ float owned_ctanf(__complex__ float) __asm__("ctanf");
static void call_ctanf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_ctanf;
  __complex__ float r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(float)tiny)&&signed_equal(__imag__ r,(float)tiny));
}
extern "C" __complex__ float owned_ctanhf(__complex__ float) __asm__("ctanhf");
static void call_ctanhf() {
  volatile float tiny=std::numeric_limits<float>::min();
  __complex__ float z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ float (*volatile fn)(__complex__ float)=owned_ctanhf;
  __complex__ float r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(float)tiny)&&signed_equal(__imag__ r,(float)tiny));
}
extern "C" __complex__ double owned_cacos(__complex__ double) __asm__("cacos");
static void call_cacos() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_cacos;
  __complex__ double r=fn(z);
  check("C ABI acos",close(__real__ r,(double)1.57079632679489661923L)&&signed_equal(__imag__ r,-tiny));
}
extern "C" __complex__ double owned_cacosh(__complex__ double) __asm__("cacosh");
static void call_cacosh() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_cacosh;
  __complex__ double r=fn(z);
  check("C ABI acosh",signed_equal(__real__ r,(double)tiny)&&close(__imag__ r,(double)1.57079632679489661923L));
}
extern "C" __complex__ double owned_casin(__complex__ double) __asm__("casin");
static void call_casin() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_casin;
  __complex__ double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(double)tiny)&&signed_equal(__imag__ r,(double)tiny));
}
extern "C" __complex__ double owned_casinh(__complex__ double) __asm__("casinh");
static void call_casinh() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_casinh;
  __complex__ double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(double)tiny)&&signed_equal(__imag__ r,(double)tiny));
}
extern "C" __complex__ double owned_catan(__complex__ double) __asm__("catan");
static void call_catan() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_catan;
  __complex__ double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(double)tiny)&&signed_equal(__imag__ r,(double)tiny));
}
extern "C" __complex__ double owned_catanh(__complex__ double) __asm__("catanh");
static void call_catanh() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_catanh;
  __complex__ double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(double)tiny)&&signed_equal(__imag__ r,(double)tiny));
}
extern "C" __complex__ double owned_ctan(__complex__ double) __asm__("ctan");
static void call_ctan() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_ctan;
  __complex__ double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(double)tiny)&&signed_equal(__imag__ r,(double)tiny));
}
extern "C" __complex__ double owned_ctanh(__complex__ double) __asm__("ctanh");
static void call_ctanh() {
  volatile double tiny=std::numeric_limits<double>::min();
  __complex__ double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ double (*volatile fn)(__complex__ double)=owned_ctanh;
  __complex__ double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(double)tiny)&&signed_equal(__imag__ r,(double)tiny));
}
extern "C" __complex__ long double owned_cacosl(__complex__ long double) __asm__("cacosl");
static void call_cacosl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_cacosl;
  __complex__ long double r=fn(z);
  check("C ABI acos",close(__real__ r,(long double)1.57079632679489661923L)&&signed_equal(__imag__ r,-tiny));
}
extern "C" __complex__ long double owned_cacoshl(__complex__ long double) __asm__("cacoshl");
static void call_cacoshl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_cacoshl;
  __complex__ long double r=fn(z);
  check("C ABI acosh",signed_equal(__real__ r,(long double)tiny)&&close(__imag__ r,(long double)1.57079632679489661923L));
}
extern "C" __complex__ long double owned_casinl(__complex__ long double) __asm__("casinl");
static void call_casinl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_casinl;
  __complex__ long double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(long double)tiny)&&signed_equal(__imag__ r,(long double)tiny));
}
extern "C" __complex__ long double owned_casinhl(__complex__ long double) __asm__("casinhl");
static void call_casinhl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_casinhl;
  __complex__ long double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(long double)tiny)&&signed_equal(__imag__ r,(long double)tiny));
}
extern "C" __complex__ long double owned_catanl(__complex__ long double) __asm__("catanl");
static void call_catanl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_catanl;
  __complex__ long double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(long double)tiny)&&signed_equal(__imag__ r,(long double)tiny));
}
extern "C" __complex__ long double owned_catanhl(__complex__ long double) __asm__("catanhl");
static void call_catanhl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_catanhl;
  __complex__ long double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(long double)tiny)&&signed_equal(__imag__ r,(long double)tiny));
}
extern "C" __complex__ long double owned_ctanl(__complex__ long double) __asm__("ctanl");
static void call_ctanl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_ctanl;
  __complex__ long double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(long double)tiny)&&signed_equal(__imag__ r,(long double)tiny));
}
extern "C" __complex__ long double owned_ctanhl(__complex__ long double) __asm__("ctanhl");
static void call_ctanhl() {
  volatile long double tiny=std::numeric_limits<long double>::min();
  __complex__ long double z;__real__ z=tiny;__imag__ z=tiny;
  __complex__ long double (*volatile fn)(__complex__ long double)=owned_ctanhl;
  __complex__ long double r=fn(z);
  check("C ABI tiny",signed_equal(__real__ r,(long double)tiny)&&signed_equal(__imag__ r,(long double)tiny));
}
int main(){contracts<float>();contracts<double>();contracts<long double>();
call_cacosf();
call_cacoshf();
call_casinf();
call_casinhf();
call_catanf();
call_catanhf();
call_ctanf();
call_ctanhf();
call_cacos();
call_cacosh();
call_casin();
call_casinh();
call_catan();
call_catanh();
call_ctan();
call_ctanh();
call_cacosl();
call_cacoshl();
call_casinl();
call_casinhl();
call_catanl();
call_catanhl();
call_ctanl();
call_ctanhl();
std::printf("complex_contract_checks=%d failures=%d\n",checks,failures);return failures?1:0;}
