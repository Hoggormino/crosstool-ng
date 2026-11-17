# Owned numerical validation

These tools test the separate TV UI process's compiler/runtime profile in
ARM1136 QEMU. They perform no TV operation. A successful program execution is
separate from numerical correctness: the broad legacy edge suite has known
findings, while the ordinary UI-range suite passes its stated comparison policy.
Use analyze.py --strict for a failing exit status on deviations.

From the Samsung math worktree, after building a fresh source-based toolchain:

```sh
export SAMSUNG_CTNG_BUILD="$PWD/build-gcc16-math-final"
math_prefix="$SAMSUNG_CTNG_BUILD/install"
math_host_tools="$SAMSUNG_CTNG_BUILD/.build/arm-samsung-linux-gnueabi/buildtools"
python3 tools/sdk/modern/numerics/make_cases.py --output "$SAMSUNG_CTNG_BUILD/new-edge-vectors"
python3 tools/sdk/modern/numerics/make_ui_cases.py --output "$SAMSUNG_CTNG_BUILD/new-ui-vectors"
python3 tools/sdk/modern/numerics/make_runner.py --output "$SAMSUNG_CTNG_BUILD/math-runner.c"
```

Compile reference.cpp with the container's host g++, using
-I$math_host_tools/include -L$math_host_tools/lib -lmpc -lmpfr -lgmp and an
appropriate host runtime library path. The supplied image has the same host
compiler used for the pinned companion libraries. Run the host executable with
new-edge-vectors/reference-inputs.tsv and new-ui-vectors/inputs.tsv as standard
input, writing reference.tsv in each respective directory. Classification
expectations are derived directly from binary fields in analyze.py. Run
check_reference.py --vectors EDGE_DIRECTORY --output NEW_SANITY_JSON to verify
independent exact identities. No reference library is linked into target code.

Compile the target evaluator with:

```sh
tools/sdk/modern/ctng-math-container.sh \
  "$math_prefix/bin/arm-samsung-linux-gnueabi-g++" \
  -x c++ -DNUMERICS_STD -std=c++17 -O2 -frounding-math -fno-builtin \
  -fno-gnu-unique "$SAMSUNG_CTNG_BUILD/math-runner.c" -lm \
  -Wl,--hash-style=sysv -o "$SAMSUNG_CTNG_BUILD/math-numerics"
```

For each dataset, create an unused result directory containing that executable
as math-numerics, the dataset's inputs.tsv as vectors.tsv, and the matching
private libstdc++.so.6/libgcc_s.so.1/libatomic.so.1 copied from this compiler.
Keep COPYING3 and COPYING.RUNTIME with packaged runtimes. Run:

```sh
python3 tools/sdk/modern/numerics/run_cases.py \
  --sysroot "$math_prefix/arm-samsung-linux-gnueabi/sysroot" \
  --results NEW_RESULTS --output NEW_RESULTS/rebuilt.json
python3 tools/sdk/modern/numerics/analyze.py \
  --cases DATASET/cases.json --reference DATASET/reference.tsv \
  --receipt NEW_RESULTS/rebuilt.json --output NEW_RESULTS/analysis.json
```

Repeat execution with the preserved OE sysroot to distinguish source-built and
reference runtime behavior. run_cases.py mounts inputs and runtimes read-only,
records hashes, uses a private tmpfs and disables networking. Library-path
selection applies to the emulated process only. The source build never uses the
OE target sysroot as an input.

For direct C ABI controls, compile math-runner.c as C99 without NUMERICS_STD.
For an old-C++ control, generate with make_runner.py --baseline-std: it uses the
old available C++ interfaces and explicit C ABI probes for formerly missing
names, preserving the known old int classification return types. This diagnostic
mode is not a compatibility change to any installed header.

projection.cpp checks finite/zero/infinity/NaN projection and scalar overloads.
fenv.cpp checks save/restore, hold/update, exception behavior and thread isolation.
The inherited feupdateenv stub causes two focused assertions to fail; preserve
that failing receipt. The vector analysis records nearbyintf inexact findings
separately. Do not suppress these checks or describe the entire legacy math
library as numerically conforming.

The report docs/sdk-gcc16-math.md defines comparison budgets, scope and retained
limitations. QEMU execution is not native Linux 2.6.18_SELP admission.

## Private-runtime regression pass

`make_runtime_cases.py --output NEW_DIRECTORY` emits 31,140 deterministic cases
(seed 0x1136f5a). Its FMA operands span the binary32/binary64 exponent range and
include cancellation, overflow, signed zero and underflow-rounding boundaries.
`logb` covers each subnormal exponent and seeded random subnormals. All four
rounding modes and binary64 long double are tested. `reference.cpp`, the existing
runner and `analyze.py --strict` use these vectors without special acceptance
budgets: all three functions require exact rounded results.

Compile `fma_flags_reference.cpp` against the same host-only MPFR library. Feed
it inputs.tsv and save flags.tsv. It computes finite fused results exactly at
4096-bit precision, then independently obtains inexact, overflow and unambiguous
underflow expectations. `check_fma_flags.py --reference FLAGS --receipt RECEIPT
--output NEW_JSON` compares those with target flags. The 45 cases that round a
tiny exact result to the smallest normal value exclude **only FE_UNDERFLOW**
from comparison: before/after-rounding tininess policies differ by architecture.
Their values and remaining flags are still checked. Signaling NaNs and invalid
infinity operations are checked separately by `runtime_math.cpp`.

Compile runtime_math.cpp normally as C++17 with -O2 -frounding-math
-ffp-contract=off (without -fno-builtin). It checks std/global/builtin/function-
pointer entry points, fused cancellation and exact-overflow avoidance, subnormal
exponents, signaling NaNs, flags and environment restoration. fenv.cpp adds the
existing pthread rounding-isolation checks. Link with g++'s default library
order; verify GLIBCXX_SAMSUNG_MATH_1.0 imports and actual LD_DEBUG providers.
Plain C/gcc consumers continue using the unchanged firmware-compatible libm.

The legacy control is intentionally expected to fail the expanded comparison.
Preserve that receipt; a nonzero flag-check status is evidence rather than an
instruction to loosen the criteria. Prototype results are diagnostics; release
results must use the final source-built compiler and matching private runtime.

`check_runtime_providers.py --binary RUNTIME_MATH --bindings ENTRY_BINDINGS
--output NEW_JSON` requires all eight corrected imports to use the private
symbol version and their observed providers to be private libstdc++.so.6.
Run it on the entry-point probe, which includes feupdateenv. This catches a
linker silently finding an older library even when the process later loads a
new private runtime. The versioned symlink (.so.6) alone is insufficient for
an explicit -L diagnostic directory; link-time -lstdc++ needs libstdc++.so too.
The normal toolchain install creates both.

## Private complex correction

`make_complex_cases.py` produces 30,936 deterministic cases (seed 0x1136c017)
for cacos/cacosh/casin/casinh/catan/catanh/ctan/ctanh, at all three precisions.
Cases cover signed branch approaches, minimum normal/subnormal components,
ordinary and wide-exponent seeded inputs, poles, scaling crossovers and
nonfinite values. Branch tests include all four rounding modes. The comparison
budget remains 16 ULP per component or 16 epsilon times complex magnitude;
finite zero signs remain strict. This is an engineering policy, not a claim
of correctly rounded complex transcendentals or exhaustive conformance.

MPC 1.4.1 is supplemented in two documented cases. For finite saturated tan/
tanh, the small component can exceed MPC's exponent range before conversion
into a target zero. The reference uses an exponential magnitude bound and
independent directed MPFR phase signs instead. Side-of-one decisions also
check that cosine is bounded away from the exponentially smaller correction.
336 cases at saturation thresholds are cross-checked against full 4096-bit
MPC evaluation, where its exponent range suffices. Existing 5,670-case broad
reference output remains byte-for-byte identical.

For zero/nonfinite tangent cases, N3096 Annex G.6.2.6 preserves the zero
component; MPC instead gives two NaNs. The ctan counterpart follows its
rotation identity. Annex G also explicitly leaves selected infinity signs
unspecified when another input component is NaN. analyze.py accepts only those
sign alternatives, retaining infinity categories and every finite-input,
signed-zero and accuracy check. Sources: https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3096.pdf
(G.6.2.2/G.6.2.6), plus the inverse rotation identities in the pinned FreeBSD
sources. No ABI gate is altered.

complex_contract.cpp independently checks 240 branch, tiny-component, rounding-
restoration, incoming-flag, nonfinite and GNU C ABI properties. Compile normally
as C++17 with -O2 -frounding-math -ffp-contract=off. It forces all 24 complex
imports, which check_complex_providers.py requires to bind at
GLIBCXX_SAMSUNG_MATH_1.1 to matching private libstdc++.so.6. The existing eight
scalar corrections retain their GLIBCXX_SAMSUNG_MATH_1.0 version.
