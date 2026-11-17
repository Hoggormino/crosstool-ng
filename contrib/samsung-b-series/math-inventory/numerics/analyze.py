#!/usr/bin/env python3
"""Compare owned numerical outputs with independently rounded MPFR/MPC data."""
import argparse,collections,json,math,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--cases',type=Path,required=True);ap.add_argument('--reference',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--strict',action='store_true',help='Return failure if comparison or environment findings exist');a=ap.parse_args()
if a.output.exists():raise SystemExit('Refusing to overwrite analysis')
cases=json.loads(a.cases.read_text())['cases'];refs={}
for line in a.reference.read_text().splitlines():
    x=line.split();refs[int(x[0])]=(int(x[1],16),int(x[2],16),int(x[3]),int(x[4]))
receipt=json.loads(a.receipt.read_text());assert receipt['exit']==0 and receipt['runtime_bytes_unchanged']
records={}
for line in Path(receipt['stdout']).read_text().splitlines():
    x=line.split();assert len(x)==8,line
    records[int(x[0])]=dict(status=int(x[1]),bits=int(x[2],16),extra=int(x[3],16),integer=int(x[4]),errno=int(x[5]),flags=int(x[6]),rounding=int(x[7]))
assert len(records)==len(cases) and set(records)=={x['id'] for x in cases}
def value(u,p):return struct.unpack('<f' if p==0 else '<d',int(u).to_bytes(4 if p==0 else 8,'little'))[0]
def fields(u,p):
    mb=23 if p==0 else 52;eb=8 if p==0 else 11
    return ((u>>(mb+eb))&1,(u>>mb)&((1<<eb)-1),u&((1<<mb)-1))
def cls(u,p):
    sign,e,m=fields(u,p);maxe=255 if p==0 else 2047
    return 0 if e==maxe and m else 1 if e==maxe else 2 if e==0 and m==0 else 3 if e==0 else 4
exact=set('fabs sqrt copysign ceil floor round trunc rint nearbyint fmod remainder remquo modf frexp ldexp scalbn scalbln nextafter nexttoward fdim fma fmax fmin logb'.split())
integers=set('ilogb lrint llrint lround llround'.split())
complex_scalar=set('cabs carg creal cimag'.split())
byfn=collections.defaultdict(lambda:dict(cases=0,failed=0,max_ulp=0,advisories=0,errno_counts=collections.Counter(),flag_counts=collections.Counter()))
failures=[];details=[];fenv=[]
for c in cases:
    o=records[c['id']];fn=c['function'];p=0 if c['precision']==0 else 1;s=byfn[(fn,c['precision'],c['mode'])];s['cases']+=1;s['errno_counts'][o['errno']]+=1;s['flag_counts'][o['flags']]+=1
    problems=[];advisories=[];maxulp=0
    if o['status']!=0 or o['rounding']!=[0,0x800000,0x400000,0xc00000][c['mode']]:problems.append('rounding_mode_not_selected')
    if c['kind']=='classification':
        u,v=c['bits'][:2];sign,e,m=fields(u,p);category=cls(u,p);x=value(u,p);y=value(v,p)
        if fn=='fpclassify':expected=category
        elif fn=='signbit':expected=sign
        elif fn=='isfinite':expected=int(category not in (0,1))
        elif fn=='isinf':expected=int(category==1)
        elif fn=='isnan':expected=int(category==0)
        elif fn=='isnormal':expected=int(category==4)
        else:
            unordered=math.isnan(x) or math.isnan(y)
            expected=int({'isunordered':unordered,'isgreater':not unordered and x>y,'isgreaterequal':not unordered and x>=y,'isless':not unordered and x<y,'islessequal':not unordered and x<=y,'islessgreater':not unordered and x!=y}[fn])
        if o['integer']!=expected:problems.append('classification_value')
    else:
        expected,extra,integer,ref_precision=refs[c['id']]
        if fn in integers:
            if o['integer']!=integer:problems.append('integer_value')
        else:
            pairs=[(o['bits'],expected)]
            if fn=='modf' or c['kind']=='complex' and fn not in complex_scalar:pairs.append((o['extra'],extra))
            scale=max(abs(value(expected,p)),abs(value(extra,p))) if c['kind']=='complex' and fn not in complex_scalar else 0
            for component,(got,want) in enumerate(pairs):
                gc,wc=cls(got,p),cls(want,p)
                if wc==0:
                    if gc!=0:problems.append('expected_nan')
                    continue
                if wc==1 or gc==1:
                    if got!=want:
                        # Annex G leaves only these infinity signs unspecified.
                        # Still reject infinity from finite inputs and retain
                        # every signed-zero and finite accuracy check.
                        x,y=[value(u,p) for u in c['bits'][:2]]
                        optional=(fn=='casinh' and component==0 and math.isnan(x) and math.isinf(y)
                                  or fn=='casin' and component==1 and math.isinf(x) and math.isnan(y)
                                  or fn=='cacos' and component==1 and math.isinf(x) and math.isnan(y))
                        if optional and gc==wc==1:advisories.append('annex_g_unspecified_infinity_sign')
                        else:problems.append('infinity_or_overflow_value')
                    continue
                if gc==0:problems.append('unexpected_nan');continue
                if got==want:continue
                if gc==2 and wc==2:
                    if fn in ('fmax','fmin'):advisories.append('signed_zero_choice')
                    else:problems.append('signed_zero')
                    continue
                mask=(1<<(32 if p==0 else 64))-1;sign=1<<(31 if p==0 else 63)
                ordered=lambda x:(~x)&mask if x&sign else x|sign
                ulp=abs(ordered(got)-ordered(want));maxulp=max(maxulp,ulp)
                budget=0 if fn in exact else 8 if fn in ('tgamma','lgamma') else 16 if c['kind']=='complex' else 4
                relative_ok=c['kind']=='complex' and fn not in complex_scalar and math.isfinite(scale) and abs(value(got,p)-value(want,p))<=16*(2**(-23 if p==0 else -52))*scale
                if ulp>budget and not relative_ok:problems.append('reference_error_budget')
                elif relative_ok and ulp>budget:advisories.append('complex_relative_tolerance')
            if fn=='frexp' and o['integer']!=integer:problems.append('frexp_exponent')
            if fn=='remquo' and (abs(o['integer'])%8!=abs(integer)%8 or o['integer'] and integer and (o['integer']<0)!=(integer<0)):problems.append('remquo_quotient')
        if fn=='nearbyint' and o['flags']&16:fenv.append(dict(id=c['id'],issue='nearbyint_raised_inexact',observed=o))
    s['max_ulp']=max(s['max_ulp'],maxulp);s['advisories']+=len(advisories)
    if problems:
        s['failed']+=1;failures.append(dict(case=c,observed=o,reference=refs.get(c['id']),issues=sorted(set(problems)),max_ulp=maxulp))
    if advisories:details.append(dict(id=c['id'],advisories=advisories,max_ulp=maxulp))
summary={f'{name}:{precision}:mode{mode}':data for (name,precision,mode),data in sorted(byfn.items())}
out=dict(receipt=str(a.receipt),case_count=len(cases),within_comparison_policy=not failures and not fenv,failed_case_count=len(failures),failure_counts=dict(collections.Counter(x['case']['function'] for x in failures)),fenv_findings=fenv,functions=summary,failures=failures,advisories=details,
         policy='Engineering comparison: exact basic operations; 4 ULP real transcendental, 8 ULP gamma, 16 ULP or 16*epsilon*complex-magnitude complex components. These budgets are not a claim of standard-mandated accuracy. NaN payloads/sign ignored; fmin/fmax zero-sign choices advisory. No TV kernel/hardware validation.')
with a.output.open('x') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
print('cases',len(cases),'failed',len(failures),'by function',out['failure_counts'],'fenv findings',len(fenv))
if a.strict and (failures or fenv):raise SystemExit(1)
