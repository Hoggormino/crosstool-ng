# Samsung toolchain math capability inventory

This is an inventory, with no target header, library, compiler configuration or
firmware modifications. It covers the source-built GCC 16.2 and preserved GCC
8.3 profiles against Samsung/OE glibc 2.5.90-9.0.9. No ARM program or TV operation
was executed for this inventory.

The main deliverable is the [237-row capability table](evidence/capabilities.md),
with a [CSV](evidence/capabilities.csv) and
[detailed JSON](evidence/capabilities.json).
It records native C declarations, actual forced linker symbols, OE exports and
versions/addresses, double aliases, C++ exposure, linked C++ import versions and
proposed remedies. [The full case matrix](evidence/matrix.csv)
includes the controls, integer overloads, special functions and type checks.

## Findings

| Check | GCC 16.2 | GCC 8.3 |
| --- | ---: | ---: |
| Owned compile/type/link cases | 1,267 | 1,267 |
| Compile and link | 898 | 876 |
| Declaration/exposure failure | 367 | 389 |
| Wrong C++ return type | 2 | 2 |
| Link failure after successful typed compilation | 0 | 0 |
| Exact C ABI probes linked against rebuilt libc/libm | 237/237 | 237/237 |
| Same probes linked directly against preserved OE libc/libm | 237/237 | 237/237 |

Counts include several views of each API and are not counts of unique missing
standard functions. The 237 distinct C ABI names are 57 scalar families and 22
complex families, each at float, double and long-double precision.

**All 79 native long-double C declarations are hidden:** 57 scalar names and
22 complex names. Every symbol is nevertheless exported by the OE runtime at
the same address and GLIBC_2.4 version as its corresponding double symbol. Each
also passes an explicit-prototype, forced-relocation link test. There is no
missing C scalar/complex implementation among these tested names.

The missing declarations cause libstdc++'s grouped C99 math probes to fail.
That removes C++ exposure for APIs whose double/float C declarations already
exist, including round, copysign, trunc and two-argument hypot. The named
long-double C++ functions are also absent. std::float_t and std::double_t are
missing, although the C typedefs are present. Three-argument std::hypot remains
available; the table distinguishes it from the two-argument form.

The classic long-double C++ overloads are usable through existing machinery.
For example, std::sin(long double) links with sinl@GLIBCXX_3.4 from private
libstdc++'s existing fallback, while OE libm also exports sinl@GLIBC_2.4 as an
alias of sin. A missing std::sinl name therefore does not imply missing sine
computation.

All 75 tested C++ complex cases and all 105 tested C++17 special-function cases
compile and link. The 11 std:: floating-environment interfaces and their 11 C
counterparts also compile and link. Numerical accuracy, branch cuts, exception
flags and rounding-mode behavior were not tested here.

The extra two failures are signature issues: **std::isinf(double) and
std::isnan(double) return int**, whereas the C++17 interface requires bool.
Float and long-double versions pass the bool type checks. Both compiler
profiles select obsolete global C double functions; GCC 16's os_defines.h
conditions its alternative overload path on __GLIBC_PREREQ(2,23).

GCC 16 adds 22 named classic float functions, such as std::sinf and std::sqrtf,
that fail declaration checks with GCC 8. No case that passes with GCC 8 fails
with GCC 16 in this matrix.

## Representation and emitted calls

Owned static assertions pass for both compilers: double and long double are
8 bytes, equally aligned, radix 2, 53 significant bits, minimum exponent -1021,
maximum exponent 1024 and IEEE 754 according to numeric_limits. They remain
distinct C++ types. The profile retains ARM1136/ARMv6J, VFPv2 and softfp/base PCS.
See [the type-property evidence](evidence/gcc16-v2-type-properties.json)
and the owned source math_type_properties.cpp.

At both -O0 and -O2, the lowering sample still references sinl, roundl and sqrtl.
At -O2 sqrt also has a VFP fast path, retaining a sqrtl fallback. Format equality
does not make this compiler automatically rename all calls to double symbols.
The existing runtime aliases already share their implementations. Disassembly
and undefined-symbol lists are retained alongside the table.

## Proposed remedies, not applied

1. Backport the public-header correction associated with glibc bug 10103 into
   the exact math.h and complex.h snapshots. Keep __NO_LONG_DOUBLE_MATH and
   preserve suppression when _LIBC is defined; expose prototypes to consumers.
   There is no reason from this matrix to add 79 replacement implementations.
2. Reconfigure and rebuild libstdc++ against the corrected headers. Let its real
   checks determine C99 exposure and fallback selection. Do not force the
   capability macros. Recheck the private runtime's exported/required versions.
3. Correct the two obsolete classification overload selections separately and
   verify bool return types. This is not an absent libm algorithm.
4. Repeat this matrix, then test numerical behavior and floating environment
   before claiming complete math support. No standalone math library is
   justified by the observed symbol inventory.

The official Sourceware glibc-2.16.0 snapshot, commit
75f0d3040a2c2de8842bfa7a09e11da1a73e17d0, records bug 10103 on 4 November 2011.
Its math.h/complex.h correction enables public long-double declarations while
retaining internal suppression. The existing __LDBL_COMPAT redirection branch
is a separate mechanism; it must not be enabled blindly on ARM. The historical
reference was fetched into a new private bare repository, without modifying the
OE source cache. [History record](evidence/history.json).

The catalog was checked against the C++17 draft's
[cmath synopsis](https://timsong-cpp.github.io/cppwp/n4659/cmath.syn),
[complex synopsis](https://timsong-cpp.github.io/cppwp/n4659/complex.syn) and
[cfenv synopsis](https://timsong-cpp.github.io/cppwp/n4659/cfenv.syn).
The matrix is finite; it does not cover every mixed-type template combination,
complex operators/streams, runtime numerical semantics or complete library
conformance.

## Reproduce

From this crosstool-ng worktree, choose an unused output directory.
The image ID used was
`sha256:00bfd6fdb967da28b6d19c6e0a128b90f7be6f24422b4b57879a46beab3b736e`.
The installed toolchains and OE sysroot are mounted read-only. The explicit
prototypes are diagnostic translation units only; they never alter headers.

```sh
math_results="$PWD/build-math-inventory-replay"
mkdir "$math_results"
for math_label in gcc16 gcc8; do
  if [ "$math_label" = gcc16 ]; then
    math_prefix=/mnt/data/Projects/samsung-gcc16-toolchain/build-gcc16-final/install
  else
    math_prefix=/mnt/data/Projects/samsung-modern-toolchain/build-modern-ctng-final/install
  fi
  docker run --rm --network none --read-only --cap-drop ALL \
    --security-opt no-new-privileges --memory 2g --cpus 4 --pids-limit 128 \
    --tmpfs /tmp:rw,nosuid,nodev,size=256m \
    --mount "type=bind,source=$math_prefix,target=/toolchain,readonly" \
    --mount "type=bind,source=/mnt/data/Projects/samsung/oe-b-series/build-samygo-cl/tmp/sysroots/armv6-linux-gnueabi,target=/oe-reference,readonly" \
    --mount "type=bind,source=$PWD,target=/project,readonly" \
    --mount "type=bind,source=$math_results,target=/results" \
    tv-ui-ctng:jammy python3 /project/contrib/samsung-b-series/math-inventory/inventory_math.py \
    --prefix /toolchain --reference-sysroot /oe-reference \
    --output "/results/$math_label-v2" --label "$math_label" --jobs 4
  docker run --rm --network none --read-only --cap-drop ALL \
    --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,nodev,size=64m \
    --mount "type=bind,source=$math_prefix,target=/toolchain,readonly" \
    --mount "type=bind,source=/mnt/data/Projects/samsung/oe-b-series/build-samygo-cl/tmp/sysroots/armv6-linux-gnueabi,target=/oe-reference,readonly" \
    --mount "type=bind,source=$PWD,target=/project,readonly" \
    --mount "type=bind,source=$math_results,target=/results" \
    tv-ui-ctng:jammy python3 /project/contrib/samsung-b-series/math-inventory/link_math_inventory_oe.py \
    --inventory "/results/$math_label-v2/inventory.json" \
    --reference-sysroot /oe-reference --output "/results/oe-links-$math_label"
done
python3 contrib/samsung-b-series/math-inventory/summarize_math_inventory.py \
  --build "$math_results" --output "$math_results/summary"
```

Cases use volatile inputs, -O0 and -fno-builtin. Raw C ABI probes take a volatile
function pointer with an explicit assembler symbol name; every object must have
an undefined reference to that exact symbol. Links against OE are checked using
linker maps to verify the reference libc/libm were loaded. Separate C++ static
assertions enforce the expected return type; a successful implicit conversion
cannot count as a correct overload.

Raw sources, objects, diagnostics and linker maps remain under
`/mnt/data/Projects/samsung-math-inventory/build-math-inventory/`.
[Provenance](evidence/provenance.json) records
mount mappings, image identity and header hashes. [The log index](evidence/log-index.json)
points to all 4,340 recorded diagnostic files. Initial runner iterations are
preserved; the validated matrix uses gcc16-v2 and gcc8-v2.
