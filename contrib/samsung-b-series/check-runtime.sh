#!/bin/bash
# Execute owned programs only, preferably in the supplied network-disabled container.
set -euo pipefail
samsung_support=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
samsung_prefix=${1:?toolchain install prefix}
samsung_result=${2:?new result directory}
mkdir "$samsung_result"
samsung_result=$(cd "$samsung_result" && pwd -P)
samsung_prefix=$(cd "$samsung_prefix" && pwd -P)
samsung_triplet=arm-samsung-linux-gnueabi
samsung_cc="$samsung_prefix/bin/$samsung_triplet-gcc"
samsung_cxx="$samsung_prefix/bin/$samsung_triplet-g++"
samsung_sysroot="$samsung_prefix/$samsung_triplet/sysroot"
"$samsung_cc" -O2 -g -gdwarf-2 "$samsung_support/probes/probe.c" "$samsung_support/probes/fp.c" -lm -Wl,--hash-style=sysv -o "$samsung_result/c-probe"
"$samsung_cxx" -O2 -g -gdwarf-2 -std=c++17 -fno-gnu-unique -pthread "$samsung_support/probes/probe.cpp" "$samsung_support/probes/rtti.cpp" -Wl,--hash-style=sysv -o "$samsung_result/cxx17-probe"
"$samsung_cxx" -O2 -g -gdwarf-2 -std=c++17 "$samsung_support/probes/atomic64.cpp" -latomic -Wl,--hash-style=sysv -o "$samsung_result/atomic64-probe"
mkdir "$samsung_result/run"
cd "$samsung_result/run"
for samsung_probe in c-probe cxx17-probe atomic64-probe; do
    # The library path affects this emulated process only, never a TV/system shell.
    timeout 45s qemu-arm -cpu arm1136 -r 2.6.18 -L "$samsung_sysroot" \
        -E "LD_LIBRARY_PATH=$samsung_prefix/$samsung_triplet/lib:$samsung_sysroot/lib:$samsung_sysroot/usr/lib" \
        "$samsung_result/$samsung_probe" >"$samsung_result/$samsung_probe.stdout" 2>"$samsung_result/$samsung_probe.stderr"
    cat "$samsung_result/$samsung_probe.stdout"
done
# QEMU uses the host kernel; -r changes uname only. Native admission stays separate.
