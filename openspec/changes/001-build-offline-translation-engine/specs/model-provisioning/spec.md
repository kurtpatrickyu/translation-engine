## Purpose

Allow maintainers and consumers to provision a fixed translation model separately from worker execution with traceable provenance and redistribution evidence.

## ADDED Requirements

### Requirement: Reviewed immutable model identity
The project SHALL record the model's exact language pair, package version, declared runtime version, approved source URL, upstream index revision, SHA-256, and model-specific license/attribution evidence. Acquisition SHALL verify bytes against the reviewed checksum and SHALL NOT select a newer package automatically. Unresolved checksums, redistribution rights, or offline compatibility SHALL block model publication.

#### Scenario: Upstream changes bytes
- **WHEN** a retrieved file differs from the reviewed checksum at the pinned URL
- **THEN** provisioning fails and neither accepts the replacement nor updates the checksum automatically

#### Scenario: Unverified model license
- **WHEN** no model-specific redistribution evidence is available
- **THEN** publication is blocked even if the engine library or index has a permissive license

#### Scenario: Early evaluation becomes production provenance
- **WHEN** A3 prepares model provisioning after the mandatory post-A1 spike
- **THEN** it reuses the inspected model identity and digest from A2, verifies redistribution evidence, and does not silently reacquire a different version or publish evaluation bytes before rights review

### Requirement: Explicit local provisioning
Provisioning SHALL accept a local verified `.argosmodel`, separately pinned `zh-hans.onnx` MiniSBD asset, and explicit destination outside the worker bundle. It SHALL preserve original distribution bytes, validate both hashes and safe bounded archive extraction, install the ONNX into package-local `minisbd/` through staging, and validate metadata and real runtime compatibility before promotion. It SHALL NOT overwrite an immutable installation, alter unrelated packages, or commit model binaries to Git. MiniSBD code/model provenance, AGPLv3 obligations, and model-specific redistribution terms SHALL be reviewed before publication; unresolved distribution clearance SHALL NOT block private local experiments or local builds.

#### Scenario: Offline consumer provisioning
- **WHEN** a consumer supplies the model asset from this repository's release and a managed directory with network disabled
- **THEN** provisioning succeeds without retrieving files from Argos upstream and the worker can use the installed package

#### Scenario: Invalid archive
- **WHEN** an archive is corrupt, escapes the destination, exceeds extraction bounds, or has unexpected identity
- **THEN** provisioning fails without activating a partial model or changing the previous installation
