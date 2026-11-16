#!/usr/bin/env python3
"""Check safe unknown-type rejection and existing C++ version matching."""
import argparse
import json
from pathlib import Path
import subprocess

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--prefix', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
a = ap.parse_args()
a.output.mkdir(parents=True)
prefix = a.prefix.resolve() / 'bin' / 'arm-samsung-linux-gnueabi-'
def run(name, *args):
    p = subprocess.run([str(prefix) + name, *map(str, args)], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f'{name} exited {p.returncode}: {p.stderr}')
    return p.stdout
unknown = '_Z1fM1CKDoFivE'
known = '_ZSt11owned_probev'
assert run('c++filt', unknown).strip() == unknown
assert run('c++filt', known).strip() == 'std::owned_probe()'
source = a.output / 'owned.s'
source.write_text('''
.syntax unified
.text
.arm
.global _ZSt11owned_probev
.type _ZSt11owned_probev,%function
_ZSt11owned_probev:
 bx lr
.global _Z1fM1CKDoFivE
.type _Z1fM1CKDoFivE,%function
_Z1fM1CKDoFivE:
 bx lr
.section .note.GNU-stack,"",%progbits
''')
version = a.output / 'owned.ver'
version.write_text('CHECK_1 { global: extern "C++" { "std::owned_probe()"; }; local: *; };\n')
obj = a.output / 'owned.o'
lib = a.output / 'libowned.so'
run('as', '-mcpu=arm1136jf-s', '-mfpu=vfp', source, '-o', obj)
run('ld', '-shared', '--hash-style=sysv', '--version-script=' + str(version), obj, '-o', lib)
dynamic = subprocess.check_output(['readelf', '-W', '--dyn-syms', str(lib)], text=True)
assert known + '@@CHECK_1' in dynamic
assert unknown not in dynamic
(a.output / 'dynamic-symbols.txt').write_text(dynamic)
result = dict(unknown_type_rejected_safely=True, known_cpp_version_export=True,
              unknown_type_remains_local=True, unknown_symbol=unknown,
              limitation='This safety fix does not add demangling of new C++ type encodings.')
(a.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
