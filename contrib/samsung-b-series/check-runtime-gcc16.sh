#!/bin/bash
# Additional owned C++20/23 checks for the GCC 16 worker variant.
set -euo pipefail
samsung_support=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
"$samsung_support/check-runtime.sh" "${1:?install prefix}" "${2:?new results directory}"
samsung_prefix=$(cd "$1" && pwd -P)
samsung_result=$(cd "$2" && pwd -P)
samsung_triplet=arm-samsung-linux-gnueabi
samsung_sysroot="$samsung_prefix/$samsung_triplet/sysroot"
"$samsung_prefix/bin/$samsung_triplet-g++" -O2 -g -gdwarf-2 -std=c++23 -fno-gnu-unique -pthread \
    "$samsung_support/probes/probe_recent.cpp" -Wl,--hash-style=sysv -o "$samsung_result/cxx23-probe"
cd "$samsung_result/run"
timeout 45s qemu-arm -cpu arm1136 -r 2.6.18 -strace -L "$samsung_sysroot" \
    -E "LD_LIBRARY_PATH=$samsung_prefix/$samsung_triplet/lib:$samsung_sysroot/lib:$samsung_sysroot/usr/lib" \
    "$samsung_result/cxx23-probe" >"$samsung_result/cxx23-probe.stdout" 2>"$samsung_result/cxx23-probe.stderr"
cat "$samsung_result/cxx23-probe.stdout"
