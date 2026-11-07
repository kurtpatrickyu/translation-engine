## MODIFIED Requirements

### Requirement: Reviewed immutable model identity
The project SHALL record the model's exact language pair, package version, declared runtime version, original filename, external upstream URL, upstream index/release identity, SHA-256, compatibility, and available model-specific license/attribution evidence, including unresolved terms. The candidate SHALL retain the original Chinese-English archive identity and separately identify its segmentation code policy and installation layout version; it SHALL require no MiniSBD ONNX asset. Historical ONNX provenance SHALL remain associated with the baseline only. Acquisition and provisioning SHALL verify reviewed hashes and SHALL NOT select newer packages or learn replacement hashes automatically. Models SHALL NOT be hosted in project GitHub Releases, bundled ZIPs, or public CI artifacts under this scope. Future hosting SHALL require a separate reviewed distribution decision and legal clearance; references to external assets SHALL NOT assert unknown rights are cleared.

#### Scenario: Upstream changes bytes
- **WHEN** a retrieved file differs from the reviewed checksum at the pinned URL
- **THEN** provisioning fails and neither accepts the replacement nor updates the checksum automatically

#### Scenario: Unverified model license
- **WHEN** no model-specific redistribution evidence is available
- **THEN** the unknown status is retained with upstream attribution; future model hosting remains blocked, while local testing and worker-only publication are assessed independently against their own requirements

#### Scenario: Early evaluation becomes production provenance
- **WHEN** production provisioning is prepared for the segmentation replacement
- **THEN** it reuses change 001's inspected translation archive identity/digest and available provenance without silently reacquiring another version, requiring the retired ONNX or uploading model bytes

### Requirement: Explicit local provisioning
Candidate provisioning SHALL accept the user-supplied pinned local `.argosmodel` obtained directly from the documented upstream provider, with an explicit destination outside the worker bundle. It SHALL preserve original bytes, verify the exact archive hash, safely bound archive extraction, validate package metadata and every installed runtime file through a versioned integrity receipt, and validate real runtime compatibility before atomic promotion. Its current receipt SHALL identify the model hash, installation layout and segmentation policy without an ONNX requirement. It SHALL NOT overwrite immutable installations, alter unrelated packages, commit binaries to Git or implicitly migrate baseline installations. The worker SHALL NOT download assets automatically, including during provisioning, startup, readiness or inference. Local development/manual testing SHALL NOT depend on model redistribution clearance. Public worker publication SHALL still satisfy compliance for all components actually distributed.

#### Scenario: Offline consumer provisioning
- **WHEN** a consumer obtains the recorded original model directly from upstream, verifies its hash and supplies it to a fresh managed directory while network access is disabled
- **THEN** candidate provisioning and warm-up succeed without an ONNX file or retrieval from upstream and the worker can use the installed package

#### Scenario: Invalid archive
- **WHEN** an archive is corrupt, escapes the destination, exceeds extraction bounds or has unexpected identity
- **THEN** provisioning fails without activating a partial model or changing the previous installation

#### Scenario: Legacy installation or obsolete CLI flag
- **WHEN** the candidate receives a baseline receipt or the obsolete `--sbd-file` argument
- **THEN** it rejects the incompatible input with actionable new-directory/model-only provisioning guidance and leaves original assets and installations unchanged

#### Scenario: Existing current installation
- **WHEN** current provisioning is repeated or concurrent for an existing valid candidate installation
- **THEN** integrity and runtime validation run without replacing its files, changing its receipt or disturbing a running worker

#### Scenario: Candidate installed file is changed
- **WHEN** a recorded model, tokenizer, metadata or other required installed file fails receipt validation
- **THEN** readiness fails with an actionable stable model error before native model/tokenizer loading or any download attempt
