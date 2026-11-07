# translation-engine

Standalone, reusable offline translation worker, initially targeting Chinese
(`zh`) to English (`en`) with Argos Translate.

The persistent worker now translates with the pinned Argos runtime, original
Chinese-English archive, and an explicitly provisioned MiniSBD ONNX resource.
Host-local real-model tests pass; clean Windows acceptance and redistribution
clearance remain pending. No production release is available.

See [Windows development setup](docs/development.md) and
[implementation evidence and blockers](docs/implementation-status.md).

Use the [model provisioning guide](docs/model-provisioning.md),
[versioned worker contract](docs/protocol-v1.md), and
[compatibility evidence and quality limits](docs/compatibility-spike.md).
