#!/usr/bin/env python3
"""Generate owned C ABI and C++ standard math evaluators from the inventory."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from math_inventory_catalog import SCALAR,PRECISIONS,COMPLEX_C,CLASSIFY,COMPARE
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--baseline-std',action='store_true',help='Use old available C++ APIs and explicit C ABI probes for unavailable names');a=ap.parse_args()
out=['''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fenv.h>
#ifdef NUMERICS_STD
#include <cmath>
#include <complex>
#include <type_traits>
#else
#include <math.h>
#include <complex.h>
#endif
struct Input {unsigned id,p,mode;uint64_t x,y,z,w;long n;};
struct Output {uint64_t value,extra;long long integer;};
static float get_f(uint64_t u){uint32_t w=u;float x;memcpy(&x,&w,4);return x;}
static double get_d(uint64_t u){double x;memcpy(&x,&u,8);return x;}
static long double get_l(uint64_t u){long double x;_Static_assert(sizeof(x)==8,"binary64 long double");memcpy(&x,&u,8);return x;}
static uint64_t put_f(float x){uint32_t u;memcpy(&u,&x,4);return u;}
static uint64_t put_d(double x){uint64_t u;memcpy(&u,&x,8);return u;}
static uint64_t put_l(long double x){uint64_t u;memcpy(&u,&x,8);return u;}
static int normalize_class(int x){return x==FP_NAN?0:x==FP_INFINITE?1:x==FP_ZERO?2:x==FP_SUBNORMAL?3:x==FP_NORMAL?4:-1;}
typedef void (*Evaluate)(const struct Input*,struct Output*);
'''.replace('_Static_assert','static_assert' if False else '_Static_assert')]
# C++ accepts a common spelling through this local owned-source macro only.
out[0]=out[0].replace('#ifdef NUMERICS_STD\n#include <cmath>','#ifdef NUMERICS_STD\n#define _Static_assert static_assert\n#include <cmath>')
entries={}
for typ,suffix in PRECISIONS:
    s=suffix or 'd';get='get_'+s;put='put_'+s
    for fn,args,result,group in SCALAR:
        ret=typ if result=='T' else result
        mapping=dict(x=typ,y=typ,z=typ,exponent='int',long_exponent='long',direction='long double')
        mapping.update({'&exponent':'int*','&quotient':'int*','&part':typ+'*','""':'const char*'})
        params=','.join(mapping[x] for x in args.split(','));symbol=fn+suffix;owned='owned_'+symbol
        use_std=not a.baseline_std or group=='classic'
        condition='defined(NUMERICS_STD)' if use_std else '0'
        out.append(f'#if !({condition})\n#ifdef __cplusplus\nextern "C"\n#endif\n{ret} {owned}({params}) __asm__("{symbol}");\n#endif\n')
        name='eval_'+fn+'_'+s;entries.setdefault(fn,[]).append(name)
        out.append(f'static void {name}(const struct Input*c,struct Output*o){{typedef {typ} T;T x={get}(c->x),y={get}(c->y),z={get}(c->z),part=0;int exponent=c->n,quotient=0;long long_exponent=c->n;long double direction=get_l(c->y);\n')
        stdfn=fn+suffix if fn=='nan' else fn;expr=f'std::{stdfn}({args})'
        out.append(f'#if {condition}\nstatic_assert(std::is_same<decltype({expr}),{ret}>::value,"math return type");\n{ret} value={expr};\n#else\n{ret} (*volatile call)({params})=&{owned};\n{ret} value=call({args});\n#endif\n')
        out.append(f'o->value={put}(value);' if result=='T' else 'o->integer=(long long)value;')
        if fn=='modf':out.append(f'o->extra={put}(part);')
        if fn=='frexp':out.append('o->integer=exponent;')
        if fn=='remquo':out.append('o->integer=quotient;')
        out.append('}\n')
    for fn in COMPLEX_C:
        scalar=fn in ('cabs','carg','creal','cimag');ret=typ if scalar else typ+' _Complex';params=typ+' _Complex'+(','+typ+' _Complex' if fn=='cpow' else '')
        symbol=fn+suffix;owned='owned_'+symbol;name='eval_'+fn+'_'+s;entries.setdefault(fn,[]).append(name)
        out.append(f'#ifndef NUMERICS_STD\nextern {ret} {owned}({params}) __asm__("{symbol}");\n#endif\n')
        out.append(f'static void {name}(const struct Input*c,struct Output*o){{typedef {typ} T;T x={get}(c->x),y={get}(c->y),z={get}(c->z),w={get}(c->w);\n')
        stdfn={'cabs':'abs','carg':'arg','creal':'real','cimag':'imag','conj':'conj','cproj':'proj'}.get(fn,fn[1:])
        args='aa,bb' if fn=='cpow' else 'aa';cppret=typ if scalar else 'CT'
        out.append(f'#ifdef NUMERICS_STD\ntypedef std::complex<T> CT;CT aa(x,y),bb(z,w);{cppret} value=std::{stdfn}( {args} );\n')
        if scalar:out.append(f'o->value={put}(value);\n')
        else:out.append(f'o->value={put}(std::real(value));o->extra={put}(std::imag(value));\n')
        out.append(f'#else\ntypedef {typ} _Complex CT;CT aa,bb;__real__ aa=x;__imag__ aa=y;__real__ bb=z;__imag__ bb=w;{ret} (*volatile call)({params})=&{owned};{ret} value=call({args});\n')
        if scalar:out.append(f'o->value={put}(value);\n')
        else:out.append(f'o->value={put}(__real__ value);o->extra={put}(__imag__ value);\n')
        out.append('#endif\n}\n')
    for fn in CLASSIFY+COMPARE:
        name='eval_'+fn+'_'+s;entries.setdefault(fn,[]).append(name);args='x,y' if fn in COMPARE else 'x';ret='int' if fn=='fpclassify' or a.baseline_std and typ=='double' and fn in ('isinf','isnan') else 'bool'
        out.append(f'static void {name}(const struct Input*c,struct Output*o){{typedef {typ} T;T x={get}(c->x),y={get}(c->y);\n#ifdef NUMERICS_STD\nstatic_assert(std::is_same<decltype(std::{fn}({args})),{ret}>::value,"predicate return type");int value=std::{fn}({args});\n#else\nint value={fn}({args});\n#endif\n')
        out.append('o->integer=normalize_class(value);}\n' if fn=='fpclassify' else 'o->integer=!!value;}\n')
out.append('struct Entry {const char*name;Evaluate functions[3];};\nstatic const struct Entry entries[]={\n')
for fn,names in entries.items():out.append('{"'+fn+'",{'+','.join(names)+'}},\n')
out.append('''};
int main(int argc,char**argv){
 if(argc!=2)return 2;FILE*f=fopen(argv[1],"r");if(!f)return 3;
 int modes[]={FE_TONEAREST,FE_DOWNWARD,FE_UPWARD,FE_TOWARDZERO};
 char name[32];struct Input c;unsigned long long x,y,z,w;
 while(fscanf(f,"%u %31s %u %u %llx %llx %llx %llx %ld",&c.id,name,&c.p,&c.mode,&x,&y,&z,&w,&c.n)==9){
  c.x=x;c.y=y;c.z=z;c.w=w;struct Output o={0,0,0};Evaluate call=0;
  for(unsigned j=0;j<sizeof(entries)/sizeof(entries[0]);j++)if(!strcmp(name,entries[j].name))call=entries[j].functions[c.p];
  if(!call||c.p>2||c.mode>3)return 4;
  int status=fesetround(modes[c.mode]);feclearexcept(FE_ALL_EXCEPT);errno=0;
  call(&c,&o);int error=errno;int flags=fetestexcept(FE_ALL_EXCEPT);int rounding=fegetround();
  printf("%u %d %016llx %016llx %lld %d %d %d\\n",c.id,status,(unsigned long long)o.value,(unsigned long long)o.extra,o.integer,error,flags,rounding);
 }
 fclose(f);fesetround(FE_TONEAREST);return 0;
}
''')
a.output.write_text(''.join(out));print(len(entries),'families generated')
