#!/usr/bin/env python3
"""Replay the reference recipe's post-compile header and installation preparation."""
import argparse,hashlib,json,shutil,struct,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
RPC=['bootparam_prot','nlm_prot','rstat','yppasswd','klm_prot','rex','sm_inter','mount','rusers','spray','nfs_prot','rquota','key_prot']
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--sysroot',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);a=ap.parse_args()
if a.receipt.exists():raise SystemExit('Refusing an existing OE completion receipt')
libc=a.sysroot/'lib/libc.so.6';data=libc.read_bytes()[:52]
if data[:7]!=b'\x7fELF\x01\x01\x01' or struct.unpack_from('<H',data,18)[0]!=40:
    raise SystemExit('Expected an isolated ARM target sysroot, not a host root')
if not (a.source/'ports/sysdeps/unix/sysv/linux/arm').is_dir():raise SystemExit('Expected the prepared ARM ports source')
manifest=json.loads((HERE/'oe-manifest.json').read_text())
def input_file(name):
    row=next(x for x in manifest['inputs'] if Path(x['path']).name==name)
    p=HERE/row['path']
    if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise RuntimeError('OE input hash mismatch: '+name)
    return p
rpcgen=shutil.which('rpcgen')
if not rpcgen:raise SystemExit('Missing host package rpcsvc-proto: rpcgen generates the reference RPC development headers')
a.receipt.parent.mkdir(parents=True,exist_ok=True)
rpcdir=a.source/'sunrpc/rpcsvc';target=a.sysroot/'usr/include/rpcsvc';target.mkdir(parents=True,exist_ok=True)
headers=[]
with tempfile.TemporaryDirectory(prefix='oe-rpc-headers-',dir=a.receipt.parent) as tmp:
    for name in RPC:
        header=rpcdir/(name+'.h');cmd=None
        if not header.exists():
            output=Path(tmp)/(name+'.h')
            cmd=[rpcgen,'-h',name+'.x','-o',str(output.resolve())]
            subprocess.run(cmd,cwd=rpcdir,check=True)
            shutil.copyfile(output,header)
        shutil.copyfile(header,target/header.name)
        headers.append(dict(name=header.name,sha256=hashlib.sha256(header.read_bytes()).hexdigest(),generation_command=cmd))
(a.sysroot/'etc').mkdir(exist_ok=True)
shutil.copyfile(input_file('ld.so.conf'),a.sysroot/'etc/ld.so.conf')
(a.sysroot/'usr/lib/locale').mkdir(parents=True,exist_ok=True)
supported=a.receipt.parent/'SUPPORTED'
subprocess.run(['make','-f',str(input_file('generate-supported.mk')),'IN='+str((a.source/'localedata/SUPPORTED').resolve()),'OUT='+str(supported.resolve())],check=True)
broken=['sid_ET','tr_TR','mn_MN','gez_ET','gez_ER','bn_BD','te_IN']
supported.write_text(''.join(line for line in supported.read_text().splitlines(True) if not any(name in line for name in broken)))
removed=[]
for rel in ['etc/rpc','usr/share/zoneinfo','usr/libexec/getconf']:
    p=a.sysroot/rel
    if p.is_symlink() or p.is_file():p.unlink();removed.append(rel)
    elif p.is_dir():shutil.rmtree(p);removed.append(rel)
receipt=dict(oe_commit=manifest['oe_commit'],rpcgen=subprocess.check_output([rpcgen,'--version'],text=True).strip(),headers=headers,ld_so_conf_sha256=hashlib.sha256((a.sysroot/'etc/ld.so.conf').read_bytes()).hexdigest(),supported_sha256=hashlib.sha256(supported.read_bytes()).hexdigest(),excluded_broken_locales=broken,removed=removed,scope='Isolated target sysroot only; no firmware or system-library changes')
with a.receipt.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('Completed reference OE post-build headers and installation preparation')
