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
