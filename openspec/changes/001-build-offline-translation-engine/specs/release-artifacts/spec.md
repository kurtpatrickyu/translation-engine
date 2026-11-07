## Purpose

Distribute a versioned worker with verifiable integrity, bundled-component compliance, and application-neutral instructions for externally obtained models.

## ADDED Requirements

### Requirement: Complete manifest and assets
Each public release SHALL distribute the worker ZIP, `manifest.json`, `SHA256SUMS`, third-party notices/license materials and any source/build materials required for code actually distributed. Original `.argosmodel` and MiniSBD `.onnx` binaries SHALL NOT be project release assets or public CI artifacts. A strict manifest SHALL declare schema/engine/protocol versions, Windows x64 platform, worker filename/tag-specific project URL/SHA-256, runtime/source-wheel identity, build inputs, notices/compliance references, and compatibility. External model and ONNX entries SHALL instead declare original filenames, upstream HTTPS URLs, versions, hashes, language/resource identity, provenance, known/unknown license information, and compatible runtime/package layout. These entries SHALL NOT require project release URLs or inclusion in the asset set. Unresolved placeholders, malformed hashes, duplicate/conflicting identities, inconsistent versions or mismatched distributed files SHALL fail verification. Upstream unavailability or changed bytes SHALL fail acquisition without weakening hashes.

#### Scenario: External model entry
- **WHEN** a release references the reviewed Chinese-English model and MiniSBD ONNX asset
- **THEN** users obtain them from upstream and verify hashes before local CLI provisioning; no worker operation downloads them automatically

#### Scenario: Artifact tampering or mismatch
- **WHEN** any published candidate asset differs from manifest metadata or checksums
- **THEN** validation rejects the candidate and publishing does not proceed

`SHA256SUMS` SHALL cover all distributed release files other than itself, including the manifest and required compliance materials. External model digests SHALL remain in the manifest/provenance and SHALL NOT be represented as attached release files. The manifest SHALL NOT embed its own hash. Covered binary distribution SHALL include reviewed license/notices and corresponding-source delivery required by applicable licenses. Local build success SHALL NOT imply redistribution clearance.

### Requirement: Public bundled-component compliance
Public worker publication SHALL require evidence-backed review and fulfillment of obligations for code/binaries actually distributed: MiniSBD AGPLv3 combined-distribution/source/notices obligations, Visual C++/OpenMP/native DLL redistribution rights, and other bundled components. Required corresponding source and build/install materials SHALL be supplied through a reviewed license-compliant mechanism tied to the exact worker. Worker-only distribution SHALL NOT eliminate these obligations. Unknown external model terms SHALL remain recorded; future model hosting SHALL require separate clearance and SHALL NOT be a current local completion gate.

#### Scenario: Bundled MiniSBD compliance is unresolved
- **WHEN** external models are not hosted but bundled MiniSBD code obligations are unresolved
- **THEN** public publication remains blocked while local development/manual testing can proceed without a clearance claim

### Requirement: Gated immutable publication and trust
Level A local usability SHALL require source/frozen worker functionality, local integrity/provisioning/protocol/network-attempt checks, native inventory, relocation, local measurements, and manual instructions with recorded manual results. Level B public release SHALL additionally require clean Windows 10 22H2 x64 acceptance and OS-denied networking for initial v0.1.0 (separate Windows 11 acceptance is waived by the maintainer on 2026-11-08, remains optional future validation and SHALL be labelled expected compatible but UNTESTED) for the same worker/model hashes, full target measurements, bundled-component compliance, consumer documentation, and verified worker-only candidate assets. Pending Level B gates SHALL NOT block Level A documentation or testing. Publication SHALL require explicit user approval of the exact verified candidate after all required gates pass. Existing published tags/assets SHALL NOT be overwritten; changes require a new version. No proposal operation SHALL publish anything.

Direct scripts and reviewed manual checklists SHALL suffice to bind source/tools, worker/compliance hashes, external model identities, test evidence and support claims to one candidate. Advanced CI/publication automation, attestations and mandatory platform immutability integration are deferred. Documentation SHALL distinguish trusted repository/metadata identity from checksums; matching hashes alone SHALL NOT be described as authentication.

#### Scenario: Local usability precedes public release
- **WHEN** Level A evidence passes while OS/compliance/candidate evidence remains pending
- **THEN** local usability can be declared separately without public redistribution readiness or untested OS support claims

#### Scenario: Required gate fails
- **WHEN** any Level B validation is failed, missing, mismatched or pending, or explicit candidate publication approval is absent
- **THEN** a production release cannot be published

#### Scenario: Existing release version
- **WHEN** publication is requested for an already published engine version
- **THEN** it fails and requires a new version rather than overwriting assets

### Requirement: Neutral contributor and consumer documentation
Documentation SHALL include README, Windows CMD environment setup, build/test procedures, model provisioning, the authoritative final versioned protocol reference and examples, manifest schema/trust, release process, validated Windows compatibility matrix, measured performance baseline, versioning, third-party notices, troubleshooting, and an application-neutral subprocess guide covering startup, draining stderr, framing, timeouts, shutdown, and failure recovery. Additional model introduction SHALL be documented without requiring a wire protocol change. Future Freya integration SHALL align to the same public contract without adding Freya-specific behavior to the engine.

A distinct local manual guide SHALL explain complete onedir extraction, upstream asset acquisition/hash verification, explicit offline CLI provisioning, model/state paths, readiness, repeated protocol-v1 translation, stderr handling and shutdown. A recorded manual session SHALL bind commands/results and limitations to artifact/model hashes. Pending OS acceptance or publication compliance SHALL NOT prevent writing or using the guide; unvalidated support and unknown external model terms SHALL be labelled accurately.

#### Scenario: Independent manual tester
- **WHEN** a tester follows the local guide with the existing worker and upstream-obtained assets
- **THEN** the tester can verify/provision, inspect readiness, translate repeatedly and shut down, recording results without waiting for public release automation or clean OS certification

#### Scenario: Independent external consumer
- **WHEN** an external application follows the integration guide
- **THEN** it can launch, inspect, translate, shut down, and recover from worker failure without any Freya dependency
