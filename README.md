# translation-engine

Standalone, reusable offline translation worker, initially targeting Chinese
(`zh`) to English (`en`) with Argos Translate.

The persistent worker now translates with the pinned Argos runtime, original
Chinese-English archive, and an explicitly provisioned MiniSBD ONNX resource.
Host-local real-model tests pass; clean Windows acceptance and redistribution
clearance remain pending. No production release is available.

**Level A local usability is complete.** The user's actual CMD transcript and
additional PowerShell recovery/translation transcript are recorded in
[manual validation results](docs/manual-test-results.md). Public Windows support,
OS-denied networking, compliance and release readiness remain separate pending gates.

See [Windows development setup](docs/development.md) and
[implementation evidence and blockers](docs/implementation-status.md).

To use the existing diagnostic executable, start with the
[CMD usage and testing guide](docs/manual-testing-cmd.md) or the existing
[PowerShell usage and testing guide](docs/manual-usage.md): verify/extract the full
worker ZIP, obtain model/ONNX files from upstream, verify hashes, provision
locally, then drive the offline worker. This is local testing, not public
support or redistribution clearance.

Use the [model provisioning guide](docs/model-provisioning.md),
[versioned worker contract](docs/protocol-v1.md), and
[compatibility evidence and quality limits](docs/compatibility-spike.md).
