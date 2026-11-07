# SentencePiece Unicode-path repair — 2026-11-07

Historical development-host evidence; current platform scope and release requirements are in [releasing](releasing.md).

## Confirmed cause and adaptation

The retained failure in
`build/diagnostic-20261107-020705/frozen-validation.json` reaches
`ArgosBackend.initialize` → `PackageTranslation` → `apply_packaged_translation`
→ `SentencePieceTokenizer.encode/lazy_processor` →
`SentencePieceProcessor(model_file=...)` → `LoadFromFile`, failing with Error #2.
Argos `Package` constructs a tokenizer instance on each selected package; the
backend directly owns that package and its translation lifecycle.

`scripts/reproduce_sentencepiece_paths.py` extracts only the tokenizer from the
hash-verified original archive into a disposable workspace. Python reads the
same bytes from ASCII, spaces, and `Café 中文 😊` paths. Native filename loading
passes ASCII/spaces but fails Unicode. `model_proto` loading passes all three
and matches encoding/decoding on the same corpus. The tokenizer is 804,374 bytes,
SHA-256 `72600ea476b3e3b76763919c3a30ef5104d9b473b19567d45251f56034264f54`.
Raw result: `runtime/unicode-sentencepiece-reproduction.json`.
This establishes a native filename-loading limitation on this host; it does not
identify the exact underlying Windows encoding/API implementation defect.

`backends/tokenizer.py` subclasses the pinned upstream `SentencePieceTokenizer`
and overrides only `lazy_processor`. After existing installation/hash validation,
the backend replaces only its own package's uninitialized tokenizer. Python opens
the file and reads at most 1 MiB plus one overflow-detection byte, rejecting empty
or oversized data. SentencePiece consumes serialized bytes. The adapter retains
one processor, inherits Argos encode/decode unchanged, and retains no serialized
buffer after initialization. Failed loading leaves the processor unset.

This temporary buffer bound does not bound SentencePiece/native inference memory;
the pinned model needs about 786 KiB of temporary Python bytes, with additional
native parsing allocations. There are no temporary ASCII model copies, model
rewrites, installed-package edits, global monkey patches, or custom Argos fork.
The original `Package` tokenizer class is unchanged. Future dependency/model
upgrades must revalidate tokenizer type/lifecycle, inherited methods, output
equivalence, the byte bound, and resource retention.

The Argos revision, reviewed wheel, all dependency pins/lock hashes, packaging
exclusions and both original asset hashes remain unchanged. Installed Argos
`tokenizer.py` and `package.py` still byte-match the approved wheel; its SHA-256
remains `825b1bf872390547bad6c1fcf1f12e5967e2fe6b44ca1e8a82e17a8dd79a2aa0`.
Lock validation still reports 58 runtime / 71 development packages. New frozen
filesystem/PYZ inspection finds no Stanza, Torch, spaCy or Thinc.

## Validation and retained evidence

Focused tests cover lazy loading/reuse, empty/oversized/invalid model rejection,
upstream token/decode equality, ASCII/spaces/Unicode paths, actual Chinese-English
translation, repeated requests, source CLI provisioning/warm-up, MiniSBD splitting,
changed tokenizer/ONNX integrity rejection, rollback, concurrency, stdout purity,
shutdown, and Python network/process-attempt audit hooks before dependency imports.
Source-worker tests include separate Unicode model/state cases, plus combined
paths, with spaCy unavailable as in freezing. No attempts were recorded.

The first run retained `runtime/unicode-source-tests.xml`: 59 passing tests,
with setup/teardown errors on one oversized-bytes parameter because pytest placed
its generated identifier into a Windows environment variable exceeding 32,767
characters. Explicit short case IDs fixed the test fixture; all seven tokenizer
tests then passed (`runtime/unicode-tokenizer-tests.xml`). The unchanged source
worker's successful test cases and combined Unicode relocation harness passed
before the build. A clean focused rerun passed all **60 tests in 39.91 seconds**,
retained separately as `runtime/unicode-source-tests-fixed.xml`. Existing SWIG deprecation warnings
occur in the pytest process; actual worker subprocesses have empty stderr.

One additional monitored build was authorized and performed for this repair:

- Build log/result: `build/diagnostic-20261107-133601/`.
- Executable: `dist/diagnostic-20261107-133601/translation-engine-worker/translation-engine-worker.exe`.
- Source relocation: `runtime/unicode-source-relocation.json`.
- Frozen reports: `frozen-unicode-model.json`, `frozen-unicode-executable.json`,
  `frozen-unicode-state.json`, `frozen-unicode-all.json`, and `frozen-ascii.json`
  in the new build directory.

All five frozen cases pass production staged provisioning, cold startup,
readiness, 15 repeated translations, response-only stdout, empty normal stderr,
shutdown, missing-model inspection, changed-tokenizer rejection, and failed
reprovision preservation of the existing installation/receipt. Test-only changed
bytes exist only in disposable model installations and are restored/cleaned;
the original archive and ONNX are never edited. Source rollback additionally
checks failed staged runtime validation never promotes an installation.

All 75 frozen translations exactly match the retained ASCII migration baseline's
outputs. All five checks use the same executable and local diagnostic ZIP hashes:

- EXE: `627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941`.
- ZIP: `965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b`.

The harness removes inherited Python/Argos/environment paths, restricts PATH to
System32, and uses fresh state. Source audit hooks cover exercised Python
network/DNS/send/process paths. Frozen tests use the offline-configured code path;
no firewall or native network-attempt tracing was applied. These checks do not
complete OS-denied-network or clean-machine acceptance.

## Resource observations

Same development host as the migration: Windows 11 build family 26300, CPython
3.12.10 x64, Intel64 Family 6 Model 158, approximately 15.9 GiB RAM. CPU/MiniSBD,
Argos threads 1/2, compute auto; fresh processes with potentially warm filesystem
and DLL caches. Storage/power settings and clean VM conditions are unrecorded.
Build sampling is 250 ms; worker-tree sampling is 50 ms. Short peaks may be missed.

| Measurement | New diagnostic | Previous reduced diagnostic |
|---|---:|---:|
| Build elapsed | 25.92 s | 22.53 s |
| Sampled build tree peak working set | 190.0 MiB | 203.7 MiB |
| Sampled build tree peak private bytes | 492.0 MiB | 500.9 MiB |
| Extracted distribution | 159,927,584 bytes | 159,926,271 bytes |
| Local ZIP | 58,072,023 bytes | 58,067,344 bytes |
| Frozen startup to info | 0.138 s, combined Unicode | 0.123 s, ASCII |
| Frozen initialization/warm-up | 0.757 s | 0.763 s |
| Sampled runtime peak working set | 186.8 MiB | 189.0 MiB |
| Sampled runtime peak private bytes | 1,315.4 MiB | 1,318.8 MiB |
| Warm translation median / p95 | 87.8 / 142.3 ms | 83.3 / 134.8 ms |

The build had no resource abort and unchanged recorded source inputs. Minimum
available RAM was 5.99 GiB and commit headroom 10.12 GiB. Across all five new
frozen runs, startup was 0.128–0.138 s and initialization 0.757–0.776 s.
The source combined-Unicode harness sampled 249.3 MiB working set / 1,357.0 MiB
private bytes, with 0.262 s startup and 2.449 s initialization.
The distribution grew by 1,313 extracted bytes. These are individual observations
under differing path/cache conditions, not evidence of a speed/memory improvement
or regression. Private memory remains around 1.3 GiB. No performance budget is
invented and no further optimization/build is part of this repair.

Previous successful/failing diagnostics and distributions remain intact. No
release was published. Current remaining acceptance is recorded in
[releasing](releasing.md).
