# Private complex functions for the TV UI process

> Native-use correction: the historical build below is preserved QEMU/math
> evidence. Its private runtimes are not safe under SELP policy 5. Use a fresh
> [canonical strict-alignment build](strict-alignment.md) for native GCC 16 work;
> application flags alone do not repair the old shared libraries.

This optional profile extends the verified GCC 16.2.0 private math runtime.
The framework base remains current upstream HEAD
`a4895d7fc49d5b423abc5f166895c80175019570`. Binutils 2.17.50, glibc/ports
2.5.90-9.0.9, complete OE preparation, Linux 2.6.18 headers and minimum kernel
2.6.16 remain unchanged. No firmware loader, libc, libm or C++ library is replaced.

The sample is `crosstool-gcc16-complex-math.config`. Its matching Samsung prefix
is `/mnt/data/Projects/samsung-complex-math/build-complex-math-final/install`,
with optional CMake profile `armv6-samsung-gcc16-complex-math-worker.cmake`.
Use a new build/install directory. Preserve existing working SDK profiles and
rebuild modern consumers with the matching private runtime bundle.

## Implementation

GCC package patch 0033 adds a C implementation to libstdc++'s convenience
library. The C compiler preserves the GNU C complex calling convention; the
source is position independent. The existing opt-in
`--enable-libstdcxx-samsung-math` and its verified ARMv6J/VFP/base-PCS/binary32/
binary64 ABI check apply. With the option disabled, this source emits nothing.

Twenty-four C ABI symbols are exported privately at
`GLIBCXX_SAMSUNG_MATH_1.1`: cacos, cacosh, casin, casinh, catan, catanh, ctan and
ctanh, each at float/double/long-double precision. The adjacent cacosh operation
uses the same inverse-function implementation even though it had no failure in
the original small dataset. The previous eight scalar fixes keep their 1.0
version. New consumers must link the matching private libstdc++; old GLIBC-
versioned imports retain their original providers. Plain C/gcc behavior remains
unchanged. No additional math DSO is packaged.

The scaled inverse algorithms and tangent/hyperbolic-tangent implementation come
from FreeBSD lib/msun, pinned at
`1ddd5b301d273b62b2c0fa3c60c8cae8c9072dc3`.
[Source identities](complex-math-source.json) record its root tree, verified Git
blob IDs, SHA256s and adaptations. The two algorithm files retain their BSD-2-
Clause notices. The NaN-mixing expression retains the permissive Sun fdlibm
header notice; IEEE word-access shims use independent memcpy-based helpers.
`licenses.d/samsung-complex.txt` must accompany redistributed runtimes, along
with the earlier MIT math notice and GCC COPYING3/COPYING.RUNTIME.

Two concrete legacy scalar dependencies required adaptation. Owned probes show
hypotf overflowing for a finite pair near 6.45e37, and scalar tan(1) becoming
inaccurate outside nearest rounding. All new complex precisions therefore use
the binary64 algorithm internally, with float narrowing after computation.
Internal scalar calculations run in FE_TONEAREST; wrappers restore the caller's
mode before component conversion and preserve incoming exception flags. This
is a bounded-error transcendental implementation, **not correctly rounded
complex arithmetic in every mode**. Existing scalar functions are not replaced
by this patch.

ARM double and long double both have size 8, mantissa 53 and the same exponent
range; long-double wrappers do not lose precision. This selection is guarded by
the real ABI check, not just a version string or forced capability macro.

## Numerical validation

The isolated ARM prototype and integrated target libstdc++ diagnostics resolve
all 39 complex findings in the original 5,670-case suite. Only nine gamma
accuracy-budget outliers remain. All 30,936 expanded cases pass with both rebuilt
and preserved OE libc, as do 240 independent contract checks. All 24 imports and
observed runtime bindings use the private version. The diagnostic closure audit
passes and its library has no text relocations. Release admission below uses
the full source-built toolchain rather than this diagnostic library.

The expanded seed is 0x1136c017. Inputs cover signed branch approaches, normal
and subnormal components, ordinary and wide-exponent pairs, poles, scaling
crossovers, infinities and NaNs. Branch tests include all four rounding modes.
The existing budget remains 16 ULP per component or 16 epsilon times complex
magnitude. Finite zero signs remain strict. These are engineering comparison
criteria, not a universal conformance claim.

The independent host reference uses MPFR 4.2.2 and MPC 1.4.1, never linked into
ARM programs. It retains directed bounds and increasing precision. Two specific
reference cases need additional handling:

* At extreme finite arguments, MPC's finite exponent range can lose a small
  component's sign before target conversion. The reference uses an exponential
  magnitude bound and independent directed MPFR phase signs. Its 336 threshold
  cases agree with full high-precision MPC evaluation where exponent range
  suffices. Existing broad reference output remains byte-identical.
* [N3096 Annex G](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3096.pdf)
  preserves zero components in zero/nonfinite tangent cases where MPC returns
  two NaNs. It also explicitly leaves selected infinity signs unspecified when
  another input component is NaN. The comparison accepts only those sign
  alternatives. Fifteen positive/negative fixtures verify that finite overflow,
  incorrect zero signs, wrong categories and specified infinity signs still
  fail. No ABI gate is changed.

The full owned validation includes actual C++ overloads, GNU C ABI pointers,
branch signs, tiny components, finite saturation, rounding restoration,
preserved incoming flags and invalid-exception cases. Trapping environments,
all signaling-NaN payload choices and exhaustive errno behavior remain outside
this measured admission. Gamma functions and the newly observed original scalar
hypotf/tan limitations remain separate work.

No TV operation occurs. QEMU ARM1136 userspace execution and uname overrides do
not emulate Linux 2.6.18_SELP. Keep vendor-facing modules on the original SDK and
EABI4 gates; this TV UI process profile remains EABI5, ARM mode, VFPv2 and softfp/
base PCS with SysV hashes. The base [GCC 16](gcc16.md) and [private scalar math](runtime-math.md)
limits still apply, including dormant unwinder frame classes and kuser-helper
restrictions. Later native admission belongs to the TV agent.

## Verified source build and release

The full source-based toolchain build completed in 33 minutes 13 seconds wall
time with functional implementation commit
`22dc1c4b7d25fecff4f1446462c3f7a7462aafdd`. The fresh upstream HEAD check still
matches the pinned framework base. Preparation reproduces the same old-component
source trees as the preserved private-scalar profile. No external OE target
sysroot is used during the build; OE libc is mounted read-only for separate tests.

Both rebuilt and OE runtime sets pass:

* all 30,936 expanded complex cases and all 244 branch/ABI/environment/thread
  contract checks, including 2,000 concurrent complex calls;
* all 31,140 earlier focused scalar cases and 20,268 finite FMA flag checks,
  retaining the documented 45 underflow-tininess bit exclusions;
* all 5,184 ordinary UI-range cases, the earlier 88 entry-point checks, all 13
  floating-environment checks and 39 projection assertions;
* core C/C++17, exceptions/RTTI, pthread/static/TLS destruction, 32-bit atomics,
  mutex-backed 64-bit atomics, and the admitted C++20/23 wait/semaphore subset;
* the pinned RmlUi Core initialization/Variant/shutdown consumer after all 187
  build steps using the optional complex-math CMake profile.

All 1,267 API compile/link probes pass. All 237 forced C ABI symbols also link
against preserved OE libc/libm. The broad 5,670-case C++ suite now has **nine
gamma accuracy-budget deviations**, down from 48. All 39 prior complex deviations
are resolved without new broad-suite failures. The unchanged C-only control
retains 102 broad deviations and 32 nearbyintf flag findings.

The 13-artifact core closure, 10-artifact base numerical closure and 8-artifact
complex closure pass static ABI/ISA-attribute, interpreter, hash, relocation,
provider/version and GNU-unique checks with both runtime sets. Actual bindings
select all 24 new private symbols and all eight earlier scalar corrections.
There are no text relocations. Relative to the verified private-scalar profile,
libstdc++ adds precisely 24 functions plus their version node and removes
nothing. libc/libm/libpthread/loader and libgcc/libatomic export sets are unchanged.
All three packaged private libraries require only GLIBC_2.4 from target C
libraries; libstdc++ also uses GCC_3.0/3.3/3.4/3.5 from matching private libgcc_s.

The matching bundle is
`/mnt/data/Projects/samsung-complex-math/build-complex-math-final/tv-ui-private-runtime`.
It contains only the three private runtimes and their licenses/manifest. It is
byte-identical to the tested libraries. Rebuild consumers against the new prefix;
changing the runtime alone does not redirect old GLIBC-versioned math imports.

[Build/ABI report](validation-complex-math/build-report.json),
[source and patch manifest](gcc16-complex-math-manifest.json),
[API matrix](validation-complex-math/api-matrix.csv),
[complex numerical results](validation-complex-math/complex-analysis.json),
[remaining broad findings](validation-complex-math/edge-analysis.json),
[core receipts](validation-complex-math/validation-summary.json),
[fixed-precision reference comparison](validation-complex-math/saturation-reference-check.json)
and [private bundle hashes](validation-complex-math/private-runtime-manifest.json)
record the result. [Failure evidence](validation-complex-math/failure-index.json)
retains the initial expanded failures, scalar dependency diagnostics and source-
copy setup problem. The accidental generated-source symlink was restored
byte-for-byte with original mtimes before any diagnostic compilation; the
[restoration receipt](validation-complex-math/source-restore.json) records it.
The [outer-session observation](validation-complex-math/outer-session-observation.json)
retains a parent-tool status discrepancy; the separately recorded ct-ng
subprocess exited zero and the installed compiler passed the checks above.

Gamma accuracy and the original scalar hypotf/non-nearest-tan defects remain
recorded separately. This result is not blanket complex-function conformance,
correct rounding in every mode, or native TV/kernel admission. No TV operation
was performed; the other agent's interface sources/builds were not changed.
