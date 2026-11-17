// Host-only MPFR/MPC reference evaluator. Never linked into ARM applications.
#include <mpfr.h>
#include <mpc.h>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <string>
#include <map>
#include <cmath>
#include <limits>
using Unary=int(*)(mpfr_ptr,mpfr_srcptr,mpfr_rnd_t);
using Binary=int(*)(mpfr_ptr,mpfr_srcptr,mpfr_srcptr,mpfr_rnd_t);
static std::map<std::string,Unary> unary={
 {"acos",mpfr_acos},{"asin",mpfr_asin},{"atan",mpfr_atan},{"cos",mpfr_cos},{"sin",mpfr_sin},{"tan",mpfr_tan},
 {"cosh",mpfr_cosh},{"sinh",mpfr_sinh},{"tanh",mpfr_tanh},{"exp",mpfr_exp},{"log",mpfr_log},{"log10",mpfr_log10},
 {"sqrt",mpfr_sqrt},{"acosh",mpfr_acosh},{"asinh",mpfr_asinh},{"atanh",mpfr_atanh},{"exp2",mpfr_exp2},
 {"expm1",mpfr_expm1},{"log1p",mpfr_log1p},{"log2",mpfr_log2},{"cbrt",mpfr_cbrt},{"erf",mpfr_erf},{"erfc",mpfr_erfc},
 {"tgamma",mpfr_gamma},{"fabs",mpfr_abs}};
static std::map<std::string,Binary> binary={{"atan2",mpfr_atan2},{"pow",mpfr_pow},{"hypot",mpfr_hypot},{"fmod",mpfr_fmod},{"remainder",mpfr_remainder},{"fdim",mpfr_dim},{"fmax",mpfr_max},{"fmin",mpfr_min},{"copysign",mpfr_copysign}};
static double value(uint64_t u,int p){if(p==0){uint32_t v=u;float x;memcpy(&x,&v,4);return x;}double x;memcpy(&x,&u,8);return x;}
static uint64_t bits(mpfr_srcptr x,int p,mpfr_rnd_t rm){if(p==0){float v=mpfr_get_flt(x,rm);uint32_t u;memcpy(&u,&v,4);return u;}double v=mpfr_get_d(x,rm);uint64_t u;memcpy(&u,&v,8);return u;}
static mpfr_rnd_t mode(int m){return m==1?MPFR_RNDD:m==2?MPFR_RNDU:m==3?MPFR_RNDZ:MPFR_RNDN;}
// MPC has a finite exponent range even when its significand precision grows.
// For very large finite tan/tanh arguments, use a target saturation bound and
// independent MPFR phase signs instead of accepting a lost signed component.
static bool saturated_complex(const std::string& name,unsigned p,unsigned m,
                              uint64_t ux,uint64_t uy,uint64_t& real,uint64_t& imag){
 if(name!="ctanh"&&name!="ctan")return false;
 double x=value(ux,p),y=value(uy,p);if(!std::isfinite(x)||!std::isfinite(y))return false;
 double dom=name=="ctanh"?x:y,phase=name=="ctanh"?y:x;
 if(std::fabs(dom)<=(p==0?100.:800.))return false;
 mpfr_t t,sl,sh,cl,ch,bound;mpfr_inits2(256,t,sl,sh,cl,ch,bound,(mpfr_ptr)0);
 mpfr_set_d(t,phase,MPFR_RNDN);mpfr_mul_2ui(t,t,1,MPFR_RNDN);
 mpfr_sin(sl,t,MPFR_RNDD);mpfr_sin(sh,t,MPFR_RNDU);
 mpfr_cos(cl,t,MPFR_RNDD);mpfr_cos(ch,t,MPFR_RNDU);
 // The small component is bounded by 4*exp(-2*abs(dom)), below half
 // the target's least subnormal. Bound the cosine away from the exponentially
 // smaller correction too, so its sign determines the side of +/-1.
 mpfr_set_ui_2exp(bound,1,p==0?-200:-2000,MPFR_RNDU);
 if(mpfr_signbit(sl)!=mpfr_signbit(sh)||mpfr_signbit(cl)!=mpfr_signbit(ch)
    ||mpfr_cmpabs(cl,bound)<=0||mpfr_cmpabs(ch,bound)<=0){
  fprintf(stderr,"ambiguous saturation phase\n");exit(4);
 }
 uint64_t sign=p==0?0x80000000ull:0x8000000000000000ull;
 bool neg=mpfr_signbit(sl);uint64_t small=neg?sign:0;
 if(phase!=0&&((m==1&&neg)||(m==2&&!neg)))small|=1;
 uint64_t big=p==0?0x3f800000ull:0x3ff0000000000000ull;
 bool nd=std::signbit(dom);if(nd)big|=sign;
 bool delta_negative=(mpfr_signbit(cl)==0)^nd;
 if((m==1&&delta_negative)||(m==2&&!delta_negative)||(m==3&&delta_negative!=nd))
  big+=(!delta_negative)!=nd?1:-1;
 real=name=="ctanh"?big:small;imag=name=="ctanh"?small:big;
 mpfr_clears(t,sl,sh,cl,ch,bound,(mpfr_ptr)0);return true;
}
static int eval(const std::string& name,mpfr_ptr r,mpfr_ptr aux,mpfr_srcptr x,mpfr_srcptr y,mpfr_srcptr z,long n,mpfr_rnd_t rm){
 if(unary.count(name))return unary[name](r,x,rm);
 if(binary.count(name))return binary[name](r,x,y,rm);
 if(name=="fma")return mpfr_fma(r,x,y,z,rm);
 if(name=="lgamma"){int sign;return mpfr_lgamma(r,&sign,x,rm);}
 if(name=="ceil")return mpfr_ceil(r,x);
 if(name=="floor")return mpfr_floor(r,x);
 if(name=="round"||name=="lround"||name=="llround")return mpfr_round(r,x);
 if(name=="trunc")return mpfr_trunc(r,x);
 if(name=="rint"||name=="nearbyint"||name=="lrint"||name=="llrint")return mpfr_rint(r,x,rm);
 if(name=="ldexp"||name=="scalbn"||name=="scalbln")return mpfr_mul_2si(r,x,n,rm);
 if(name=="modf"){if(mpfr_inf_p(x)){mpfr_set(aux,x,rm);mpfr_set_zero(r,mpfr_signbit(x)?-1:1);return 0;}return mpfr_modf(aux,r,x,rm);}
 if(name=="frexp"){mpfr_exp_t e=0;int rc=mpfr_frexp(&e,r,x,rm);mpfr_set_si(aux,e,MPFR_RNDN);return rc;}
 if(name=="remquo"){long q=0;int rc=mpfr_remquo(r,&q,x,y,rm);mpfr_set_si(aux,q,MPFR_RNDN);return rc;}
 if(name=="logb"||name=="ilogb"){if(mpfr_zero_p(x))mpfr_set_inf(r,-1);else if(mpfr_nan_p(x))mpfr_set_nan(r);else if(mpfr_inf_p(x))mpfr_set_inf(r,1);else mpfr_set_si(r,mpfr_get_exp(x)-1,rm);return 0;}
 if(name=="nan"){mpfr_set_nan(r);return 0;}
 fprintf(stderr,"unknown function %s\n",name.c_str());exit(2);
}
using CUnary=int(*)(mpc_ptr,mpc_srcptr,mpc_rnd_t);
static std::map<std::string,CUnary> cu={{"cacos",mpc_acos},{"casin",mpc_asin},{"catan",mpc_atan},{"cacosh",mpc_acosh},{"casinh",mpc_asinh},{"catanh",mpc_atanh},{"ccos",mpc_cos},{"csin",mpc_sin},{"ctan",mpc_tan},{"ccosh",mpc_cosh},{"csinh",mpc_sinh},{"ctanh",mpc_tanh},{"cexp",mpc_exp},{"clog",mpc_log},{"csqrt",mpc_sqrt},{"conj",mpc_conj},{"cproj",mpc_proj}};
int main(int argc,char**argv){
 bool mpc_only=argc==2&&std::string(argv[1])=="--mpc-only-4096";
 if(argc>1&&!mpc_only)return 2;
 fprintf(stderr,"MPFR=%s MPC=%s; %s; directed bounds checked after target conversion\n",mpfr_get_version(),mpc_get_version(),mpc_only?"MPC-only fixed precision 4096 bits":"reference precision 256/1024/4096 bits with target saturation bounds");
 unsigned id,p,m;char fn[32];unsigned long long ux,uy,uz,uw;long n;
 while(scanf("%u %31s %u %u %llx %llx %llx %llx %ld",&id,fn,&p,&m,&ux,&uy,&uz,&uw,&n)==9){
  std::string name(fn);mpfr_rnd_t rm=mode(m);bool ok=false;uint64_t expected=0,extra=0;long long integer=0;int precision_used=0;
  if(name=="nextafter"||name=="nexttoward"){
   double x=value(ux,p),y=value(uy,name=="nexttoward"?1:p);uint64_t sign=p==0?0x80000000ull:0x8000000000000000ull;
   if(std::isnan(x)||std::isnan(y))expected=p==0?0x7fc00000:0x7ff8000000000000ull;
   else if(x==y){if(p==0){float f=y;uint32_t u;memcpy(&u,&f,4);expected=u;}else{memcpy(&expected,&y,8);}}
   else if(x==0)expected=(std::signbit(y)?sign:0)|1;
   else expected=(y>x)==(x>0)?ux+1:ux-1;
   ok=true;
  }else if(!mpc_only&&((name=="ctanh"&&value(ux,p)==0&&!std::isfinite(value(uy,p)))
          ||(name=="ctan"&&value(uy,p)==0&&!std::isfinite(value(ux,p))))){
   // N3096 G.6.2.6 and ctan(z)=-i*ctanh(i*z) preserve the zero
   // component here; MPC 1.4.1 instead returns two NaNs.
   uint64_t qnan=p==0?0x7fc00000:0x7ff8000000000000ull;
   expected=name=="ctanh"?ux:qnan;extra=name=="ctanh"?qnan:uy;ok=true;
  }else if(!mpc_only&&saturated_complex(name,p,m,ux,uy,expected,extra)){
   ok=true;precision_used=256;
  }else for(int prec: {256,1024,4096}){
   if(mpc_only&&prec!=4096)continue;
   mpfr_t x,y,z,w,lo,hi,alo,ahi;mpfr_inits2(prec,x,y,z,w,lo,hi,alo,ahi,(mpfr_ptr)0);
   mpfr_set_d(x,value(ux,p),MPFR_RNDN);mpfr_set_d(y,value(uy,p),MPFR_RNDN);mpfr_set_d(z,value(uz,p),MPFR_RNDN);mpfr_set_d(w,value(uw,p),MPFR_RNDN);
   if(name[0]=='c'&&name!="cos"&&name!="cosh"&&name!="ceil"&&name!="cbrt"&&name!="copysign"||name=="conj"){
    mpc_t a,b,l,h;mpc_init2(a,prec);mpc_init2(b,prec);mpc_init2(l,prec);mpc_init2(h,prec);mpc_set_fr_fr(a,x,y,MPC_RNDNN);mpc_set_fr_fr(b,z,w,MPC_RNDNN);
    if(cu.count(name)){cu[name](l,a,MPC_RNDDD);cu[name](h,a,MPC_RNDUU);mpfr_set(lo,mpc_realref(l),MPFR_RNDN);mpfr_set(hi,mpc_realref(h),MPFR_RNDN);mpfr_set(alo,mpc_imagref(l),MPFR_RNDN);mpfr_set(ahi,mpc_imagref(h),MPFR_RNDN);}
    else if(name=="cpow"){mpc_pow(l,a,b,MPC_RNDDD);mpc_pow(h,a,b,MPC_RNDUU);mpfr_set(lo,mpc_realref(l),MPFR_RNDN);mpfr_set(hi,mpc_realref(h),MPFR_RNDN);mpfr_set(alo,mpc_imagref(l),MPFR_RNDN);mpfr_set(ahi,mpc_imagref(h),MPFR_RNDN);}
    else if(name=="cabs"){mpc_abs(lo,a,MPFR_RNDD);mpc_abs(hi,a,MPFR_RNDU);mpfr_set_zero(alo,1);mpfr_set_zero(ahi,1);}
    else if(name=="carg"){mpc_arg(lo,a,MPFR_RNDD);mpc_arg(hi,a,MPFR_RNDU);mpfr_set_zero(alo,1);mpfr_set_zero(ahi,1);}
    else if(name=="creal"||name=="cimag"){mpfr_set(lo,name=="creal"?x:y,MPFR_RNDN);mpfr_set(hi,lo,MPFR_RNDN);mpfr_set_zero(alo,1);mpfr_set_zero(ahi,1);}
    else {fprintf(stderr,"unknown complex %s\n",fn);return 2;}
    if(cu.count(name)||name=="cpow"){
     if(cu.count(name))cu[name](l,a,MPC_RND(rm,rm));else mpc_pow(l,a,b,MPC_RND(rm,rm));
     if(mpfr_zero_p(lo)&&mpfr_zero_p(hi)){mpfr_set(lo,mpc_realref(l),MPFR_RNDN);mpfr_set(hi,lo,MPFR_RNDN);}
     if(mpfr_zero_p(alo)&&mpfr_zero_p(ahi)){mpfr_set(alo,mpc_imagref(l),MPFR_RNDN);mpfr_set(ahi,alo,MPFR_RNDN);}
    }
    ok=(mpfr_nan_p(lo)&&mpfr_nan_p(hi)||bits(lo,p,rm)==bits(hi,p,rm))&&(mpfr_nan_p(alo)&&mpfr_nan_p(ahi)||bits(alo,p,rm)==bits(ahi,p,rm));
    mpc_clear(a);mpc_clear(b);mpc_clear(l);mpc_clear(h);
   }else{
    bool integer_round=name=="rint"||name=="nearbyint"||name=="lrint"||name=="llrint";
    eval(name,lo,alo,x,y,z,n,integer_round?rm:MPFR_RNDD);eval(name,hi,ahi,x,y,z,n,integer_round?rm:MPFR_RNDU);
    if(mpfr_zero_p(lo)&&mpfr_zero_p(hi)&&mpfr_signbit(lo)!=mpfr_signbit(hi)){eval(name,lo,alo,x,y,z,n,rm);mpfr_set(hi,lo,MPFR_RNDN);}
    ok=mpfr_nan_p(lo)&&mpfr_nan_p(hi)||bits(lo,p,rm)==bits(hi,p,rm);
   }
   expected=bits(lo,p,rm);extra=bits(alo,p,rm);
   if(name=="ilogb"||name=="lrint"||name=="llrint"||name=="lround"||name=="llround")integer=(long long)mpfr_get_d(lo,MPFR_RNDN);
   if(name=="frexp"||name=="remquo")integer=(long long)mpfr_get_d(alo,MPFR_RNDN);
   mpfr_clears(x,y,z,w,lo,hi,alo,ahi,(mpfr_ptr)0);precision_used=prec;
   if(ok)break;
  }
  if(!ok){fprintf(stderr,"ambiguous reference id=%u fn=%s\n",id,fn);return 3;}
  printf("%u %016llx %016llx %lld %d\n",id,(unsigned long long)expected,(unsigned long long)extra,integer,precision_used);
 }
}
