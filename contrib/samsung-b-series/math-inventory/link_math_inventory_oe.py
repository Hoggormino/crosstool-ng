#!/usr/bin/env python3
"""Link the exact-symbol C ABI probes against the preserved OE runtime."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import json
from pathlib import Path
import subprocess
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--inventory',type=Path,required=True)
ap.add_argument('--reference-sysroot',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--jobs',type=int,default=4)
a=ap.parse_args();a.output.mkdir(parents=True)
r=json.loads(a.inventory.read_text());compiler=Path(r['prefix'])/'bin/arm-samsung-linux-gnueabi-gcc'
def probe(case):
    obj=Path(case['source']).parent/'probe.o';exe=a.output/case['id'];mapfile=a.output/(case['id']+'.map')
    command=[str(compiler),'--sysroot='+str(a.reference_sysroot),str(obj),
             '-L'+str(a.reference_sysroot/'lib'),'-L'+str(a.reference_sysroot/'usr/lib'),
             '-Wl,--hash-style=sysv','-Wl,-Map,'+str(mapfile),'-lm','-o',str(exe)]
    p=subprocess.run(command,text=True,capture_output=True,timeout=60)
    (a.output/(case['id']+'.log')).write_text(p.stdout+p.stderr)
    loads=[line for line in mapfile.read_text().splitlines() if line.startswith('LOAD ')] if mapfile.exists() else []
    reference_libm=any(str(a.reference_sysroot)+'/' in line and 'libm.so' in line for line in loads)
    reference_libc=any(str(a.reference_sysroot)+'/' in line and 'libc.so' in line for line in loads)
    if p.returncode==0:assert reference_libm and reference_libc,loads
    return dict(id=case['id'],symbol=case['c_symbol_hint'],exit=p.returncode,command=command,
                reference_libm=reference_libm,reference_libc=reference_libc,loaded_files=loads,
                diagnostic=p.stderr if p.returncode else '')
cases=[x for x in r['tests'] if x['form']=='abi_decl_c'];assert all(x['status']=='linked' for x in cases)
with ThreadPoolExecutor(max_workers=a.jobs) as pool:rows=list(pool.map(probe,cases))
out=dict(label=r['label'],scope='Owned C ABI link checks only; explicit diagnostic prototypes; no ARM execution.',
         reference_sysroot=str(a.reference_sysroot),counts=dict(Counter(x['exit'] for x in rows)),tests=rows)
(a.output/'oe-links.json').write_text(json.dumps(out,indent=2)+'\n')
print(r['label'],len(rows),'OE links',out['counts'])
