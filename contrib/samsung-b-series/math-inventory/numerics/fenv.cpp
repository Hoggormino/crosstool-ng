// Owned environment-state and thread-isolation checks; numerical findings persist.
#include <cfenv>
#include <cmath>
#include <cstdio>
#include <pthread.h>
static int failures;
static void check(const char*name,bool pass){std::printf("%s %s\n",name,pass?"PASS":"FAIL");if(!pass)++failures;}
struct Thread {int mode;double expected;bool pass;};
static pthread_barrier_t barrier;
static void* worker(void*arg){auto*t=static_cast<Thread*>(arg);t->pass=std::fesetround(t->mode)==0;pthread_barrier_wait(&barrier);volatile double x=1.5;double(*volatile fn)(double)=static_cast<double(*)(double)>(&std::rint);t->pass=t->pass&&std::fegetround()==t->mode&&fn(x)==t->expected;return nullptr;}
int main(){
 std::fesetenv(FE_DFL_ENV);std::feclearexcept(FE_ALL_EXCEPT);std::fesetround(FE_UPWARD);std::feraiseexcept(FE_DIVBYZERO);
 std::fenv_t saved;check("fegetenv",std::fegetenv(&saved)==0);
 std::fesetround(FE_DOWNWARD);std::feclearexcept(FE_ALL_EXCEPT);check("fesetenv",std::fesetenv(&saved)==0);
 check("round_restore",std::fegetround()==FE_UPWARD);check("flags_restore",std::fetestexcept(FE_ALL_EXCEPT)==FE_DIVBYZERO);
 std::fenv_t held;check("feholdexcept",std::feholdexcept(&held)==0);check("hold_clears_flags",std::fetestexcept(FE_ALL_EXCEPT)==0);
 std::feraiseexcept(FE_INVALID);check("feupdateenv",std::feupdateenv(&held)==0);check("update_merges_flags",std::fetestexcept(FE_ALL_EXCEPT)==(FE_INVALID|FE_DIVBYZERO));
 std::fesetenv(FE_DFL_ENV);std::feclearexcept(FE_ALL_EXCEPT);volatile double x=.25;double(*volatile nr)(double)=static_cast<double(*)(double)>(&std::nearbyint);double value=nr(x);
 check("nearbyint_value",value==0.);check("nearbyint_no_inexact",!(std::fetestexcept(FE_ALL_EXCEPT)&FE_INEXACT));
 pthread_barrier_init(&barrier,nullptr,3);Thread a{FE_DOWNWARD,1.,false},b{FE_UPWARD,2.,false};pthread_t ta,tb;
 int ca=pthread_create(&ta,nullptr,worker,&a),cb=pthread_create(&tb,nullptr,worker,&b);
 if(!ca&&!cb){pthread_barrier_wait(&barrier);pthread_join(ta,nullptr);pthread_join(tb,nullptr);check("thread_downward",a.pass);check("thread_upward",b.pass);check("parent_round_unchanged",std::fegetround()==FE_TONEAREST);}
 else check("pthread_create",false);
 std::fesetenv(FE_DFL_ENV);std::printf("fenv_failures=%d\n",failures);return failures?1:0;
}
