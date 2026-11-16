#!/usr/bin/env python3
"""Owned regression checks for syntax backports; no target execution."""
import argparse,json,struct,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--prefix',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True)
assembler=a.prefix/'bin/arm-samsung-linux-gnueabi-as';objcopy=a.prefix/'bin/arm-samsung-linux-gnueabi-objcopy'
head='.syntax unified\n.arch armv6\n.fpu vfpv2\n.arm\n.text\n'
modern=head+'vmrs APSR_nzcv, FPSCR\nvmrs r0, FPSCR\nvmsr FPSCR, r0\nbx lr\n'
legacy=head+'fmstat\nfmrx r0, FPSCR\nfmxr FPSCR, r0\nbx lr\n'
cases={
    'vfp-modern':(modern,True,struct.pack('<IIII',0xeef1fa10,0xeef10a10,0xeee10a10,0xe12fff1e)),
    'vfp-legacy':(legacy,True,struct.pack('<IIII',0xeef1fa10,0xeef10a10,0xeee10a10,0xe12fff1e)),
    'fp-register-copy':(head+'vmov.f64 d7,d6\nvmov.f32 s15,s13\n',True,struct.pack('<II',0xeeb07b46,0xeef07a66)),
    'vfp-ual-semantics':(head+'vmla.f64 d0,d1,d2\nvmls.f64 d0,d1,d2\nvnmla.f64 d0,d1,d2\nvnmls.f64 d0,d1,d2\nvcmp.f64 d0,d1\nvcmpe.f64 d0,d1\nvmrs APSR_nzcv,FPSCR\nvsqrt.f64 d0,d1\nvneg.f64 d0,d1\nvabs.f64 d0,d1\nvcvt.f64.s32 d0,s0\nvcvt.s32.f64 s0,d0\nvdiv.f64 d0,d1,d2\n',True,struct.pack('<13I',0xee010b02,0xee010b42,0xee110b42,0xee110b02,0xeeb40b41,0xeeb40bc1,0xeef1fa10,0xeeb10bc1,0xeeb10b41,0xeeb00bc1,0xeeb80bc0,0xeebd0bc0,0xee810b02)),
    'inst-mapping':(head+'.word 0\n.inst 0xe7f000f0\nbx lr\n.thumb\n.inst 0xdeff\nbx lr\n',True,struct.pack('<IIIHH',0,0xe7f000f0,0xe12fff1e,0xdeff,0x4770)),
    'inst-nonconstant':(head+'.extern owned_external\n.inst owned_external\n',False,None),
    'inst-arm-width':(head+'.inst.n 0\n',False,None),
    'vmrs-invalid-control':(head+'vmrs r0, cpsr\n',False,None),
    'neon-outside-profile':(head+'vadd.i32 q0, q0, q1\n',False,None),
    'thumb2-outside-profile':(head+'.thumb\nmovw r0, #1\n',False,None),
}
rows=[]
for name,(source,accept,expected) in cases.items():
    src=a.output/(name+'.s');src.write_text(source);obj=a.output/(name+'.o')
    cmd=[str(assembler),str(src),'-o',str(obj)]
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    row={'name':name,'command':cmd,'exit':p.returncode,'expected_accept':accept,'diagnostic':p.stdout,'passed':(p.returncode==0)==accept}
    if p.returncode==0 and accept:
        binary=a.output/(name+'.bin');subprocess.run([str(objcopy),'-O','binary','-j','.text',str(obj),str(binary)],check=True)
        row['text_hex']=binary.read_bytes().hex();row['expected_text_hex']=expected.hex();row['passed'] &= binary.read_bytes()==expected
        row['symbols']=subprocess.check_output(['readelf','-Ws',str(obj)],text=True)
        row['undefined_symbols']=subprocess.check_output([str(a.prefix/'bin/arm-samsung-linux-gnueabi-nm'),'-u',str(obj)],text=True)
        row['passed'] &= not row['undefined_symbols'].strip()
        if name=='inst-mapping':
            row['passed'] &= all(s in row['symbols'] for s in ('$a','$d','$t'))
    rows.append(row)
(a.output/'results.json').write_text(json.dumps({'scope':'assembler source/byte checks; no native or QEMU execution','tests':rows},indent=2)+'\n')
print(json.dumps([{'name':r['name'],'passed':r['passed']} for r in rows],indent=2))
if not all(r['passed'] for r in rows):raise SystemExit(1)
