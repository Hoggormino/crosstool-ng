#!/usr/bin/env python3
"""Independent exact identities checking the MPFR/MPC vector plumbing."""
import argparse,json,math,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--vectors',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
cases=json.loads((a.vectors/'cases.json').read_text())['cases'];refs={}
for line in (a.vectors/'reference.tsv').read_text().splitlines():
 x=line.split();refs[int(x[0])]=(int(x[1],16),int(x[2],16))
def bits(x,p):return int.from_bytes(struct.pack('<f' if p==0 else '<d',x),'little')
def val(u,p):return struct.unpack('<f' if p==0 else '<d',u.to_bytes(4 if p==0 else 8,'little'))[0]
def rounded_positive_integer(n,p):
 mant,bias=(23,127) if p==0 else (52,1023);e=n.bit_length()-1;shift=e-mant
 q,r=divmod(n,1<<shift) if shift>0 else (n<<-shift,0)
 if shift>0 and (2*r>1<<shift or 2*r==1<<shift and q&1):q+=1
 if q==1<<(mant+1):q>>=1;e+=1
 return ((e+bias)<<mant)|(q-(1<<mant))
checks=[]
for c in cases:
 if c['id'] not in refs:continue
 p=0 if c['precision']==0 else 1;r=refs[c['id']];fn=c['function'];x=val(c['bits'][0],p)
 if fn=='tgamma' and x==30:checks.append((c['id'],'Gamma(30)=29!',r[0]==rounded_positive_integer(math.factorial(29),p)))
 k=13 if p==0 else 27
 if fn=='fma' and c['bits'][:3]==[bits(1+2.**-k,p),bits(1-2.**-k,p),bits(-1.,p)]:checks.append((c['id'],'FMA cancellation exact power of two',r[0]==bits(-2.**(-2*k),p)))
 if fn=='logb' and c['bits'][0]==1:checks.append((c['id'],'smallest subnormal exponent',r[0]==bits(-149. if p==0 else -1074.,p)))
 if fn=='cproj' and math.isfinite(x) and math.isfinite(val(c['bits'][1],p)):checks.append((c['id'],'finite projection identity',r==tuple(c['bits'][:2])))
assert checks and all(ok for _,_,ok in checks),checks
with a.output.open('x') as f:json.dump({'checks':checks,'passed':True},f,indent=2);f.write('\n')
print(len(checks),'independent exact reference identities passed')
