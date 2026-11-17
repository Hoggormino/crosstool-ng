# GCC 16 strict ARMv6 alignment: canonical and native verified

The GCC 16 Samsung samples now default to strict alignment. Application-only
flags do not repair private runtimes built with hardware unaligned access.
The historical complex-math handoff passed QEMU but faulted on the PS50B850
under SELP alignment policy 5 before main, in libstdc++ locale initialization.

The four-byte `money_base::pattern` is a char array with alignment 1. GCC's
ARMv6 default optimized its legitimate copy into `ldr r0, [r2]` from address
0x4017bb01. This build keeps the type/ABI unchanged and generates safe copies.
No kernel policy workaround or artificial ELF flag/attribute change is used.

## Default correction

Every GCC 16 sample adds `-mno-unaligned-access` to target flags and C++ runtime
flags. Both bootstrap and final GCC also use the supported configuration:

```
--with-specs=%{!munaligned-access:%{!mno-unaligned-access:-mno-unaligned-access}}
```

Ordinary C and C++ driver invocations therefore default to strict access.
The explicit unsafe override is retained only as a static negative control.
The portable CMake worker profile also supplies the strict flag. The complete
canonical build recompiles source libc, all private runtimes, static libgcc and
startup objects; no external target sysroot supplies the new libc.

The framework base remains a4895d7fc49d5b423abc5f166895c80175019570, the compiler
GCC 16.2.0, and the exact binutils/glibc/ports/kernel/OE source preparation is
unchanged. Target remains ARM1136JF-S/ARMv6J, ARM mode, VFPv2, little endian,
softfp/base PCS and EABI5. Vendor-facing modules keep the original GCC 4.2/EABI4
SDK. Historical installed prefixes remain preserved.

## Verified canonical build

The source build completed in 33 minutes 11 seconds wall time. Functional
alignment commit is e12b2778b2d5522492fbe68766e9653d9f38e5d1. The new install is:

`/mnt/data/Projects/samsung-strict-alignment/build-complex-math-final/install`

The matching stripped private bundle is in that build's `tv-ui-private-runtime`.
The Samsung workflow `tools/sdk/modern/build-gcc16-strict.sh` prepares a new
build, compiles it, runs core/RmlUi and all math checks, audits alignment, and
stages the bundle. It uses the existing pinned Ubuntu 22.04 image. The previous
SDK is mounted read-only only for post-build comparison, not compilation.

Host gates passed:

* 3,916 generated runtime objects: 3,563 libgcc, 245 libstdc++, 108 libatomic;
* strict C/C++ defaults/predefines and safe-versus-unsafe copy code generation;
* installed startup/static artifacts and exact private dynamic contracts;
* four byte-identical runtime feature headers and unchanged C-runtime contracts;
* core C/C++17, EH/RTTI, thread/static/TLS/atomics and RmlUi against both libcs;
* 31,140 scalar cases, 20,268 finite FMA flag comparisons and 30,936 complex cases,
  with the same documented nine gamma outliers and 45 FMA underflow-bit exclusions;
* both math ABI nodes and all 24 complex/eight scalar provider checks;
* stripped exports and allocated section bytes equal to the tested libraries.

The fully rebuilt pilot includes RmlUi, FreeType and QuickJS. All 244 generated
ARM objects and all 253 compile commands are strict. Its two QEMU modes return
BYE 0 and match all three original capture hashes. The original EABI4 presenter
is reused unchanged. QEMU is not SELP alignment emulation.

## Native policy-5 result

The user authorized device testing. The owned alignment probe exited 0 after
unaligned EABI helper offsets 0..7, 2,624 memcpy cases and classic monetary
patterns. Both C++ and QuickJS pilot modes then presented Home and Library,
accepted Enter/Right/Return/Exit, restored the display and unloaded normally.
Actual target worker/runtime and mapped-presenter hashes match the new bundle.
The stock process stayed PID 47 with identical start ticks.

Policy 5 was never changed. User/System/Skipped/Half/Word/DWord/Multi counters
were all 0 before launch and remained 0 after all cleanup. Active OSD plane 1
contains Home/Library; Home RGB pixels downsampled to the 320×180 canvas are
byte-identical to QEMU. This is native OSD/presentation and startup evidence,
not a seated physical-panel quality or sustained GUI-fluidity judgment.

After cleanup, one ordinary discrete Off request produced three offline samples
on ports 23/2323/52235. Melody Off was not changed. No system loader/libc/libm,
firmware library or exeDSP process was replaced/stopped.

An initial inactive-plane capture and a failed second-session checker are
preserved separately. The latter read an old LIVE_RETURN and caused a matching
normal Exit; no runtime fault or counter change occurred. Successful v2 runs
use current-session reads and both-plane capture. Old failed native evidence
is not relabeled as successful.

[Build report](validation-strict-alignment/build-report.json),
[source manifest](gcc16-strict-alignment-manifest.json),
[object/default audit](validation-strict-alignment/alignment-audit.json),
[native result and runtime hashes](validation-strict-alignment/native-summary.json),
[native Home](validation-strict-alignment/native-v2-home.png),
[native Library](validation-strict-alignment/native-v2-library.png),
[matching bundle](validation-strict-alignment/private-runtime-manifest.json)
and [standby receipt](validation-strict-alignment/standby.log) preserve the result.

The main-based evidence branch is `gcc16-native-alignment-evidence`, commit
87cd9c8 (full identity in the build report). It updates
`docs/gcc16-native-alignment-issue.md` and adds native receipts without absorbing
main's uncommitted pilot changes. Use the strict SDK worktree's current handoff
for new native consumers.

Gamma, original scalar hypotf/non-nearest-tan issues, dormant unwinder frame
classes and legacy __sync64 kuser requirements remain separate limitations.
This alignment fix does not certify every optional library facility.
