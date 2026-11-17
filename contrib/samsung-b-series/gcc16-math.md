# GCC 16 math-header compatibility for the TV UI process

This pass repairs C/C++ math declarations, classification return types and the
C++ complex-projection implementation selection. **It does not upgrade the
TV's math library or establish complete numerical conformance.** The final isolated source build completed in 35 minutes 50 seconds and
its installed prefix passed the API/core/UI-range checks described below.
The TV interface is built by a separate agent. No TV operations are performed.

## Implementation

The framework remains crosstool-ng master a4895d7fc49d5b423abc5f166895c80175019570,
with GCC 16.2.0 and the same exact binutils 2.17.50, glibc/ports 2.5.90 snapshots,
OE preparation, Linux 2.6.18 headers and glibc minimum kernel 2.6.16.

* glibc patch 0005 adapts BZ 10103 to math.h and complex.h. Public consumers get
  long-double declarations while _LIBC builds retain suppression. The existing
  ARM binary64 aliases provide the implementations.
* glibc patch 0006 adapts the later C++11 classification guards. C and C++98 keep
  the old integer C interfaces. C++11+ no longer sees obsolete double isinf/isnan
  declarations, allowing libstdc++'s actual probes to choose bool overloads.
* GCC patch 0031 keeps the existing C++ projection fallback for ARM glibc 2.5.
  The old C cproj implementation computes stereographic coordinates even for
  finite inputs. Correcting detection otherwise selects that defective path.
  Availability flags remain configured normally; type layout is unchanged.

The first clean header build took 33:34.81 and passed all 1,267 inventory cases.
Both C99 math feature groups became enabled through real probes; obsolete
classification macros became undefined. No capability or libc-version macro is
forced. The projection regression was then isolated and fixed, with a second
clean source build (35:50.15) including all patches from the start. Both builds
use the exact legacy sources and no external target sysroot.

The focused header checks preserve C++98/C behavior, expose public long-double
interfaces, hide only the obsolete C++11 double classifications, avoid leaking
the precision marker and retain internal long-double suppression.

## Numerical method and results

Owned evaluators use volatile runtime inputs. Raw C ABI calls use explicit
symbol names and volatile function pointers. The C++ evaluator uses the standard
interfaces and checks exact return types. Tests run under qemu-arm -cpu arm1136
in network-disabled, read-only containers with private temporary directories.
No MPFR/MPC library is linked into an ARM executable.

The independent host reference uses pinned MPFR 4.2.2 and MPC 1.4.1. Directed
lower/upper evaluations are converted to target binary32/binary64; expectations
are accepted only when they agree. Precision increases from 256 to 1024/4096
bits if required. Exact bit stepping handles nextafter/nexttoward. Fifty-one
independent identities check the reference plumbing, including Gamma(30)=29!,
FMA cancellation powers of two, subnormal exponents and finite projection.

The curated dataset contains 5,670 cases over 57 scalar and 22 complex families,
plus predicates and comparisons. Float, double and binary64 long double are
included. It covers signed zero, quiet NaNs, infinity, subnormals, extreme values,
cancellation and selected rounding modes. It does not exhaust numerical domains,
signaling NaNs, all C++ overload combinations or special-function accuracy.

The separate seeded dataset contains 5,184 ordinary UI-range scalar cases.
All are within the engineering comparison budgets with both source-built and preserved OE libc in the final
C++ run. Functions include trigonometry, square root, powers/logarithms,
hypotenuse, remainders, rounding, absolute value, min/max and sign copying.
This result is specific to those inputs and says nothing about TV rendering.

Comparison budgets are exact for basic operations, four ULP for ordinary real
transcendentals, eight ULP for gamma, and sixteen ULP or a component error bounded
by sixteen epsilon times complex magnitude for complex functions. These are
engineering criteria, not standard-mandated universal accuracy guarantees.
NaN payloads/signs are ignored; min/max zero-sign choices are advisory.

### Known inherited limits

The unchanged C runtime produces 102 curated value/budget deviations, identically
with the source-built and preserved OE runtime. Corrected C++ projection removes
21, leaving 81 measured deviations and 32 nearbyintf exception-flag findings.
Some deviations are accuracy-budget outliers rather than outright wrong
mathematical values. The full results preserve every input and output.

| Facility | Observed behavior | Consequence |
| --- | --- | --- |
| fma/fmaf/fmal | Separate multiply/add; cancellation can return zero and intermediate overflow can return infinity | Fused semantics unavailable through the old library |
| logb on subnormals | Smallest float gives -126 instead of -149; double gives -1022 instead of -1074 | Exponent result is wrong in that range |
| Raw C cproj | Finite values changed; e.g. .5+.25i becomes about .7619+.3810i | C payload remains defective; std::proj now uses its correct fallback |
| Complex inverse/trigonometric edges | Signed-zero branch differences, lost tiny components, NaNs from large finite ctan/ctanh inputs | No blanket complex-numerical admission |
| tgamma/lgamma | Selected errors exceed the stated ULP budgets; Gamma(30) is about 44 ULP off | Accuracy limitations retained |
| nearbyintf | FE_INEXACT raised for some nonzero small inputs | Value checks pass, exception suppression does not |
| feupdateenv | Generic source is an unconditional failure stub | Combined environment update unsupported |

For example, fma(1+2^-27,1-2^-27,-1) should return exactly -2^-54; the old binary64
implementation returns zero. The float counterpart similarly loses -2^-26.
Equal double/long-double formats do not provide extra intermediate precision
that could repair fusion by a simple cast.

Save/restore, flag restoration, hold/clear, all four rounding modes and thread
isolation pass focused environment checks. feupdateenv and merged-flag checks
fail. The vector suite separately records nearbyintf's inexact behavior.

Before the projection correction, enabling C99 complex selection introduced
21 new failures compared with the old-header C++ control. The targeted fallback
removes all 21. Fifteen previously available complex comparison cases improve;
the mixed control also improves two hypothetical C ABI hypot cases whose std
names were unavailable before the header repair. New C99 APIs are compared with
raw C controls rather than claimed as previously working C++ interfaces.

## Integration boundary

The intended final install is
`/mnt/data/Projects/samsung-math-toolchain/build-gcc16-math-final/install`.
Use optional profile `cmake/toolchains/armv6-samsung-gcc16-math-worker.cmake`.
Existing SDK profiles, prefixes, downloaded sources, application builds and the
other agent's interface sources are preserved.

Rebuild the TV UI process and its modern objects with the matching private
libstdc++/libgcc/libatomic bundle. Improved detection removes redundant C math
fallback exports from private libstdc++; mixing an older modern binary with the
new runtime bundle is not a supported update path. The TV's loader/libc/libm and
firmware C++ libraries are never replaced. Vendor-facing in-process modules
retain the old SDK and EABI4 gates. This profile remains EABI5, ARMv6J, ARM mode,
VFPv2 and softfp/base PCS, with SysV hashes and no GNU-unique symbols.

The numerical restrictions above must be observed if the TV UI process uses
those APIs. There is no complete C++17/23/26 library-conformance claim. QEMU's
uname override is not Linux 2.6.18_SELP kernel emulation; later hardware
admission belongs to the TV agent under the shared lock.

## Reproduce the source build

For a standalone checkout, follow README.md with crosstool-gcc16-math.config.
The convenience-wrapper commands below run from the Samsung math worktree.
Portable numerical tools are in math-inventory/numerics/.

The prepared source/patch identities are in
[the source manifest](validation-gcc16-math/source-manifest.json).
The final build has 21 GCC package patches and 16 old-component compatibility
patches, with the complete OE layer recorded separately. The Ubuntu 22.04 build
image is tv-ui-ctng:jammy, ID
sha256:00bfd6fdb967da28b6d19c6e0a128b90f7be6f24422b4b57879a46beab3b736e.
Host GCC is 11.4; no host package was installed for this pass. Bootstrap the
framework as documented in the earlier SDK report/crosstool-ng support README.
Use an unused build path:

```sh
export SAMSUNG_CTNG_SOURCE=/mnt/data/Projects/crosstool-ng-samsung-math
export SAMSUNG_CTNG_BUILD="$PWD/build-math-reproduce"
mkdir "$SAMSUNG_CTNG_BUILD"
tools/sdk/modern/prepare-math.sh
tools/sdk/modern/ctng-math-container.sh /ctng/ct-ng build
SAMSUNG_RMLUI_TOOLCHAIN="$PWD/cmake/toolchains/armv6-samsung-gcc16-math-worker.cmake" \
  tools/sdk/modern/validate-gcc16.sh "$SAMSUNG_CTNG_BUILD" \
  "$SAMSUNG_CTNG_BUILD/validation"
```

Source retrieval needs networking; compilation defaults to network=none.
Numerical commands and the deliberately failing legacy checks are documented
in math-inventory/numerics/README.md (Samsung wrapper commands; portable numerical sources are included here).

## Final evidence

[Build/ABI report](validation-gcc16-math/build-report.json),
[core execution summary](validation-gcc16-math/validation-summary.json),
[all 1,267 API results](validation-gcc16-math/api-matrix.csv),
[UI numerical results](validation-gcc16-math/ui-reference-analysis.json),
[edge numerical findings](validation-gcc16-math/edge-reference-analysis.json),
and [private ABI changes](validation-gcc16-math/abi-comparison.json)
preserve concrete results. All 13 core closure artifacts and all nine numerical
closure artifacts pass the static ELF/provider checks against the OE reference.
The RmlUi Core initialize/Variant/shutdown consumer passes with both libc sets.
The C ABI export sets of libc/libm/libpthread/loader are unchanged. Private
libstdc++ adds 24 exports and removes 22 redundant C math fallback exports;
libgcc/libatomic export sets are unchanged. A clean consumer rebuild is required.

The full numerical suite is intentionally reported as not within its comparison
policy. Do not interpret successful compilation, process exit or the passing
UI-range subset as complete mathematical conformance.
