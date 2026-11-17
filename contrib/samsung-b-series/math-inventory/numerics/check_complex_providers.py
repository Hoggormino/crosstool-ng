#!/usr/bin/env python3
"""Require the private complex symbol versions and observed runtime providers."""
import argparse,json,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--binary',type=Path,required=True);ap.add_argument('--bindings',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
required={f+s for f in ['cacos','cacosh','casin','casinh','catan','catanh','ctan','ctanh'] for s in ['', 'f','l']};version='GLIBCXX_SAMSUNG_MATH_1.1'
symbols=subprocess.check_output(['readelf','-W','--dyn-syms',str(a.binary)],text=True);found={m.group(1) for m in re.finditer(r'\bUND\s+(\w+)@'+re.escape(version)+r'\b',symbols)}
if required-found:raise SystemExit('Missing private complex imports: '+str(sorted(required-found)))
records=[]
for line in a.bindings.read_text().splitlines():
 m=re.search(r'binding file (.*?) \[.*?\] to (.*?) \[.*?\]:.*?symbol `([^\x27]+)\x27 \[([^]]+)\]',line)
 if m and m[3] in required and m[4]==version:records.append(dict(consumer=m[1],provider=m[2],symbol=m[3],version=m[4]))
if required-{r['symbol'] for r in records}:raise SystemExit('Missing private complex bindings')
if any(not r['provider'].endswith('/private/libstdc++.so.6') for r in records):raise SystemExit('Unexpected complex provider')
with a.output.open('x') as f:json.dump(dict(passed=True,version=version,symbols=sorted(required),bindings=records),f,indent=2);f.write('\n')
print('All 24 private complex imports and providers verified')
