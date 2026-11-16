#!/usr/bin/env python3
"""Inventory declarations, exact C++ overloads, emitted references and links.

All sources are owned probes. Nothing is executed on ARM, and no headers or
libraries in the compiler prefix are modified. Explicit C prototypes are used
only in separate diagnostic cases to test binary availability.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from math_inventory_catalog import HEADERS, body, catalog

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--prefix', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
ap.add_argument('--label', required=True)
ap.add_argument('--jobs', type=int, default=4)
ap.add_argument('--reference-sysroot', type=Path)
ap.add_argument('--limit', type=int, help='Small runner check before the full inventory')
a = ap.parse_args()
a.output.mkdir(parents=True)
root = a.output.resolve();prefix = a.prefix.resolve()
triplet = 'arm-samsung-linux-gnueabi-'
cc = prefix/'bin'/(triplet+'gcc');cxx = prefix/'bin'/(triplet+'g++')
nm = prefix/'bin'/(triplet+'nm')
started = time.monotonic()
def run(command, **kw):
    return subprocess.run(list(map(str,command)), capture_output=True, text=True, timeout=90, **kw)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
sysroot = Path(run([cc,'-print-sysroot']).stdout.strip())
predefines = run([cxx,'-std=c++17','-dM','-E','-x','c++','-include','cmath','-include','cfloat','/dev/null'])
(root/'predefines.txt').write_text(predefines.stdout)
compiler = run([cxx,'-v']);(root/'compiler.txt').write_text(compiler.stderr)
providers = []
search = [('rebuilt-libm',sysroot/'lib/libm.so.6'),('rebuilt-libc',sysroot/'lib/libc.so.6'),
          ('private-libstdc++',Path(run([cxx,'-print-file-name=libstdc++.so.6']).stdout.strip()))]
if a.reference_sysroot:
    search += [('oe-libm',a.reference_sysroot/'lib/libm.so.6'),('oe-libc',a.reference_sysroot/'lib/libc.so.6')]
provider_map = {}
for label,path in search:
    p = run(['readelf','-W','--dyn-syms',path]);assert p.returncode==0,p.stderr
    (root/(label+'.symbols')).write_text(p.stdout)
    count = 0
    for line in p.stdout.splitlines():
        f=line.split()
        if len(f)<8 or not f[0].endswith(':') or not f[0][:-1].isdigit() or f[6]=='UND': continue
        if f[4] not in ('GLOBAL','WEAK'): continue
        name,*version=f[7].replace('@@','@').split('@',1)
        provider_map.setdefault(name,[]).append(dict(provider=label,file=str(path),version=version[0] if version else None,address=f[1],type=f[3],binding=f[4]))
        count+=1
    providers.append(dict(label=label,file=str(path),sha256=sha(path),defined_dynamic_symbols=count))
(root/'providers.json').write_text(json.dumps(dict(files=providers,symbols=provider_map),indent=2)+'\n')

flags_cpp = ['-std=c++17','-O0','-fno-builtin','-fno-gnu-unique']
flags_c = ['-std=c99','-O0','-fno-builtin','-Werror=implicit-function-declaration']
pch = {}
for section,includes in HEADERS.items():
    cpp=section in ('cmath','complex_cpp','cfenv');compiler=cxx if cpp else cc
    header=root/(section+('.hpp' if cpp else '.h'));header.write_text(includes)
    flags=flags_cpp if cpp else flags_c
    p=run([compiler,*flags,'-x','c++-header' if cpp else 'c-header',header,'-o',str(header)+'.gch'])
    (root/(section+'.pch.log')).write_text(p.stdout+p.stderr)
    pch[section]=header if p.returncode==0 else None

cases=catalog()
if a.limit: cases=cases[:a.limit]
(root/'catalog.json').write_text(json.dumps(cases,indent=2)+'\n')
def probe(case):
    directory=root/case['id'];directory.mkdir()
    cpp=case['section'] in ('cmath','complex_cpp','cfenv')
    compiler=cxx if cpp else cc;flags=flags_cpp if cpp else flags_c
    header=HEADERS[case['section']]
    source=directory/('probe.cpp' if cpp else 'probe.c');obj=directory/'probe.o';exe=directory/'probe'
    text=header+case.get('prototype','')+body(case)
    source.write_text(text)
    command=[compiler,*flags]
    if pch[case['section']]:command+=['-include',pch[case['section']],'-Werror=invalid-pch']
    command+=['-c',source,'-o',obj]
    p=run(command);(directory/'compile.log').write_text(p.stdout+p.stderr)
    row=dict(case,source=str(source),source_sha256=sha(source),compile_command=list(map(str,command)),compile_exit=p.returncode)
    if p.returncode:
        row['status']='wrong_return_type' if re.search(r'error: static assertion failed[^\n]*return_type_mismatch',p.stderr) else 'declaration_failed'
        row['diagnostic']=p.stderr
        if row['status']=='wrong_return_type':
            source=directory/'call-only.cpp';source.write_text(header+body(case,check_type=False))
            retry=[compiler,*flags,'-c',source,'-o',obj]
            q=run(retry);row['call_only_compile_exit']=q.returncode
            (directory/'call-only.log').write_text(q.stdout+q.stderr)
            diagnostic = header+'template<class> struct owned_type;\n'+body(case,check_type=False).replace('volatile '+case['expected']+' result',f'owned_type<decltype({case["expression"]})> actual;\nvolatile '+case['expected']+' result')
            source=directory/'actual-type.cpp';source.write_text(diagnostic)
            q=run([compiler,*flags,'-fsyntax-only',source])
            (directory/'actual-type.log').write_text(q.stdout+q.stderr)
            found=re.findall(r'owned_type<([^>]+)>',q.stderr)
            row['actual_return_type']=found[0] if found else 'see actual-type.log'
        return row
    p=run([nm,'-u',obj]);assert p.returncode==0,p.stderr
    (directory/'undefined.txt').write_text(p.stdout)
    refs=[]
    for line in p.stdout.splitlines():
        fields=line.split()
        if fields:refs.append(fields[-1])
    row['emitted_undefined_symbols']=refs
    if case['form']=='abi_decl_c':
        assert case['c_symbol_hint'] in refs, ('Raw ABI symbol probe did not reference its symbol',case)
    row['symbol_provider_candidates']={symbol:provider_map.get(symbol,[]) for symbol in refs}
    command=[compiler,obj,'-Wl,--hash-style=sysv','-lm','-o',exe]
    p=run(command);(directory/'link.log').write_text(p.stdout+p.stderr)
    row.update(link_command=list(map(str,command)),link_exit=p.returncode,status='linked' if p.returncode==0 else 'link_failed')
    if p.returncode:row['diagnostic']=p.stderr
    else:
        row['elf_sha256']=sha(exe)
        dyn=run(['readelf','-W','--dyn-syms',exe]);assert dyn.returncode==0
        (directory/'dynamic-symbols.txt').write_text(dyn.stdout)
        row['required_dynamic_symbols']=[line.split()[7] for line in dyn.stdout.splitlines() if len(line.split())>=8 and line.split()[6]=='UND']
    return row

results=[]
with ThreadPoolExecutor(max_workers=a.jobs) as pool:
    tasks={pool.submit(probe,case):case['id'] for case in cases}
    for future in as_completed(tasks):
        results.append(future.result())
        if len(results)%50==0: print(a.label,len(results),'/',len(cases),dict(Counter(r['status'] for r in results)),flush=True)
results.sort(key=lambda x:x['id'])
receipt=dict(label=a.label,prefix=str(prefix),sysroot=str(sysroot),compiler_version=run([cxx,'-dumpfullversion']).stdout.strip(),
             elapsed_seconds=round(time.monotonic()-started,2),case_count=len(results),counts=dict(Counter(r['status'] for r in results)),
             scope='Owned compile/link inventory only; no ARM execution, numerical accuracy, fenv behavior or kernel compatibility claim.',
             flags_cpp=flags_cpp,flags_c=flags_c,providers=providers,tests=results)
(root/'inventory.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(a.label,'complete',receipt['counts'],flush=True)
