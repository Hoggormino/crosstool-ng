#!/usr/bin/env python3
"""Produce a compact capability table from the immutable probe receipts."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from math_inventory_catalog import SCALAR
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--build',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();a.output.mkdir(parents=True)
receipts={label:json.loads((a.build/(label+'-v2')/'inventory.json').read_text()) for label in ('gcc16','gcc8')}
oe={label:json.loads((a.build/('oe-links-'+label)/'oe-links.json').read_text()) for label in receipts}
providers=json.loads((a.build/'gcc16-v2/providers.json').read_text())['symbols']
for r in oe.values(): assert len(r['tests'])==237 and all(x['exit']==0 for x in r['tests'])
tests={label:{x['id']:x for x in r['tests']} for label,r in receipts.items()}
assert tests['gcc16'].keys()==tests['gcc8'].keys()
index={(x['section'],x['family'],x['precision'],x['form']):x for x in receipts['gcc16']['tests']}
oe_index={x['id']:x for x in oe['gcc16']['tests']}
rows=[]
for case in receipts['gcc16']['tests']:
    if case['form']!='abi_decl_c':continue
    symbol=case['c_symbol_hint'];section=case['section'];family=case['family'];precision=case['precision']
    native=index[(section,family,precision,'c_header')]
    std_section='cmath' if section=='math_c' else 'complex_cpp'
    std_family=family if section=='math_c' else {'cabs':'abs','carg':'arg','creal':'real','cimag':'imag'}.get(family,family[1:] if family.startswith('c') and family not in ('conj','cproj') else family)
    if family=='cproj':std_family='proj'
    cpp=index.get((std_section,std_family,precision,'std_overload' if section=='math_c' else 'std_complex'))
    named=index.get(('cmath',family,precision,'std_named')) if section=='math_c' else None
    if precision=='double': named=named or cpp
    if family=='nan': cpp=named
    vendor=[x for x in providers.get(symbol,[]) if x['provider'].startswith('oe-')]
    assert vendor and case['status']=='linked' and symbol in case['emitted_undefined_symbols']
    aliases=[]
    if precision=='long double':
        for x in vendor:
            for y in providers.get(family,[]):
                if x['provider']==y['provider'] and x['address']==y['address'] and x['version']==y['version']:aliases.append(family)
    if native['compile_exit']:
        remedy='Backport public long-double declarations/redirections; reconfigure libstdc++; no implementation gap observed.'
    elif cpp and cpp['status']=='declaration_failed':
        remedy='Repair grouped C99 feature detection via target headers, then reconfigure libstdc++; C interface already links.'
    else:remedy='No remedy needed for this tested C/overload interface.'
    rows.append(dict(section=section,family=family,precision=precision,c_symbol=symbol,
                     c_declaration=native['compile_exit']==0,c_header_link=native['status'],
                     exact_symbol_rebuilt_link=case['status']=='linked',exact_symbol_oe_link=oe_index[case['id']]['exit']==0,
                     emitted_symbol=symbol,oe_exports=vendor,oe_alias_of_double=sorted(set(aliases)),
                     cpp_overload=cpp['status'] if cpp else 'not sampled',cpp_named=named['status'] if named else 'not applicable',
                     cpp_emitted=cpp.get('emitted_undefined_symbols',[]) if cpp else [],
                     cpp_versioned_imports=[s for s in cpp.get('required_dynamic_symbols',[]) if s.split('@')[0]==symbol] if cpp else [],
                     private_cpp_exports=[x for x in providers.get(symbol,[]) if x['provider']=='private-libstdc++'],
                     c_probe_id=native['id'],abi_probe_id=case['id'],cpp_probe_id=cpp['id'] if cpp else None,proposed_remedy=remedy))
differences=[]
for key,x in tests['gcc16'].items():
    y=tests['gcc8'][key]
    if x['status']!=y['status']:differences.append({k:x[k] for k in ('id','section','family','form','precision')}|dict(gcc16=x['status'],gcc8=y['status']))
summary=dict(scope='Finite C++17/C99 declaration, type, emitted-symbol and link inventory; no numerical or ARM execution tests.',
             compiler_cases={k:dict(case_count=r['case_count'],counts=r['counts']) for k,r in receipts.items()},
             abi_symbol_count=len(rows),oe_link_count_per_compiler=237,
             hidden_c_declarations=[r['c_symbol'] for r in rows if not r['c_declaration']],
             ld_aliases=sum(bool(r['oe_alias_of_double']) for r in rows),
             cpp_type_mismatches=[{k:x[k] for k in ('id','family','precision','expected','actual_return_type')} for x in receipts['gcc16']['tests'] if x['status']=='wrong_return_type'],
             gcc_differences=differences,
             per_section={label:{section:dict(Counter(x['status'] for x in r['tests'] if x['section']==section)) for section in sorted({x['section'] for x in r['tests']})} for label,r in receipts.items()})
(a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(a.output/'capabilities.json').write_text(json.dumps(rows,indent=2)+'\n')
columns=['section','family','precision','c_symbol','c_declaration','c_header_link','exact_symbol_rebuilt_link','exact_symbol_oe_link','emitted_symbol','oe_version','oe_address','oe_alias_of_double','cpp_overload','cpp_named','cpp_versioned_imports','proposed_remedy']
with (a.output/'capabilities.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader()
    for row in rows:
        values={key:row.get(key) for key in columns};values['oe_version']=';'.join(sorted({x['version'] or '' for x in row['oe_exports']}));values['oe_address']=';'.join(sorted({x['address'] for x in row['oe_exports']}))
        values['oe_alias_of_double']=';'.join(row['oe_alias_of_double']);values['cpp_versioned_imports']=';'.join(row['cpp_versioned_imports']);writer.writerow(values)
short={'linked':'yes','declaration_failed':'missing','wrong_return_type':'wrong type','link_failed':'link failure'}
lines=['# Math capability table','', 'C99 scalar and complex functions, all three target precisions. `C decl` tests the native header; `ABI link` uses a separate explicit-prototype probe with a forced symbol relocation. Both rebuilt and preserved OE links pass for every row. No target execution or numerical accuracy claim is made.','', '| C symbol | C decl | OE symbol/version | Double alias | C++ overload | C++ named |','| --- | --- | --- | --- | --- | --- |']
for row in rows:
    versions=','.join(sorted({x['version'] or 'unversioned' for x in row['oe_exports']}))
    lines.append(f'| `{row["c_symbol"]}` | {"yes" if row["c_declaration"] else "hidden"} | `{versions}` | {",".join(row["oe_alias_of_double"]) or "—"} | {short.get(row["cpp_overload"],row["cpp_overload"])} | {short.get(row["cpp_named"],row["cpp_named"])} |')
(a.output/'capabilities.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
