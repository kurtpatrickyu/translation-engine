## Purpose

Let independent applications obtain versioned engine and model artifacts with verifiable compatibility, integrity, provenance, and neutral integration instructions.

## ADDED Requirements

### Requirement: Complete manifest and assets
Each release SHALL contain worker ZIP, pinned original `.argosmodel`, `manifest.json`, `SHA256SUMS`, and third-party notices. A schema-validated manifest SHALL declare schema version, independent engine version, protocol version, OS/architecture, worker filename/tag-specific URL/SHA-256, Argos version, model pair/version/filename/tag-specific URL/SHA-256, and explicit compatibility requirements. Unresolved placeholders, malformed hashes, inconsistent versions, or mismatched assets SHALL fail validation.

#### Scenario: Artifact tampering or mismatch
- **WHEN** any published candidate asset differs from manifest metadata or checksums
- **THEN** validation rejects the candidate and publishing does not proceed

The asset set and manifest SHALL additionally include the separately pinned MiniSBD ONNX resource with source/release identity, language, SHA-256, and license/provenance reference. Covered binary distribution SHALL include the reviewed license/notices and corresponding-source delivery required by applicable licenses. Local experiment/build success SHALL NOT imply redistribution clearance.

### Requirement: Gated immutable publication and trust
Tests, real-model offline validation, Windows build, packaged validation, license review, and clean-machine evidence for every accepted OS matrix row SHALL pass for the exact candidate before production publication. GitHub release immutability SHALL be enabled; all assets SHALL be attached to a draft before publication. Existing published tags/assets SHALL NOT be replaced. Documentation SHALL explain that hashes provide integrity relative to trusted metadata and that authenticity requires verifying the expected repository/release identity and release attestation or independently trusted metadata. No proposal operation SHALL publish a release. Extensive release automation SHALL follow the first independently working A4 executable and use focused scripts/workflow gates without requiring a general automation framework; all necessary integrity and reliability checks SHALL remain mandatory.

#### Scenario: Required gate fails
- **WHEN** any validation is failed, missing, or pending
- **THEN** the workflow cannot publish a production release

#### Scenario: Existing release version
- **WHEN** publication is requested for an already published engine version
- **THEN** it fails and requires a new version rather than overwriting assets

### Requirement: Neutral contributor and consumer documentation
Documentation SHALL include README, Windows CMD environment setup, build/test procedures, model provisioning, the authoritative final versioned protocol reference and examples, manifest schema/trust, release process, validated Windows compatibility matrix, measured performance baseline, versioning, third-party notices, troubleshooting, and an application-neutral subprocess guide covering startup, draining stderr, framing, timeouts, shutdown, and failure recovery. Additional model introduction SHALL be documented without requiring a wire protocol change. Future Freya integration SHALL align to the same public contract without adding Freya-specific behavior to the engine.

#### Scenario: Independent external consumer
- **WHEN** an external application follows the integration guide
- **THEN** it can launch, inspect, translate, shut down, and recover from worker failure without any Freya dependency
