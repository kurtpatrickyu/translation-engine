# Remaining Windows acceptance checklist

Host-local translation and Python network-attempt instrumentation permit local
development/builds. They do not establish supported-platform compatibility.

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

Record worker ZIP/extracted sizes, separate model and ONNX sizes, process cold
start to uninitialized info, initialization/warm-up to readiness, idle/ready/peak
working set and private bytes, repeated translation latency, sample counts/raw
observations/median/tail, corpus identity, cache/warm-up conditions, thread and
compute settings, timing/memory methods, and artifact/source/lock identities.
Review these baselines before setting performance thresholds.

Also pending before publication: native DLL/app-local runtime audit, legally
complete third-party license/notices and corresponding-source delivery,
model-specific redistribution clearance, complete manifest/checksum validation,
immutable release configuration, and explicit publication instruction. No release
is authorized by local experiment/build success. VM unavailability does not
block executable production, but both clean rows gate final acceptance and
Milestone A completion.
