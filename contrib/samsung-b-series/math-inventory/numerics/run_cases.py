#!/usr/bin/env python3
"""Execute owned math probes in disposable ARM1136 userspace emulation."""
import argparse,hashlib,json,subprocess,time,uuid
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--sysroot',type=Path,required=True);ap.add_argument('--results',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--image',default='tv-ui-ctng:jammy');a=ap.parse_args()
if a.output.exists():raise SystemExit('Refusing to overwrite receipt')
image=subprocess.check_output(['docker','image','inspect',a.image,'--format','{{.Id}}'],text=True).strip()
def hashes():
    files=list((a.results/'private').glob('*.so*'))
    files += [a.sysroot/'lib'/name for name in ['libc.so.6','libm.so.6','ld-linux.so.3','libpthread.so.0']]
    return {str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
before=hashes();name='samsung-math-'+uuid.uuid4().hex[:12]
cmd=['docker','run','--rm','--init','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','128','--memory','512m','--cpus','1','--tmpfs','/tmp:rw,nosuid,nodev,size=32m',
     '--mount','type=bind,source='+str(a.sysroot.resolve())+',target=/target,readonly','--mount','type=bind,source='+str(a.results.resolve())+',target=/probes,readonly',
     '--workdir','/tmp',image,'qemu-arm','-cpu','arm1136','-r','2.6.18','-L','/target','-E','LD_LIBRARY_PATH=/probes/private:/target/lib:/target/usr/lib','-E','LD_DEBUG=bindings:versions','/probes/math-numerics','/probes/vectors.tsv']
start=time.monotonic()
try:
    p=subprocess.run(cmd,capture_output=True,timeout=60)
    rc=p.returncode;stdout=p.stdout;stderr=p.stderr
except subprocess.TimeoutExpired as error:rc=None;stdout=error.stdout or b'';stderr=error.stderr or b''
finally:subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
output=a.output.with_suffix('.stdout');bindings=a.output.with_suffix('.bindings');output.write_bytes(stdout);bindings.write_bytes(stderr)
after=hashes();r=dict(command=cmd,image_id=image,exit=rc,elapsed_seconds=round(time.monotonic()-start,3),stdout=str(output),bindings=str(bindings),runtime_sha256=before,runtime_bytes_unchanged=before==after,executable_sha256=hashlib.sha256((a.results/'math-numerics').read_bytes()).hexdigest(),vectors_sha256=hashlib.sha256((a.results/'vectors.tsv').read_bytes()).hexdigest(),scope='Owned numerical tests. QEMU uses the host kernel; uname override does not emulate Linux 2.6.18_SELP.')
with a.output.open('x') as stream:json.dump(r,stream,indent=2);stream.write('\n')
print('exit',rc,'rows',len(stdout.splitlines()),'runtime unchanged',before==after)
if rc!=0 or before!=after:raise SystemExit(1)
