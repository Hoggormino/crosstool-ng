# GCC 16 worker variant

> Native-use correction: the historical build below is preserved QEMU/math
> evidence. Its private runtimes are not safe under SELP policy 5. Use a fresh
> [canonical strict-alignment build](strict-alignment.md) for native GCC 16 work;
> application flags alone do not repair the old shared libraries.

The newest GCC package at framework commit
`a4895d7fc49d5b423abc5f166895c80175019570` is GCC 16.2.0. This separate variant
uses HEAD's normal package integration; GCC 8.3 and its sample are preserved.
The official `gcc-16.2.0.tar.xz` SHA-256 is
`e6738e29597f733270731aa90600f37ffdc045079dfc27ec7e8192cc81085c3e`.

Follow the source preparation and container instructions in [README.md](README.md),
using `crosstool-gcc16.config` or sample `arm-samsung-linux-gnueabi-gcc16` in a
new build directory. Keep GCC 8.3 and the vendor SDK install prefixes separate.
The same exact binutils, glibc/ports, OE preparation and kernel headers remain.
No externally built sysroot is required for the compiler or libc build.

GCC 16 still supports ARMv6J/ARM1136JF-S. Its libgcc CFI adaptation is patch 0029:
the assembler's real capability test guards two directives, with the changed
`lib1funcs.S` include context ported individually. The old glibc needs valid C
declarations in SELP initialization and two configure tests; the latter avoids a
false no-whole-archive result rather than forcing a linker capability.

Patch 0030 handles the C++20 atomic-wait backend, which otherwise hardcodes
private futex operations and absolute bitset waits unavailable on Linux 2.6.18.
It selects operations provided by target kernel headers, using shared WAIT/WAKE
and relative timeouts for this profile. The existing chrono conversion retains
32-bit timeout saturation. The kernel compatibility patch guards kernel-only
declarations exposed by the original futex header; syscall numbers and robust
list layouts are unchanged.

The snapshot linker's demangler also crashed on a const noexcept member-pointer
type in the new runtime. Compatibility patch 0007 rejects an unsupported member
type safely, preserving the linker's existing fallback to the raw symbol for
version matching. `check-demangler.py` verifies safe rejection, a known C++
versioned export and localization of the unknown symbol. This does not add new
type demangling support.

`check-runtime-gcc16.sh PREFIX NEW_RESULTS` runs the baseline owned C/C++17
checks plus concepts, span, ranges, expected, atomic wait/notify and semaphore
timeout/release checks. Use the supplied container with networking disabled.
Guest syscall traces remain in the results. These tests use the host kernel;
QEMU's uname override does not emulate the TV kernel.

The clean four-job build completed in 32 minutes 54 seconds without restarts or
an externally supplied target sysroot. C/C++17/atomic probes, additional C++20/23
checks and the RmlUi Core consumer pass with both rebuilt and OE reference libc.
The guest trace uses shared WAIT/WAKE for the tested waits.
32-bit atomics are lock-free; 64-bit std::atomic uses private libatomic mutexes,
with 64-bit instruction primitives and IFUNC variants disabled. Timed futures
retain GCC's existing ENOSYS-to-relative-wait fallback; native kernel behavior
remains a separate admission check.

The standard-library module build reports math exports missing from the old
target cmath and uses GCC's existing empty-module fallback. `import std` and
`import std.compat` are unsupported here. This variant tests header-based C++;
it does not claim all C++23/26 library facilities.

Header-based C++17 math has gaps too: std::round, std::copysign, std::trunc,
std::acoshl and std::sinl fail the owned availability checks with this libc
configuration. sqrt, the long-double sin overload and isfinite compile.
Complete C++17 library conformance is not claimed; the tested RmlUi Core
consumer does not require the unavailable names. The Samsung report retains
the source snippets and compiler diagnostics.
The preserved GCC 8.3 checkpoint produces the same results for those checks.

`validation-gcc16/` contains the clean build report, pinned source preparation,
13-artifact ELF closure summary, owned execution receipts, math availability
checks and assembler/demangler regressions. Full logs remain at the workspace
paths in the log index. Private runtime imports require GLIBC_2.4; actual ELF
output is EABI5 (`0x05000002`), with no flags rewritten. Native SELP admission
remains separate from QEMU execution.

The Samsung project's `docs/sdk-gcc16.md` records the build, RmlUi consumer,
ELF/provider closure audits and remaining admission limits. Keep this as a
separate EABI5 worker with a private runtime. Preserve the old SDK for vendor
modules, and do not replace firmware libraries or pass C++ objects/exceptions
across the worker boundary.
