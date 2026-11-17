#!/usr/bin/env python3
"""Prove Annex G sign allowances do not admit finite overflow or wrong zeros."""
import json,struct,subprocess,tempfile
from pathlib import Path
here=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='complex-policy-') as tmp:
 p=Path(tmp);cases=0
 for prec in [0,1,2]:
  b=lambda x:int.from_bytes(struct.pack('<f' if prec==0 else '<d',x),'little')
  tests=[('finite_overflow','cacos',2.,1.,.5,-.25,float('inf'),-.25,False),
         ('zero_sign','casinh',0.,0.,0.,0.,-0.,0.,False),
         ('permitted_infinity_sign','casinh',float('nan'),-float('inf'),float('inf'),float('nan'),-float('inf'),float('nan'),True),
         ('wrong_category','casinh',float('nan'),float('inf'),float('inf'),float('nan'),0.,float('nan'),False),
         ('specified_infinity_sign','cacos',float('nan'),float('inf'),float('nan'),-float('inf'),float('nan'),float('inf'),False)]
  for name,fn,x,y,er,ei,ar,ai,should_pass in tests:
   case=dict(id=0,function=fn,precision=prec,mode=0,bits=[b(x),b(y),0,0],n=0,kind='complex',tag=name)
   (p/'cases.json').write_text(json.dumps(dict(cases=[case])))
   (p/'reference.tsv').write_text(f'0 {b(er):016x} {b(ei):016x} 0 256\n')
   (p/'actual.tsv').write_text(f'0 0 {b(ar):016x} {b(ai):016x} 0 0 0 0\n')
   (p/'receipt.json').write_text(json.dumps(dict(exit=0,runtime_bytes_unchanged=True,stdout=str(p/'actual.tsv'))))
   output=p/f'{prec}-{name}.json'
   r=subprocess.run(['python3',str(here/'analyze.py'),'--cases',str(p/'cases.json'),'--reference',str(p/'reference.tsv'),'--receipt',str(p/'receipt.json'),'--output',str(output),'--strict'],capture_output=True,text=True)
   assert (r.returncode==0)==should_pass,(prec,name,r.stdout,r.stderr);cases+=1
 print(cases,'complex-policy positive/negative fixtures passed')
