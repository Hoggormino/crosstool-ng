#!/usr/bin/env python3
"""Deterministic MPC inputs for the private complex-function correction."""
import argparse,json,math,random,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True)
rng=random.Random(0x1136c017);cases=[]
functions=['cacos','cacosh','casin','casinh','catan','catanh','ctan','ctanh']
def bits(x,p):
 try:return int.from_bytes(struct.pack('<f' if p==0 else '<d',x),'little')
 except OverflowError:return (0xff800000 if x<0 else 0x7f800000) if p==0 else (0xfff0000000000000 if x<0 else 0x7ff0000000000000)
def value(u,p):return struct.unpack('<f' if p==0 else '<d',u.to_bytes(4 if p==0 else 8,'little'))[0]
def emit(fn,p,x,y,tag,modes=(0,)):
 for m in modes:cases.append(dict(id=len(cases),function=fn,precision=p,mode=m,bits=[x,y,0,0],n=0,kind='complex',tag=tag))
for p in range(3):
 mb,eb=(23,8) if p==0 else (52,11);width=mb+eb+1;sign=1<<(width-1);normal=1<<mb;inf=((1<<eb)-1)<<mb;one=bits(1.,p)
 tiny=[0,sign,1,sign|1,normal,sign|normal,normal-1,sign|(normal-1),bits(2.**(-20 if p==0 else -40),p)]
 branch=[one-1,one,one+1,sign|(one-1),sign|one,sign|(one+1)]
 # Cartesian pairs include signed branch approaches, both tiny components and poles.
 for fn in functions:
  for x in tiny+branch:
   for y in tiny:emit(fn,p,x,y,'branch_and_tiny',(0,1,2,3))
  for x in tiny:
   for y in branch:emit(fn,p,x,y,'imaginary_branch',(0,1,2,3))
  special=[0,sign,one,sign|one,inf,sign|inf,inf|(1<<(mb-1))]
  for x in special:
   for y in special:emit(fn,p,x,y,'special')
  # Finite ordinary-domain samples, including both sides of cuts.
  for i in range(120):emit(fn,p,bits(rng.uniform(-20.,20.),p),bits(rng.uniform(-20.,20.),p),'ordinary')
  # Wide dynamic range: uniform random binary fields, constrained to finite inputs.
  for i in range(160):
   pair=[rng.getrandbits(width) for j in range(2)];pair=[u if u&inf!=inf else u^normal for u in pair]
   emit(fn,p,*pair,'wide_exponent')
  # Overflow thresholds, scaling crossovers and trigonometric poles.
  for x in [1e10,22.,11.,350.,710.,1e20]:
   for y in [0.,-0.,.25,math.pi/2,math.pi,1e10,-1e10]:
    for sx in [-1,1]:
     emit(fn,p,bits(sx*x,p),bits(y,p),'extreme');emit(fn,p,bits(y,p),bits(sx*x,p),'rotated_extreme')
  pole=bits(math.pi/2,p)
  for u in [pole-1,pole,pole+1]:
   for v in tiny[:6]:emit(fn,p,u,v,'trig_pole');emit(fn,p,v,u,'hyperbolic_pole')
lines=[]
for c in cases:lines.append(f'{c["id"]} {c["function"]} {c["precision"]} {c["mode"]} '+' '.join(f'{u:016x}' for u in c['bits'])+' 0\n')
for name in ['inputs.tsv','reference-inputs.tsv']:(a.output/name).write_text(''.join(lines))
(a.output/'cases.json').write_text(json.dumps(dict(seed='0x1136c017',cases=cases),indent=2)+'\n')
print(len(cases),'cases')
