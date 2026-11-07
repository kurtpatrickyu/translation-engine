# translation-engine

Standalone, reusable offline translation worker, initially targeting Chinese
(`zh`) to English (`en`) with Argos Translate.

The project's own source retains its [MIT license](LICENSE). The bundled worker
also includes MiniSBD under AGPLv3 and separately licensed dependencies; see
[third-party notices](THIRD_PARTY_NOTICES.md), [source availability](SOURCE_AVAILABILITY.md)
and [rebuilding instructions](docs/rebuilding-worker.md). Candidate-specific
[compliance staging](docs/compliance-staging.md) preserves unresolved supplier
obligations; these materials do not yet establish public release readiness.

The persistent worker now translates with the pinned Argos runtime, original
Chinese-English archive, and an explicitly provisioned MiniSBD ONNX resource.
Host-local real-model tests pass; clean Windows acceptance and redistribution
clearance remain pending. No production release is available.

For initial **v0.1.0** (current candidate **0.1.0-rc.1**), Windows 10 x64 VM
build 19045.3803 is [core smoke-tested with limitations](docs/windows10-smoke-results.md).
Windows 11 is **expected compatible, UNTESTED**: the maintainer explicitly waived
its separate clean-machine acceptance for this release; future validation is
optional. See the [scope decision](docs/v0.1.0-acceptance-scope.md) and
[remaining mandatory release gates](docs/windows-acceptance.md#exact-remaining-publication-gates).
The waiver does not clear Windows 10's remaining evidence requirements,
source/notices/native obligations, artifact integrity or final release approval.

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

New change-003 worker ZIPs require the separately installed official
[Microsoft Visual C++ x64 Redistributable](https://aka.ms/vc14/vc_redist.x64.exe).
Install the latest supported package if needed; keep compatible newer versions.
See [runtime requirements and remediation](docs/native-dependencies.md#external-vc-prerequisite-for-change-003).
The older validated diagnostic remains preserved. No target Python or automatic
prerequisite download/installation is required.
