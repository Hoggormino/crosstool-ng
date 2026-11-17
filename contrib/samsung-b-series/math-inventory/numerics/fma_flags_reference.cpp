// Host-only independent flag expectations for finite fused operations.
#include <mpfr.h>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cmath>
static double value(uint64_t u,unsigned p){if(p==0){uint32_t v=u;float x;memcpy(&x,&v,4);return x;}double x;memcpy(&x,&u,8);return x;}
int main(){
 unsigned id,p,m;char fn[32];unsigned long long u,v,w,q;long n;mpfr_t x,y,z,r,t,rounded;
 mpfr_inits2(4096,x,y,z,r,t,(mpfr_ptr)0);mpfr_init2(rounded,53);
 while(scanf("%u %31s %u %u %llx %llx %llx %llx %ld",&id,fn,&p,&m,&u,&v,&w,&q,&n)==9){
  if(strcmp(fn,"fma"))continue;
  double a=value(u,p),b=value(v,p),c=value(w,p);
  if(!std::isfinite(a)||!std::isfinite(b)||!std::isfinite(c))continue;
  mpfr_rnd_t mode=m==1?MPFR_RNDD:m==2?MPFR_RNDU:m==3?MPFR_RNDZ:MPFR_RNDN;
  mpfr_set_d(x,a,MPFR_RNDN);mpfr_set_d(y,b,MPFR_RNDN);mpfr_set_d(z,c,MPFR_RNDN);
  // 4096 bits exactly spans a binary64 product plus binary64 addend.
  if(mpfr_fma(r,x,y,z,mode)!=0)return 2;
  double got=p==0?(double)mpfr_get_flt(r,mode):mpfr_get_d(r,mode);
  mpfr_set_d(t,got,MPFR_RNDN);int flags=mpfr_equal_p(t,r)?0:16,mask=31;
  mpfr_set_prec(rounded,p==0?24:53);mpfr_set(rounded,r,mode);
  if(!mpfr_zero_p(rounded)&&mpfr_get_exp(rounded)>(p==0?128:1024))flags|=4;
  double minnormal=p==0?0x1p-126:0x1p-1022;
  if(flags&16){
   if(std::fabs(got)<minnormal)flags|=8;
   // Tininess detection before/after rounding is architecture dependent.
   // Test these boundary values separately instead of selecting either policy.
   if(std::fabs(got)==minnormal)mask&=~8;
  }
  printf("%u %d %d\n",id,flags,mask);
 }
 mpfr_clears(x,y,z,r,t,rounded,(mpfr_ptr)0);
}
