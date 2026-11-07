## Purpose

Allow consumers to obtain fixed model assets directly from upstream and provision them locally with traceable provenance and integrity, independently of worker-only releases.

## ADDED Requirements

### Requirement: Reviewed immutable model identity
The project SHALL record the model's exact language pair, package version, declared runtime version, original filename, external upstream URL, upstream index/release identity, SHA-256, compatibility, and available model-specific license/attribution evidence, including unresolved terms. The separately pinned MiniSBD ONNX asset SHALL have equivalent identity/provenance metadata. Acquisition and provisioning SHALL verify reviewed hashes and SHALL NOT select newer packages or learn replacement hashes automatically. Models SHALL NOT be hosted in project GitHub Releases, bundled ZIPs, or public CI artifacts under this scope. Future hosting SHALL require a separate reviewed distribution decision and legal clearance; references to external assets SHALL NOT assert unknown rights are cleared.

#### Scenario: Upstream changes bytes
- **WHEN** a retrieved file differs from the reviewed checksum at the pinned URL
- **THEN** provisioning fails and neither accepts the replacement nor updates the checksum automatically

#### Scenario: Unverified model license
- **WHEN** no model-specific redistribution evidence is available
- **THEN** the unknown status is retained with upstream attribution; future model hosting remains blocked, while local testing and worker-only publication are assessed independently against their own requirements

#### Scenario: Early evaluation becomes production provenance
- **WHEN** A3 prepares model provisioning after the mandatory post-A1 spike
- **THEN** it reuses the inspected model identity/digest and available provenance from A2 without silently reacquiring another version or uploading model bytes

### Requirement: Explicit local provisioning
Provisioning SHALL accept user-supplied local `.argosmodel` and pinned `zh-hans.onnx` files obtained directly from documented upstream providers, with an explicit destination outside the worker bundle. It SHALL preserve original bytes, verify both exact hashes, safely bound archive extraction, stage package-local ONNX placement, and validate metadata and real runtime compatibility before atomic promotion. It SHALL NOT overwrite immutable installations, alter unrelated packages, or commit binaries to Git. The worker SHALL NOT download either asset automatically, including during provisioning, startup, readiness or inference. Local development/manual testing SHALL NOT depend on model redistribution clearance. Public worker publication SHALL still satisfy compliance for the MiniSBD code and other components actually distributed.

#### Scenario: Offline consumer provisioning
- **WHEN** a consumer obtains the recorded original model and ONNX files directly from upstream, verifies their hashes, and supplies them with a managed directory while network access is disabled
- **THEN** provisioning succeeds without retrieving files from Argos upstream and the worker can use the installed package

#### Scenario: Invalid archive
- **WHEN** an archive is corrupt, escapes the destination, exceeds extraction bounds, or has unexpected identity
- **THEN** provisioning fails without activating a partial model or changing the previous installation

### Requirement: Separate local and clean-OS offline evidence
Local completion SHALL require import/initialization/repeated-translation network-attempt instrumentation and isolated cache/state evidence. Public Windows support/release acceptance SHALL additionally require OS-denied networking on the mandatory clean Windows 10 target for initial v0.1.0; separate Windows 11 validation is optional under the explicit 2026-11-08 maintainer waiver and remains UNTESTED. Python-only evidence SHALL NOT be represented as native/OS network isolation, and pending clean tests SHALL NOT block manual local usage documentation.

#### Scenario: Local checks pass while clean OS images are unavailable
- **WHEN** local instrumentation passes and clean Windows environments are unavailable
- **THEN** local work is credited with its limitations and public support/isolation acceptance remains pending
