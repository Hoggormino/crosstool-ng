// Owned C++ projection checks, including the previously incorrect finite path.
#include <complex>
#include <cmath>
#include <limits>
#include <cstdio>
#include <cstdlib>
static void require(bool ok){if(!ok)std::abort();}
template<class T> void test(){
 const T inf=std::numeric_limits<T>::infinity(),nan=std::numeric_limits<T>::quiet_NaN();
 const T points[][2]={{T(.5),T(.25)},{T(-.5),T(.25)},{T(1e10),T(-1e10)},{T(0),T(-0.0)},
 {inf,T(2)},{-inf,T(-0.0)},{T(2),inf},{T(2),-inf},{inf,nan},{nan,inf},{nan,T(2)},{T(2),nan}};
 for(const auto& p:points){
  const auto z=std::proj(std::complex<T>(p[0],p[1]));
  if(std::isinf(p[0])||std::isinf(p[1])){require(std::isinf(z.real())&&!std::signbit(z.real()));require(z.imag()==T(0));require(std::signbit(z.imag())==std::signbit(p[1]));}
  else{require(std::isnan(p[0])?std::isnan(z.real()):z.real()==p[0]);require(std::isnan(p[1])?std::isnan(z.imag()):z.imag()==p[1]);if(p[1]==T(0))require(std::signbit(z.imag())==std::signbit(p[1]));}
 }
 require(std::proj(T(.5)).real()==T(.5));
}
int main(){test<float>();test<double>();test<long double>();std::puts("TV UI C++ projection finite/zero/infinity/NaN checks passed");}
