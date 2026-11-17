#!/usr/bin/env python3
"""Require private-version imports and observed providers for corrected math."""
import argparse,json,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--binary',type=Path,required=True);ap.add_argument('--bindings',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
required={'fma','fmaf','fmal','logb','logbf','logbl','nearbyintf','feupdateenv'};version='GLIBCXX_SAMSUNG_MATH_1.0'
symbols=subprocess.check_output(['readelf','-W','--dyn-syms',str(a.binary)],text=True)
imports={m.group(1) for m in re.finditer(r'\bUND\s+(\w+)@'+re.escape(version)+r'\b',symbols)}
missing=required-imports
if missing:raise SystemExit('Missing private-version imports: '+', '.join(sorted(missing)))
records=[]
for line in a.bindings.read_text().splitlines():
 m=re.search(r'binding file (.*?) \[.*?\] to (.*?) \[.*?\]:.*?symbol `([^\x27]+)\x27 \[([^]]+)\]',line)
 if m and m[3] in required and m[4]==version:records.append(dict(consumer=m[1],provider=m[2],symbol=m[3],version=m[4]))
seen={r['symbol'] for r in records}
if required-seen:raise SystemExit('Missing observed bindings: '+', '.join(sorted(required-seen)))
if any(not r['provider'].endswith('/private/libstdc++.so.6') for r in records):raise SystemExit('Unexpected corrected-math provider')
with a.output.open('x') as f:json.dump(dict(binary=str(a.binary),private_version=version,imports=sorted(required),bindings=records,passed=True),f,indent=2);f.write('\n')
print('All eight private math imports and runtime providers verified')
