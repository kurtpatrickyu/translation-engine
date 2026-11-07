## MODIFIED Requirements

### Requirement: Complete manifest and assets
Each public release SHALL distribute the worker ZIP, `manifest.json`, `SHA256SUMS`, third-party notices/license materials and any source/build materials required for code actually distributed. Original translation and sentence-boundary model binaries SHALL NOT be project release assets or public CI artifacts. A strict manifest SHALL declare schema/engine/protocol versions, Windows x64 platform, worker filename/tag-specific project URL/SHA-256, runtime/base-source/patch/wheel identity, build inputs, notices/compliance references and compatibility. The candidate's external translation model entry SHALL declare its unchanged original filename, upstream HTTPS URL, version, hash, language identity, provenance, known/unknown license information and compatible receipt/layout/segmentation policy. The candidate SHALL require no ONNX asset entry; historical ONNX metadata SHALL remain associated with baseline provenance only. External entries SHALL NOT require project release URLs or inclusion in the asset set. Unresolved placeholders, malformed hashes, duplicate/conflicting identities, inconsistent versions or mismatched distributed files SHALL fail verification. Upstream unavailability or changed bytes SHALL fail acquisition without weakening hashes.

`SHA256SUMS` SHALL cover all distributed release files other than itself, including the manifest and required compliance materials. External model digests SHALL remain in manifest/provenance and SHALL NOT be represented as attached release files. The manifest SHALL NOT embed its own hash. Covered binary distribution SHALL include reviewed license/notices and source delivery required by applicable licenses. Local build success or removal of MiniSBD SHALL NOT imply redistribution clearance.

#### Scenario: External model entry
- **WHEN** a candidate release references the reviewed Chinese-English model
- **THEN** users obtain that exact archive from upstream and verify its hash before model-only local CLI provisioning; no worker operation downloads it automatically or requires the retired ONNX

#### Scenario: Artifact tampering or mismatch
- **WHEN** any published candidate asset differs from manifest metadata or checksums
- **THEN** validation rejects the candidate and publishing does not proceed

### Requirement: Public bundled-component compliance
Public worker publication SHALL require evidence-backed review and fulfillment of obligations for all code/binaries actually distributed, including Visual C++/OpenMP/native DLL redistribution rights, applicable GPL runtime exceptions, MPL-covered source availability, Apache notices, and other bundled component terms. The candidate SHALL establish absence of MiniSBD and other AGPL runtime code through complete artifact reconciliation before replacing the baseline AGPL compliance path. Unresolved supplier grants, embedded-component identities or other required materials SHALL remain release blockers. Any required source/build/install materials SHALL be supplied through a reviewed license-compliant mechanism tied to the exact worker. Worker-only distribution SHALL NOT eliminate these obligations. Unknown external model terms SHALL remain recorded; future model hosting SHALL require separate clearance and SHALL NOT be a current local completion gate. host application' independent license and application SHALL remain unchanged.

#### Scenario: MiniSBD removed while native obligations remain unresolved
- **WHEN** candidate AGPL absence is established but Microsoft, Intel, static-component, MPL or other remaining compliance evidence is incomplete
- **THEN** public publication remains blocked without marking those obligations cleared

#### Scenario: Replacement cannot meet essential acceptance
- **WHEN** the migration is rejected and the baseline MiniSBD worker is retained
- **THEN** its original AGPL combined-distribution/source/notices requirements remain applicable and unresolved publication gates remain open

#### Scenario: Completed baseline evidence
- **WHEN** the candidate is evaluated or rejected
- **THEN** change 001's completed Level A evidence and original assets remain preserved and candidate results are recorded separately
