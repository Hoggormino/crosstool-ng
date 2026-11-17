# Private numerical corrections for the TV UI process

This optional profile keeps GCC 16.2.0, the framework base
`a4895d7fc49d5b423abc5f166895c80175019570`, and the exact source-built
binutils 2.17.50 / glibc+ports 2.5.90 snapshots from the math-header profile.
It corrects selected runtime operations in **private libstdc++**, selected by
`--enable-libstdcxx-samsung-math`. The option defaults to no. It does not replace
firmware libm, libc, loader or firmware C++ libraries.

Use `crosstool-gcc16-runtime-math.config` with a new build/install directory.
The Samsung convenience wrapper defaults to
`/mnt/data/Projects/samsung-runtime-math/build-runtime-math-final/install`.
Its optional CMake profile is
`cmake/toolchains/armv6-samsung-gcc16-runtime-math-worker.cmake`.
Rebuild the TV UI process and its modern objects with the matching private
runtime bundle. Vendor-facing modules keep the working GCC 4.2 SDK and EABI4
checks. This separate TV UI process profile still emits EABI5 with base PCS.

## Implementation and provider selection

GCC package patch 0032 adds one opt-in libstdc++ source, a configure ABI check,
per-source floating-point options, and a private GNU symbol-version node.
It exports `fma`, `fmaf`, `fmal`, `logb`, `logbf`, `logbl`, `nearbyintf` and
`feupdateenv` as `GLIBCXX_SAMSUNG_MATH_1.0`. These are C ABI entry points, used
by the standard C++ interfaces and compiler builtins when they emit calls.
The normal g++ driver places libstdc++ before libm; new references can therefore
bind explicitly to this private version. Validate actual imports and loader
bindings. Plain C/gcc programs keep the original libm providers. An existing
binary requesting a GLIBC_2.4 math symbol is not converted by this build.
Do not rely on arbitrary library reordering or unversioned interposition.

The configure check rejects anything outside the verified little-endian ARMv6J
EABI, ARM instruction mode, base PCS, glibc 2.5, IEEE binary32 float and binary64
double/long-double ABI with hardware VFP arithmetic. Software-only arithmetic is
rejected because its helper routines do not honor active VFP rounding modes. It does not force capability macros or pretend a newer
libc version. The eight exports are absent with the default disabled option.

FMA uses musl's integer-significand algorithms, pinned with file hashes and
license in `runtime-math-source.json`. Only these implementations are adapted;
no musl libc, loader or separate math DSO is introduced. The signed 64-bit final
conversion is adapted for ARM: `__aeabi_l2d` has fixed nearest rounding, so two
exact 32-bit conversions and one VFP addition honor the active rounding mode.
A nonfinite addend is evaluated with z+z to quiet signaling NaNs. The source
compiles with `-frounding-math -ffp-contract=off -fno-fast-math -fno-builtin`.

`logb` decodes the IEEE exponent and leading subnormal bit, preserving zero,
infinity, NaN and exception behavior. Binary64 long-double entry points forward
to double implementations. `nearbyintf` uses the working double nearbyint
through a volatile function pointer; every float input and rounded finite
result fits double. `feupdateenv` composes the verified exception-test,
environment-restore and exception-raise primitives rather than the old stub.
No new syscall or kernel-helper requirement is introduced by these functions.

Retain `licenses.d/samsung-math.txt` with redistributed private runtimes, as well
as GCC COPYING3 and COPYING.RUNTIME. ct-ng collects this notice into its
installed `share/licenses/crosstool-ng/licenses.d/` directory.

## Build and maintainer tools

Use the existing Ubuntu 22.04 `tv-ui-ctng:jammy` image. Network-disabled target
compilation uses no external OE sysroot. The exact OE runtime is mounted
read-only for separate validation only. All old prefixes and application builds
remain preserved. No TV operation is part of this work.

GCC's generated files are regenerated using project-local Autoconf 2.69 and
Automake 1.15.1, not the image's newer versions. Official GNU archive SHA256s:

* autoconf-2.69.tar.xz:
  64ebcec9f8ac5b2487125a86a7760d2591ac9e1d3dbd59489633f9de62a57684
* automake-1.15.1.tar.xz:
  af6ba39142220687c500f79b4aa2f181d9b24e4f8d8ec497cea4ba26c64bedaf

From the patched GCC source, run autoconf, autoheader and
`automake --foreign --add-missing src/c++11/Makefile` in libstdc++-v3.
Retain the existing generated-only package patch 0026 libtool guard when
regenerating configure. No host package installation is required for normal
builds; the release patch includes the generated files.

## Validation scope

Portable numerical sources are in `math-inventory/numerics/`; the Samsung
project mirrors them under `tools/sdk/modern/numerics/`. MPFR 4.2.2 / MPC 1.4.1
are host-only references. Owned runtime inputs prevent constant folding.
Tests cover exact values and exception flags, all four rounding modes,
binary32/binary64, signaling NaNs, std/global/builtin/function-pointer entry
points, and environment restoration/thread isolation. A 31,140-case focused
suite uses seed 0x1136f5a. Forty-five finite tininess-boundary flag cases exclude
only FE_UNDERFLOW, because before/after-rounding detection differs; their values
and other flags remain checked. This is a measured subset, not exhaustive
floating-point conformance or a proof of every signaling-NaN/errno behavior.

The earlier 5,670-case broad and 5,184-case UI-range suites remain separate.
Gamma accuracy and complex inverse/extreme-value defects are retained. The raw
C cproj defect remains; std::proj keeps the previous correct fallback. QEMU ARM1136
runs and uname overrides do not emulate the TV's Linux 2.6.18_SELP kernel.
Hardware admission belongs to the TV agent under the shared lock.

## Integration preflight

A separately built target libstdc++ passes all 31,140 focused value cases and
20,268 finite FMA flag comparisons (45 underflow-tininess bit exclusions) with
both rebuilt and OE reference libc. The 88 normal-entry checks and all 13
floating-environment/thread checks also pass with both. ELF imports and loader
bindings require the private version, and the target closure/provider audit
passes. These are integration diagnostics; the full source toolchain build and
release validation are recorded separately below when complete.

The unchanged-runtime control has 10,804 value failures (4,132 FMA; 6,672 logb),
2,977 finite FMA flag failures and eight nearbyint exception findings in this
expanded dataset. Initial diagnostic failures are retained: a macro-prefix
mismatch produced an empty source file, and a missing link-time .so symlink
selected the baseline library. Neither failure was accepted as a passing result.
