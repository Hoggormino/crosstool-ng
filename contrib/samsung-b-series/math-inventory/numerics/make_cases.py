#!/usr/bin/env python3
"""Deterministic binary32/binary64 input vectors; expectations come from MPFR/MPC."""
import argparse,json,math,random,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from math_inventory_catalog import SCALAR,COMPLEX_C,CLASSIFY,COMPARE
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True)
cases=[]
def bits(x,p):
    if p==0:
        try:return struct.unpack('<I',struct.pack('<f',x))[0]
        except OverflowError:return 0xff800000 if x<0 else 0x7f800000
    return struct.unpack('<Q',struct.pack('<d',x))[0]
def val(u,p):return struct.unpack('<f' if p==0 else '<d',int(u).to_bytes(4 if p==0 else 8,'little'))[0]
def add(fn,p,x=.5,y=.25,z=.75,w=0.,n=2,m=0,kind='real',tag='ordinary',raw=None):
    values=[bits(v,p) for v in [x,y,z,w]] if raw is None else list(raw)
    if fn=='nexttoward' and raw is None:values[1]=bits(y,1)
    cases.append(dict(id=len(cases),function=fn,precision=p,mode=m,bits=values,n=n,kind=kind,tag=tag))
for p in [0,1,2]:
    q=0 if p==0 else 1;mini=val(1,q);normal=val(0x00800000 if q==0 else 0x0010000000000000,q);maximum=val(0x7f7fffff if q==0 else 0x7fefffffffffffff,q)
    tiny=[0.,-0.,mini,-mini,normal,-normal,2**-20,-2**-20]
    moderate=[-.875,-.5,-.25,.125,.5,.75,1.,1.25,2.,3.5,10.]
    for fn,args,ret,group in SCALAR:
        if fn in CLASSIFY+COMPARE:continue
        if fn in ('acos','asin','atanh'):xs=tiny+[-1.,-.75,.25,.875,1.]
        elif fn=='acosh':xs=[1.,val(bits(1.,q)+1,q),1.25,2.,10.,maximum]
        elif fn in ('log','log2','log10'):xs=[mini,normal,2**-20,.25,.5,1.,val(bits(1.,q)+1,q),2.,10.,maximum,0.,-1.]
        elif fn=='log1p':xs=tiny+[-1.,-.875,-.5,.5,1.,10.,maximum]
        elif fn=='sqrt':xs=[0.,-0.,mini,normal,.25,.5,1.,2.,4.,maximum,-1.]
        elif fn in ('tgamma','lgamma'):xs=[-.5,-1.5,-2.5,.125,.5,1.,1.25,2.,3.,5.,10.,30.,100.,170.]
        elif fn in ('exp','exp2','expm1','cosh','sinh','tanh'):xs=tiny+[-1000.,-100.,-10.,-1.,.5,1.,10.,80.,100.,700.,710.,1000.]
        elif fn in ('sin','cos','tan','atan','asinh','cbrt'):xs=tiny+moderate+[math.pi/2,math.pi,1e10,-1e10,maximum]
        elif fn in ('lrint','llrint','lround','llround','rint','nearbyint','round','trunc','floor','ceil'):xs=tiny+[-3.5,-2.5,-1.5,-.5,.5,1.5,2.5,3.5,12345.75]
        elif fn=='ilogb':xs=[mini,normal,2**-20,.25,.5,1.,2.,10.,maximum]
        else:xs=tiny+moderate+[maximum]
        modes=[0,1,2,3] if fn in ('lrint','llrint','lround','llround','rint','nearbyint','round','trunc','floor','ceil','fma') else [0]
        if fn=='nan':add(fn,p,tag='quiet_nan');continue
        if fn in ('atan2','pow','fmod','hypot','remainder','copysign','nextafter','fdim','fmax','fmin','remquo','nexttoward'):
            pairs=[(.5,.25),(3.,2.),(-3.,2.),(3.,-2.),(-3.,-2.),(0.,-0.),(-0.,0.),(mini,0.),(normal,mini),(maximum,maximum)]
            if fn=='pow':pairs=[(.5,2.),(2.,.5),(2.,-3.),(-2.,3.),(-2.,2.),(0.,2.),(-0.,3.),(10.,10.),(normal,.5)]
            if fn=='atan2':pairs += [(0.,-1.),(-0.,-1.),(1.,0.),(-1.,0.)]
            if fn in ('fmax','fmin','hypot'):pairs += [(math.inf,math.nan),(math.nan,1.),(1.,math.nan)]
            if fn in ('nextafter','nexttoward'):pairs += [(1.,2.),(1.,0.),(maximum,math.inf),(-maximum,-math.inf),(math.inf,0.),(0.,math.inf),(-0.,-math.inf)]
            for x,y in pairs:add(fn,p,x,y,tag='binary_edge' if not math.isfinite(x*y) else 'binary')
            continue
        if fn=='fma':
            k=13 if p==0 else 27
            triples=[(1+2**-k,1-2**-k,-1.),(maximum,2.,-maximum),(.5,.25,.125),(1.,1.,-1.),(-1.,1.,1.),(mini,.5,mini),(0.,1.,-0.),(-0.,1.,-0.)]
            for m in modes:
                for x,y,z in triples:add(fn,p,x,y,z,m=m,tag='fma_cancellation')
            continue
        if fn in ('ldexp','scalbn','scalbln'):
            for x in [0.,-0.,mini,normal,.5,-.5,maximum]:
                for n in [-1100,-150,-1,0,1,150,1100]:add(fn,p,x,n=n,tag='scaling')
            continue
        for m in modes:
            for x in xs:add(fn,p,x,m=m,tag='edge' if x in tiny or not math.isfinite(x) else 'ordinary')
    for fn in COMPLEX_C:
        points=[(.5,.25),(-.5,.25),(-.5,-.25),(1.,0.),(1.,-0.),(-1.,0.),(-1.,-0.),(0.,.5),(2.,3.),(normal,normal),(1e10,-1e10)]
        if fn=='cpow':points=[(.5,.25),(-.5,.25),(-.5,-.25),(2.,3.),(1.,0.)]
        for x,y in points:add(fn,p,x,y,z=.75,w=.25,kind='complex',tag='complex_branch' if y==0 else 'complex')
    special=[0,1,0x80000000 if q==0 else 0x8000000000000000,0x00800000 if q==0 else 0x0010000000000000,0x7f800000 if q==0 else 0x7ff0000000000000,0xff800000 if q==0 else 0xfff0000000000000,0x7fc12345 if q==0 else 0x7ff8123456789abc,0xffc12345 if q==0 else 0xfff8123456789abc,bits(1.,q),bits(-1.,q)]
    for fn in CLASSIFY+COMPARE:
        for u in special:
            add(fn,p,kind='classification',tag='classification',raw=[u,bits(.5,q),0,0])
with (a.output/'inputs.tsv').open('w') as f:
    for c in cases:f.write(f'{c["id"]} {c["function"]} {c["precision"]} {c["mode"]} '+ ' '.join(f'{u:016x}' for u in c['bits'])+f' {c["n"]}\n')
lines=(a.output/'inputs.tsv').read_text().splitlines(True)
(a.output/'reference-inputs.tsv').write_text(''.join(line for c,line in zip(cases,lines) if c['kind']!='classification'))
(a.output/'cases.json').write_text(json.dumps({'seed':'deterministic curated binary inputs','cases':cases},indent=2)+'\n')
print(len(cases),'cases')
