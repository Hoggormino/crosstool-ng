#!/usr/bin/env python3
"""Replay pinned OE source preparation, without accessing the working OE SDK."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
SOURCES = {
    'binutils': ('138bc74f170158c175024317a9ccee37aa7cf617', '5a90a09425544931548cc8de6b0d2391badb67bb'),
    'glibc': ('371f84a4dca19f1416c3f28db9980539d2f62905', '54dbb78b9b99c131340f95eab844f4f83fb5d3aa'),
    'glibc-ports': ('908afa831ca4403a689304a86e2014b4baa66366', 'b4820db599b0f60aea688472de218ab5454d5e07'),
}

def run(*cmd, **kw):
    return subprocess.run([str(x) for x in cmd], check=True, **kw)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sources', type=Path, required=True, help='Directory of bare Sourceware repositories')
    ap.add_argument('--output', type=Path, required=True, help='New directory, must not exist')
    ap.add_argument('--linux-archive', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True)  # Deliberately refuse existing output.
    receipt = {'sources': [], 'oe': json.loads((HERE/'oe-manifest.json').read_text())}
    for name, (commit, tree) in SOURCES.items():
        repo = args.sources / (name + '.git')
        actual = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', commit+'^{tree}'], text=True).strip()
        if actual != tree:
            raise RuntimeError('Unexpected tree for '+name)
        url = subprocess.check_output(['git', '-C', str(repo), 'remote', 'get-url', 'origin'], text=True).strip()
        if url != 'https://sourceware.org/git/'+name+'.git':
            raise RuntimeError('Expected official Sourceware remote: '+name)
        archive = args.output/(name+'-'+commit+'.tar')
        with archive.open('wb') as f:
            run('git', '-C', repo, 'archive', '--format=tar', '--prefix='+('glibc/ports/' if name=='glibc-ports' else name+'/'), commit, stdout=f)
        with tarfile.open(archive) as tf:
            tf.extractall(args.output)
        receipt['sources'].append(dict(name=name, url=url, commit=commit, tree=tree, archive=archive.name, sha256=sha(archive)))
    if sha(args.linux_archive) != 'c95280ff6c5d2a17788f7cc582d23ae8a9a7ba3f202ec6e4238eaadfce7c163d':
        raise RuntimeError('Linux 2.6.18 archive checksum mismatch')
    with tarfile.open(args.linux_archive) as tf:
        tf.extractall(args.output)
    (args.output/'linux-2.6.18').rename(args.output/'linux')
    # do_munge runs after unpack, before any OE patches.
    g = args.output/'glibc'
    arm = g/'ports/sysdeps/unix/sysv/linux/arm'
    shutil.rmtree(arm/'linuxthreads')
    (arm/'linuxthreads').symlink_to('nptl')
    for src, dest in [('nptl/sysdeps/pthread/bits/sigthread.h','sigthread.h'), ('sysdeps/unix/sysv/linux/i386/bits/wchar.h','wchar.h'), ('sysdeps/wordsize-32/bits/wordsize.h','wordsize.h')]:
        shutil.copyfile(g/src, arm/'bits'/dest)
    inputs = receipt['oe']['inputs']
    for entry in inputs:
        f = HERE/entry['path']
        if sha(f) != entry['sha256']:
            raise RuntimeError('OE input changed: '+str(f))
        if f.name.startswith('generic-bits_'):
            shutil.copyfile(f, arm/'bits'/f.name.replace('generic-bits_', ''))
    for f in sorted((g/'bits').glob('*.h')):
        if f.name in ('local_lim.h','errno.h'):
            continue
        if not any((g/d/f.name).exists() for d in ('ports/sysdeps/unix/sysv/linux/arm/bits','ports/sysdeps/arm/bits','sysdeps/unix/sysv/linux/bits','sysdeps/ieee754/bits')):
            shutil.copyfile(f, arm/'bits'/f.name)
    for name in ('libc-lock.h','fenv.h','utmp.h'):
        (arm/'bits'/name).unlink(missing_ok=True)
    for entry in inputs:
        if entry['patch']:
            run('patch','--batch','--fuzz=2','-p'+str(entry['strip']),'-i',HERE/entry['path'],cwd=args.output/entry['package'])
    # OE do_configure invokes gnu-configize. Its traced auxiliary destinations
    # are the binutils top directory and glibc/scripts; use the pinned OE files.
    for entry in receipt['oe']['gnu_config']['files']:
        source = HERE/entry['path']
        if sha(source) != entry['sha256']:
            raise RuntimeError('GNU config input changed: '+str(source))
        for destination in entry['destinations']:
            target = args.output/destination
            shutil.copyfile(source, target)
            target.chmod(0o755)
    # Host/compiler compatibility patches are kept separate from the OE changes.
    for package in ('binutils','glibc','linux'):
        for patch in sorted((HERE/'patches'/package).glob('*.patch')):
            run('patch','--batch','--fuzz=0','-p1','-i',patch,cwd=args.output/package)
            receipt.setdefault('compatibility_patches', []).append(dict(package=package,path=str(patch.relative_to(HERE)),sha256=sha(patch)))
    # Custom-source copies bypass CT_DoExtractPatch's generated-file timestamp
    # repair. Keep the audited generated scripts newer than their patched inputs;
    # modern host Autoconf must not regenerate this 2007 build system.
    for package in ('binutils', 'glibc', 'linux'):
        for name in ('aclocal.m4', 'config.h.in', 'Makefile.in', 'configure', 'preconfigure'):
            for path in sorted((args.output/package).rglob(name)):
                if path.is_file():
                    os.utime(path, None)
    # Hash the effective prepared source contents, including executable bits
    # and link destinations, independently of archive metadata and timestamps.
    receipt['prepared_trees'] = {}
    for package in ('binutils', 'glibc', 'linux'):
        digest = hashlib.sha256()
        root = args.output/package
        for path in sorted(root.rglob('*')):
            rel = str(path.relative_to(root))
            if path.is_symlink():
                value = ['symlink', rel, os.readlink(path)]
            elif path.is_file():
                value = ['file', rel, bool(path.stat().st_mode & 0o111), sha(path)]
            else:
                continue
            digest.update((json.dumps(value, separators=(',', ':'))+'\n').encode())
        receipt['prepared_trees'][package] = digest.hexdigest()
    (args.output/'source-preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__ == '__main__':
    main()
