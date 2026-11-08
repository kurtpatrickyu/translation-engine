# Approved Argos upstream migration — 2026-11-07

Subsequent focused repair: the SentencePiece Unicode-path failure recorded below
is resolved by a package-local serialized-model adapter. Source tests and a new
frozen artifact pass Unicode relocation; see [Unicode repair evidence](unicode-path-validation.md).
The measurements and failure reports below remain the original migration record.

The user approved Approach A: unmodified upstream revision
`17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88`, metadata version 1.11.1.
The fresh root `.venv` adopts that artifact; the old environment, old locks and
failed-build reports are preserved under `runtime/approved-migration-baseline/`.
Earlier `runtime/recovery-*`, old `build/pyinstaller.log`, and the old distribution
remain intact. Nothing was published. Clean Windows acceptance and licensing
review remain pending.

## Wheel and dependency integrity

`packaging/argos-upstream.json` identifies the full commit, captured source ZIP
SHA-256, commit timestamp, pinned tools, wheel filename/hash and unmodified-source
policy. `scripts/build_argos_wheel.py` verifies the source before extraction and
builds without an index, dependency resolution, or isolated tool downloads.
`SOURCE_DATE_EPOCH` is the commit timestamp and `PYTHONHASHSEED=0`. Two fresh local
builds yielded the same 41,937-byte wheel:

`825b1bf872390547bad6c1fcf1f12e5967e2fe6b44ca1e8a82e17a8dd79a2aa0`

This demonstrates local repeated-build identity, not cross-host reproducibility
or independent authentication of the upstream author. No Argos source patch or
fork is maintained. The metadata version is not used as a substitute for source
and wheel identity.

Setup uses `packaging/argos-build.lock`, verifies/builds the reviewed wheel,
acquires the other locked wheels with hash enforcement, and installs the complete
graph from the local wheelhouse with `--no-index`. The lock verifier rejects a
different same-version Argos hash, Stanza/Torch, and runtime/development pin
inconsistency. Both lock files permit only the reviewed Argos wheel hash.

The runtime graph decreased from 65 to 58 packages, and development/build from
78 to 71. Removed: `stanza`, `torch`, `emoji`, `fsspec`, `mpmath`, `networkx`,
`sympy`. Argos is the only retained package whose version changed. CTranslate2
4.8.5, SentencePiece 0.2.1, MiniSBD 0.9.5, ONNX Runtime 1.31.1, spaCy 3.8.18,
Thinc 8.3.14, and the other compatible pins are preserved. spaCy remains a
consistent default source dependency; it is separately excluded from freezing.
The translation archive and ONNX SHA-256 values are unchanged in
`models/provenance.json`.

## Actual worker validation

- Fresh environment import/absence checks and `pip check` passed.
- 45 unit/integration tests passed in 22.51 seconds, including actual CLI local
  provisioning and persistent worker requests. Two existing SWIG deprecation
  warnings were reported, plus a SWIG shutdown warning from pytest's process.
- Production provisioning, readiness/warm-up, repeated Chinese/product/Unicode
  text/paragraph/long/empty requests, resource reuse, missing/corrupt/ambiguous
  resources, rollback/concurrency, shutdown, and stdout purity were exercised.
- Audit hooks block network/process attempts before imports in the CLI and
  worker subprocesses. They also assert Stanza/Torch are not installed/loaded.
  The same actual-worker test passes with spaCy import unavailability simulated,
  and verifies spaCy/Thinc are absent from loaded modules in that subprocess.
- Three additional lock-integrity rejection tests passed in 0.13 seconds.

Raw source evidence: `runtime/migration-source-tests.xml`,
`runtime/migration-source-tests.log`, `runtime/migration-environment.json` and
`runtime/migration-setup.log`. Python instrumentation does not establish OS-level
network denial or every native networking path.

## One controlled diagnostic build

Only one PyInstaller build was attempted. It used the new environment and
`excludes=['spacy', 'stanza', 'torch']`; Thinc also disappeared. The filesystem
collection and PYZ table contain none of those four packages. Runtime metadata
for Argos/CTranslate2/SentencePiece/MiniSBD is explicitly included. Required
native collection was retained.

The build succeeded with unchanged hashed inputs, no resource abort, and no
Torch/spaCy/Thinc hook processing. Evidence and output are separate from old
artifacts:

- `build/diagnostic-20261107-020705/pyinstaller.log`
- `build/diagnostic-20261107-020705/build-result.json`
- `dist/diagnostic-20261107-020705/translation-engine-worker/`

The monitor samples the build process tree and system counters every 250 ms.
A Windows job contains only that diagnostic tree; sustained low physical RAM
or commit headroom terminates that job, not unrelated applications. Its limits
are operational host protection, not artifact performance budgets. Short-lived
processes or peaks between samples may be missed; summed working sets may include
shared pages across processes.

| Build measurement | New candidate | Previous available evidence |
|---|---|---|
| Outcome/time | Success, 22.53 s | Latest old build failed after 176.18 s |
| Sampled peak tree working set | 203.7 MiB | Not captured |
| Sampled peak tree private bytes | 500.9 MiB | Not captured |
| Minimum available RAM | 6.78 GiB | Earlier smoke snapshot reached about 440 MiB; different operation |
| Minimum commit headroom | 10.72 GiB | No equivalent process-tree baseline |
| Extracted distribution | 159,926,271 bytes | 729,221,757 bytes; 78.1% reduction |
| Local diagnostic ZIP | 58,067,344 bytes | No validated prior ZIP baseline |

The previous failed build and current successful build are different outcomes;
their elapsed times are not an equivalent benchmark. No numerical build-memory
or runtime-memory reduction versus the old runtime can be established without
old measurements. The size reduction is directly measured from the retained
directories. The diagnostic ZIP is local-only and lacks final redistribution
clearance/notices; it is not a release candidate.

## Frozen/source results and remaining path failure

The default relocated test still fails with Unicode paths. The retained
`frozen-validation.json` traceback reaches SentencePiece `LoadFromFile` through
Argos tokenizer initialization and raises `OSError: Not found ...
sentencepiece.model ... Error #2`. The displayed path contains `Caf�` after
best-effort stderr decoding. This identifies the failing component/operation;
the exact filename encoding/API mechanism is not established. Model validation
had succeeded before warm-up. No path-copy workaround, tokenizer modification,
model rewrite, or dependency change was introduced to hide this failure.

A separate ASCII-with-spaces relocated test passes provisioning, startup,
readiness, 15 translations, stdout purity, graceful shutdown, and missing-model
behavior. Its result is `frozen-ascii-validation.json`; the failing Unicode
result remains separate and has not been overwritten. The original source
worker also passes this same harness with ASCII paths.

| Host-local measurement | Frozen, ASCII paths | Source, ASCII paths |
|---|---|---|
| Fresh launch to uninitialized info | 0.123 s | 0.244 s |
| First health initialization/warm-up | 0.763 s | 1.638 s |
| Sampled peak working set | 189.0 MiB | 253.0 MiB |
| Sampled peak private bytes | 1,318.8 MiB | 1,358.4 MiB |
| Warm translation median / p95 | 83.3 / 134.8 ms | 90.8 / 138.7 ms |

Frozen OS-reported working-set peak was about 195.6 MiB, illustrating that a
50-ms sampler can miss a short peak. Source counters sum the `.venv` launcher
and interpreter child. The first source report sampled only the launcher; it is
retained as `source-ascii-validation.json` but superseded for memory comparison
by `source-tree-validation.json`. High private bytes remain material despite
the lower resident footprint. No thread/model optimizations were added.

Environment: Windows 11 development host, build family 26300; CPython 3.12.10
x64; Intel64 Family 6 Model 158 CPU; approximately 15.9 GiB visible RAM. These
are fresh worker processes with potentially warm filesystem/DLL caches, three
fixed inputs repeated five times, CPU execution, Argos thread settings 1/2 and
compute `auto`. Storage hardware/power settings and clean-machine conditions
were not captured. These are local diagnostics, not complete target OS baselines.

This migration snapshot predates the Unicode tokenizer repair linked above.
Current acceptance scope and remaining publication requirements are recorded in
[releasing](releasing.md). No release occurred during this migration.
