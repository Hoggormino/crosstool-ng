# Samsung B-series exact snapshots

This integration targets a separate worker process. Keep the reference GCC 4.2
SDK for vendor-facing in-process modules. No firmware runtime replacements are
installed by this build.

`prepare.py` verifies official Sourceware commit/tree objects and all copied OE
inputs, then replays the recipe's complete ordered source preparation. Inputs
are from OE commit e9fcef71f94fb4e76c6e8d992b7936f8d5fa8632. Their paths,
patch order, strip levels and hashes are in `oe-manifest.json`. GNU patch's
original default fuzz allowance (2) is retained for the OE stack; offsets/fuzz
are recorded in the preparation log. Compatibility patches are a separate
layer under `patches/`. Prepared directories are supplied through HEAD's custom
source support, which deliberately does not apply package patches itself.

The added version descriptors describe the snapshots for HEAD's milestone
logic; they are not substitutes for preparation. Do not select release tarball
retrieval for these snapshots. The sample selects the prepared directories.
GCC 8.3.0 package patches/checksums are restored from the 1.24.0 tag, while the
framework remains pinned to HEAD a4895d7fc49d5b423abc5f166895c80175019570.
The special 8.3 selector coexists with HEAD's normal major-version 8 selector.

See the Samsung project's `docs/sdk-modern-ctng.md` for commands, build evidence,
ABI boundaries and remaining limitations.

## Build without the OE SDK

The integration carries all OE patch/header/helper inputs with hashes. The
working OE sysroot is not a build input. Download only the three pinned Git
objects and the original Linux 2.6.18 archive into a new cache:

```sh
# From this implementation checkout (see the Samsung report for exact commits):
python3 contrib/samsung-b-series/fetch.py /absolute/new-build/sources
curl -fL https://cdn.kernel.org/pub/linux/kernel/v2.6/linux-2.6.18.tar.bz2 \
  -o /absolute/new-build/linux-2.6.18.tar.bz2
python3 contrib/samsung-b-series/prepare.py \
  --sources /absolute/new-build/sources --output /absolute/new-build/prepared \
  --linux-archive /absolute/new-build/linux-2.6.18.tar.bz2
```

Preparation refuses an existing output directory and verifies the kernel archive
hash. Its receipt records new Git-archive hashes, source trees, every applied
compatibility patch and hashes of the complete prepared contents.

`Dockerfile` provides an independent Ubuntu 22.04 build image, without needing
an OE SDK image. Build it with your UID/GID, bootstrap/configure ct-ng with
`--enable-local`, and mount this checkout at `/ctng`. For a Git worktree, also
mount its `git rev-parse --git-common-dir` at its original absolute path,
read-only, during framework bootstrap so `git describe` can report its version.
Copy `crosstool.config` into a **new** build directory as `.config`; run
`/ctng/ct-ng olddefconfig` and `/ctng/ct-ng source` there with networking, then
`/ctng/ct-ng build` with networking disabled. Mount the build directory at the
same absolute path in the container. Installation is isolated at `BUILD/install`.
Run as the unprivileged builder; the sample does not allow building as root.

The assembler backports can be checked without executing ARM code:

```sh
python3 /ctng/contrib/samsung-b-series/check-assembler.py \
  --prefix BUILD/install --output BUILD/new-assembler-results
```

This profile emits EABI5 when driven by GCC 8.3, while the snapshot assembler's
standalone default is EABI4. Keep it separate from vendor-module SDK profiles.
No flags are rewritten to mask that distinction. Use `-gdwarf-2` for debugging
with the old binutils DWARF reader; GCC 8 otherwise defaults to a newer debug
format. Debug format does not change the target calling convention or kernel.

## Verified checkpoint

The complete four-job source build passed on 16 November 2026 in 20 minutes
39 seconds. GCC 8.3.0, its private libstdc++/libgcc/libatomic, the exact prepared
libc/ports snapshots, and Linux 2.6.18 headers were built into a new prefix.
The working OE target sysroot was not mounted or used as a compiler build input.

Owned C/C++17 probes pass under ARM1136 QEMU with both the rebuilt libc and the
preserved OE reference libc. They cover C startup/allocation/files, softfp calls
across translation units and into libm, formatting/conversions, optional,
variant, string_view, structured bindings, constexpr, allocated STL lifetimes,
exception cleanup, RTTI across translation units, pthread/std::thread, contended
static initialization, TLS destructors and 32-bit atomics. 64-bit std::atomic
operations pass through a non-lock-free private-libatomic fallback. The current
RmlUi Core checkpoint c29f20d73ec9c563af6752c87283b468237201be compiled/linked
and passed Core initialization, Variant use and shutdown with both libc sets.
Samples/backends, FreeType, Lua, SVG and Lottie were disabled; standard containers
were enabled. This does not validate graphics hardware or proprietary objects.

`check-runtime.sh PREFIX NEW_RESULTS` builds and executes the owned probes in
the supplied container. Run it with networking disabled and a private writable
result directory. This is userspace execution against the host kernel, not TV
kernel emulation. The Samsung project keeps the fuller ELF/provider/binding
receipts, RmlUi consumer and optional CMake worker profile.

Two important failures drove real target fixes: the 2007 assembler's draft VFP
UAL encodings produced inaccurate sqrt results, and linker section GC discarded
live ARM unwind tables from libstdc++. The arithmetic/conversion patch matches
independent instruction encodings; the EHABI mark-pass backport restores dynamic
exception handling. Neither fix changes ELF flags or substitutes newer sources.

Unsupported/unverified facilities remain explicit: legacy 64-bit __sync helpers
require kuser version 5 (absent from the standard 2.6.18 reference), while the
validated std::atomic64 path uses mutexes. GNU-unique symbols, IFUNC target
variants, LTO and optional sanitizer/OpenMP/SSP/quadmath/VTV/Cilk/MPX/ITM libraries
are not part of this profile. Newer GCC versions and optional standard-library
facilities such as filesystem are not certified by this checkpoint. Keep the
old SDK for in-process vendor modules; C++ objects/exceptions stay within the
owned worker and its private runtime. A C++11 ABI=0 switch does not establish
vendor compatibility. No TV operations were performed.

The portable optional CMake profile is `armv6-worker.cmake`; set
`-DSAMSUNG_MODERN_PREFIX=BUILD/install`. The current Core consumer is reproducible
from this checkout too:

```sh
python3 contrib/samsung-b-series/fetch_rmlui.py BUILD/RmlUi
cmake -S contrib/samsung-b-series/rmlui -B BUILD/rmlui-build -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/contrib/samsung-b-series/armv6-worker.cmake" \
  -DSAMSUNG_MODERN_PREFIX=BUILD/install -DRMLUI_SOURCE=BUILD/RmlUi \
  -DCMAKE_BUILD_TYPE=Release
cmake --build BUILD/rmlui-build --target rmlui-probe -j4
```

Use absolute BUILD paths. `validation/` holds the compact compiler/ABI report,
owned execution summary, assembler checks and exact OE install replay receipt.
Full logs/binaries remain in the Samsung workspace evidence paths listed there.
The generic ARM unwinder retains dormant register-bank support for VFPv3/iWMMX;
those frame classes are outside this worker contract. ARM1136-owned paths pass,
and the source/ISA limitations remain part of later hardware admission.
