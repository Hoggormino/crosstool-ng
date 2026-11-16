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
