// Owned entry-point, exception and environment checks. No TV operations.
#include <cmath>
#include <cfenv>
#include <cfloat>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <limits>
#include <initializer_list>
static int failures,checks;
static void check(const char* name,bool pass){++checks;if(!pass){++failures;std::printf("FAIL %s\n",name);}}
template<class T> static bool equal(T a,T b){return a==b && (a!=0 || std::signbit(a)==std::signbit(b));}
static double from_bits(uint64_t u){double x;std::memcpy(&x,&u,8);return x;}
static float from_bits32(uint32_t u){float x;std::memcpy(&x,&u,4);return x;}
int main(){
 static_assert(sizeof(double)==sizeof(long double) && DBL_MANT_DIG==LDBL_MANT_DIG,"binary64");
 volatile double x=1.+0x1p-27,y=1.-0x1p-27,z=-1.;
 volatile float xf=1.f+0x1p-13f,yf=1.f-0x1p-13f,zf=-1.f;
 volatile long double xl=x,yl=y,zl=z;
 double(*volatile fd)(double,double,double)=::fma;
 float(*volatile ff)(float,float,float)=::fmaf;
 long double(*volatile fl)(long double,long double,long double)=::fmal;
 check("std fma double",equal(std::fma(x,y,z),-0x1p-54));
 check("std fma float",equal(std::fma(xf,yf,zf),-0x1p-26f));
 check("std fma long double",equal(std::fma(xl,yl,zl),-0x1p-54L));
 check("global fma",equal(::fma(x,y,z),-0x1p-54));
 check("global fmaf",equal(::fmaf(xf,yf,zf),-0x1p-26f));
 check("global fmal",equal(::fmal(xl,yl,zl),-0x1p-54L));
 check("builtin fma",equal(__builtin_fma(x,y,z),-0x1p-54));
 check("builtin fmaf",equal(__builtin_fmaf(xf,yf,zf),-0x1p-26f));
 check("builtin fmal",equal(__builtin_fmal(xl,yl,zl),-0x1p-54L));
 check("pointer fma",equal(fd(x,y,z),-0x1p-54));
 check("pointer fmaf",equal(ff(xf,yf,zf),-0x1p-26f));
 check("pointer fmal",equal(fl(xl,yl,zl),-0x1p-54L));
 for(int mode:{FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO}){
  std::fesetenv(FE_DFL_ENV);std::fesetround(mode);
  volatile double max=DBL_MAX,two=2.;std::feclearexcept(FE_ALL_EXCEPT);
  check("no intermediate overflow",equal(fd(max,two,-max),DBL_MAX));
  check("exact fused flags",std::fetestexcept(FE_ALL_EXCEPT)==0);
  volatile double tiny=from_bits(1);volatile float tinyf=from_bits32(1);volatile long double tinyl=tiny;
  check("std logb subnormal",std::logb(tiny)==-1074.);
  check("std logb float subnormal",std::logb(tinyf)==-149.f);
  check("std logb long double subnormal",std::logb(tinyl)==-1074.L);
  check("global logb",::logb(tiny)==-1074.);
  check("global logbf",::logbf(tinyf)==-149.f);
  check("global logbl",::logbl(tinyl)==-1074.L);
  check("builtin logb",__builtin_logb(tiny)==-1074.);
  check("builtin logbf",__builtin_logbf(tinyf)==-149.f);
  check("builtin logbl",__builtin_logbl(tinyl)==-1074.L);
  std::feclearexcept(FE_ALL_EXCEPT);std::feraiseexcept(FE_DIVBYZERO);
  volatile float fraction=.25f;float(*volatile nearby)(float)=::nearbyintf;
  check("nearbyintf value",equal(nearby(fraction),mode==FE_UPWARD?1.f:0.f));
  check("nearbyintf preserves flags",std::fetestexcept(FE_ALL_EXCEPT)==FE_DIVBYZERO);
  std::fenv_t saved;std::fegetenv(&saved);std::fesetround(mode==FE_UPWARD?FE_DOWNWARD:FE_UPWARD);std::feraiseexcept(FE_INVALID);
  check("feupdateenv success",std::feupdateenv(&saved)==0);
  check("feupdateenv rounding",std::fegetround()==mode);
  check("feupdateenv merged flags",std::fetestexcept(FE_ALL_EXCEPT)==(FE_DIVBYZERO|FE_INVALID));
 }
 std::fesetenv(FE_DFL_ENV);
 // Inputs are loaded at runtime, including all three signaling-NaN positions.
 volatile double sn=from_bits(UINT64_C(0x7ff0000000000001)),one=1.;
 for(int pos=0;pos<3;++pos){
  std::feclearexcept(FE_ALL_EXCEPT);double r=fd(pos==0?sn:one,pos==1?sn:one,pos==2?sn:one);
  check("sNaN quieted",std::isnan(r));check("sNaN invalid",std::fetestexcept(FE_ALL_EXCEPT)==FE_INVALID);
 }
 volatile double zero=0.,inf=std::numeric_limits<double>::infinity();
 std::feclearexcept(FE_ALL_EXCEPT);check("inf times zero NaN",std::isnan(fd(inf,zero,one)));check("inf times zero invalid",std::fetestexcept(FE_ALL_EXCEPT)==FE_INVALID);
 std::feclearexcept(FE_ALL_EXCEPT);check("opposite infinity NaN",std::isnan(fd(inf,one,-inf)));check("opposite infinity invalid",std::fetestexcept(FE_ALL_EXCEPT)==FE_INVALID);
 std::feclearexcept(FE_ALL_EXCEPT);check("logb zero infinity",equal(::logb(zero),-inf));check("logb zero flags",std::fetestexcept(FE_ALL_EXCEPT)==FE_DIVBYZERO);
 std::fesetenv(FE_DFL_ENV);std::printf("runtime_math_checks=%d failures=%d\n",checks,failures);return failures?1:0;
}
