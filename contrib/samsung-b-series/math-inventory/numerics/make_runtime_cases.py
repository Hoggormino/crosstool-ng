#!/usr/bin/env python3
"""Seeded FMA, exponent and nearbyint vectors for the private math runtime."""
import argparse,json,random,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True)
rng=random.Random(0x1136f5a);cases=[]
def emit(fn,p,u,v=0,w=0,tag='random'):
    for m in range(4):cases.append(dict(id=len(cases),function=fn,precision=p,mode=m,bits=[u,v,w,0],n=0,kind='real',tag=tag))
def bits(x,p):return int.from_bytes(struct.pack('<f' if p==0 else '<d',x),'little')
for p in range(3):
    mb,eb=(23,8) if p==0 else (52,11);width=1+mb+eb;sign=1<<(width-1);exp=((1<<eb)-1)<<mb;maxfinite=exp-1;normal=1<<mb
    edges=[0,sign,1,sign|1,normal-1,sign|(normal-1),normal,sign|normal,maxfinite,sign|maxfinite,exp,sign|exp,exp|(1<<(mb-1))]
    for u in edges:
        for v,w in [(bits(1.,p),0),(bits(-1.,p),0),(bits(.5,p),u),(bits(2.,p),u^sign),(0,exp),(exp,0),(bits(1.,p),u^sign)]:emit('fma',p,u,v,w,'special')
    # Every subnormal exponent, both signs, with neighbors near powers of two.
    for k in range(mb):
        for u in {1<<k,max(1,(1<<k)-1),(1<<k)+1}:
            emit('logb',p,u,tag='subnormal_exponent');emit('logb',p,u|sign,tag='subnormal_exponent')
    for u in edges:emit('logb',p,u,tag='logb_special')
    for u in [normal,normal-1,normal+1,1,2,3,maxfinite]:
        for v in [bits(.5,p),bits(1.,p)-1,bits(1.,p)+1,bits(2.,p)]:
            for w in [0,1,sign|1,u^sign]:emit('fma',p,u,v,w,'underflow_rounding')
    for i in range(1400):
        us=[rng.getrandbits(width) for j in range(3)]
        # Finite random operands, spanning the full exponent range.
        us=[u if u&exp!=exp else u^normal for u in us]
        emit('fma',p,*us)
    # Near-cancellation of products of numbers near 1, at many mantissa bits.
    for k in range(1,mb+1):
        u=bits(1.+2.**-k,p);v=bits(1.-2.**-k,p);w=bits(-1.,p)
        for delta in [-1,0,1]:emit('fma',p,u,v,w+delta,'cancellation')
    for i in range(300):
        u=rng.randrange(1,normal);emit('logb',p,u|(sign if i&1 else 0),tag='random_subnormal')
        x=rng.uniform(-100.,100.);emit('nearbyint',p,bits(x,p),tag='nearbyint')
for name in ['inputs.tsv','reference-inputs.tsv']:
    with (a.output/name).open('w') as f:
        for c in cases:f.write(f'{c["id"]} {c["function"]} {c["precision"]} {c["mode"]} '+' '.join(f'{u:016x}' for u in c['bits'])+' 0\n')
(a.output/'cases.json').write_text(json.dumps(dict(seed='0x1136f5a',cases=cases),indent=2)+'\n')
print(len(cases),'cases')
