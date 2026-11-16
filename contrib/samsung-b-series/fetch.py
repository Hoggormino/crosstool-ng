#!/usr/bin/env python3
"""Fetch exact Sourceware histories into a new toolchain cache."""
import argparse, json, subprocess
from pathlib import Path
import runpy
SOURCES = {name: value[0] for name, value in runpy.run_path(str(Path(__file__).with_name('prepare.py')))['SOURCES'].items()}
ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);a=ap.parse_args();a.directory.mkdir(parents=True,exist_ok=True)
rows=[]
for name, commit in SOURCES.items():
    url='https://sourceware.org/git/'+name+'.git';repo=a.directory/(name+'.git')
    if not repo.exists():
        subprocess.run(['git','init','--bare',str(repo)],check=True)
        subprocess.run(['git','-C',str(repo),'remote','add','origin',url],check=True)
    actual=subprocess.check_output(['git','-C',str(repo),'remote','get-url','origin'],text=True).strip()
    if actual!=url: raise RuntimeError('Refusing cache with unexpected remote: '+str(repo))
    subprocess.run(['git','-C',str(repo),'fetch','--depth=1','origin',commit],check=True)
    tree=subprocess.check_output(['git','-C',str(repo),'rev-parse',commit+'^{tree}'],text=True).strip()
    remote_head=subprocess.check_output(['git','ls-remote',url,'HEAD'],text=True).strip()
    rows.append(dict(package=name,url=url,commit=commit,tree=tree,remote_head=remote_head))
(a.directory/'sourceware-fetch.json').write_text(json.dumps(rows,indent=2)+'\n')
