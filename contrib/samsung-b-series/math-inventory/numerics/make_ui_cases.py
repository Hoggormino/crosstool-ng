#!/usr/bin/env python3
"""Seeded ordinary coordinate/range inputs for common TV UI scalar math."""
import argparse,json,random,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True)
rng=random.Random(0x1136_1717);cases=[]
def bits(x,p):return int.from_bytes(struct.pack('<f' if p==0 else '<d',x),'little')
functions='sin cos tan asin acos atan atan2 sqrt hypot fabs floor ceil round trunc fmod remainder fmin fmax copysign nextafter exp log log1p exp2 expm1 log2 pow'.split()
for p in [0,1,2]:
 for fn in functions:
  for _ in range(64):
   x=rng.uniform(-4096,4096);y=rng.uniform(.125,4096);z=rng.uniform(-4096,4096)
   if fn in ('asin','acos'):x=rng.uniform(-1,1)
   if fn=='sqrt':x=rng.uniform(0,65536)
   if fn in ('exp','expm1'):x=rng.uniform(-16,16)
   if fn=='exp2':x=rng.uniform(-20,20)
   if fn in ('log','log2'):x=rng.uniform(.001,65536)
   if fn=='log1p':x=rng.uniform(-.9,65536)
   if fn=='pow':x=rng.uniform(.125,8);y=rng.uniform(-4,4)
   cases.append(dict(id=len(cases),function=fn,precision=p,mode=0,bits=[bits(v,p) for v in [x,y,z,0.]],n=2,kind='real',tag='ui_seeded_ordinary'))
(a.output/'cases.json').write_text(json.dumps({'seed':'0x11361717','scope':'Ordinary UI scalar ranges; no fused, gamma or complex claims.','cases':cases},indent=2)+'\n')
with (a.output/'inputs.tsv').open('w') as f:
 for c in cases:f.write(f'{c["id"]} {c["function"]} {c["precision"]} 0 '+' '.join(f'{u:016x}' for u in c['bits'])+' 2\n')
print(len(cases),'UI-range cases')
