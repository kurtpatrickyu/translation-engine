# Remaining Windows acceptance checklist

Host-local translation and Python network-attempt instrumentation permit local
development/builds. They do not establish supported-platform compatibility.

The current diagnostic is technically ready for clean-image testing: the
[native audit](native-dependencies.md) verifies all 53 AMD64 PE files, bundled
non-OS imports/exports, runtime metadata, and byte-for-byte ZIP contents. Actual
inference loads the application runtimes locally. No packaging correction or
new build was required. Two external Teruten DLLs were observed in this host's
worker process; the strict isolation audit remains failed despite functional
success. Do not copy or allowlist these DLLs; use genuinely clean images.

Candidate hashes (same as the successful Unicode relocation tests):

- Worker ZIP: `965cf2b166443a27ddfecf4d09b756420febaafb8d065f5ca97af8a3244a264b`.
- Worker EXE: `627c5e40ded9dd29655c2e9b68cbab7a8a12c90843daf3d6d7cd5d23fbc0b941`.
- Model: `62e7af5a3a48b530e47b7b3e5c78c2de79073ecd815750d2bf3ab35b4a67da2d`.
- ONNX: `b2a6e45ebb43df44ac3c8e4100ea1cb30ec8319c5698b678ed3f203e5edc5d0e`.

The ZIP is a private diagnostic, not a cleared release bundle.

| Target | Exact clean image | Python-free offline executable test | Measurements | Status |
|---|---|---|---|---|
| Windows 10 22H2 x64 | Not available | Pending | Pending | Not yet validated |
| Windows 11 x64 | Not available | Pending | Pending | Not yet validated |

For each row, record edition/version/build/update/servicing status, CPU/features,
RAM, storage and VM allocation; use the **same** worker ZIP, original translation
archive, and separately pinned ONNX hashes. Extract the full onedir distribution
to a new path containing spaces and Unicode. Ensure no system Python, global
Argos, inherited development paths, model cache, or SBD cache is present.

Disable networking at the VM/OS boundary before explicit local provisioning,
startup, readiness, and repeated zh-to-en translation. Record network controls
and results; Python audit instrumentation is additional evidence, not a
substitute. Verify product/Unicode/paragraph/long-input samples, stdout-only
JSON responses, stderr diagnostics without default text logs, error recovery,
flushing, and shutdown. Verify missing/corrupt resources fail without downloads.

Record loaded native module paths at readiness and after translation. Confirm
Python, Visual C++ v14, Intel OpenMP, CTranslate2, SentencePiece, NumPy/OpenBLAS,
and ONNX runtimes load from the bundle, with no development/global fallback or
external injected vendor modules. Start without a separately installed Visual
C++ redistributable prerequisite; preserve any loader/API error before changing
the test image. Verify Windows API sets/UCRT and delay imports on each exact OS
build, rather than treating development-host System32 presence as compatibility.
Do not modify host security software to force an isolation pass.

Record worker ZIP/extracted sizes, separate model and ONNX sizes, process cold
start to uninitialized info, initialization/warm-up to readiness, idle/ready/peak
working set and private bytes, repeated translation latency, sample counts/raw
observations/median/tail, corpus identity, cache/warm-up conditions, thread and
compute settings, timing/memory methods, and artifact/source/lock identities.
Review these baselines before setting performance thresholds.

The host-local technical DLL/app-local audit is complete; native redistributable
source/rights and servicing review remain pending. The four bundled ordinary
Visual C++ DLLs were collected from host System32 (14.50.35719.0); their hashes
are recorded but Python locks alone do not pin their acquisition source.

Also pending before publication: legally
complete third-party license/notices and corresponding-source delivery,
model-specific redistribution clearance, complete manifest/checksum validation,
immutable release configuration, and explicit publication instruction. No release
is authorized by local experiment/build success. VM unavailability does not
block executable production, but both clean rows gate final acceptance and
Milestone A completion.
