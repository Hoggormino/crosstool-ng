#!/usr/bin/env python3
"""Check FMA final-operation flags; preserve finite tininess-boundary exclusions."""
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--reference',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
r=json.loads(a.receipt.read_text());assert r['exit']==0 and r['runtime_bytes_unchanged'];observed={int(x[0]):int(x[6]) for line in Path(r['stdout']).read_text().splitlines() if (x:=line.split())}
failures=[];count=0;boundaries=0
for line in a.reference.read_text().splitlines():
 i,want,mask=map(int,line.split());got=observed[i];count+=1;boundaries+=mask!=31
 if got&mask!=want&mask:failures.append(dict(id=i,expected=want,observed=got,mask=mask))
with a.output.open('x') as f:json.dump(dict(checked=count,tininess_boundary_exclusions=boundaries,failed=len(failures),failures=failures),f,indent=2);f.write('\n')
print('FMA flags',count,'checked;',len(failures),'failed;',boundaries,'tininess boundaries excluded')
if failures:raise SystemExit(1)
