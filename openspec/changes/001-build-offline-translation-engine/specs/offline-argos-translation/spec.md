## Purpose

Translate Chinese to English with reusable local models while preserving offline operation and isolating application-managed model state.

## ADDED Requirements

### Requirement: Offline reusable translation
The engine SHALL implement Argos as its sole Milestone A backend and support direct `zh` to `en` translation using a validated model. It SHALL reuse initialized translation and sentence-boundary resources across requests. It SHALL NOT contact network services, update package indexes, install models, or download sentence-boundary resources during startup, readiness, or translation.

#### Scenario: Repeated offline inference
- **WHEN** a provisioned worker processes repeated Chinese and mixed Unicode inputs with network access denied
- **THEN** translations succeed using the same loaded resources and no network connection is attempted

#### Scenario: Unsupported pair
- **WHEN** a request specifies a pair other than the configured supported direct pair
- **THEN** it returns `UNSUPPORTED_LANGUAGE` without pivot translation or cloud fallback

### Requirement: Early validated runtime and sentence splitting
As the first A2 task immediately after A1 environment setup, a blocking minimal real zh-to-en spike SHALL verify the pinned Argos runtime/model combination and local sentence-boundary resources before extensive protocol, packaging, or release implementation. It SHALL inspect actual model resources and dependency behavior, select the simplest supported offline SBD path that passes validation, and record versions, model digest, commands, repeated translation results, and segmentation/quality/compatibility tradeoffs. A custom Stanza adapter SHALL NOT be required without evidence from real tests that simpler supported configuration is insufficient. Network access and implicit downloads SHALL remain forbidden during backend imports, startup, readiness, and translation, including with empty caches.

#### Scenario: Pinned combination cannot translate offline
- **WHEN** the early spike fails model initialization, representative translation, or no-network-attempt checks
- **THEN** extensive implementation remains blocked with recorded evidence and no silent dependency/model substitution

#### Scenario: Supported local sentence splitter is sufficient
- **WHEN** actual local resources and supported configuration pass offline and representative Chinese segmentation/translation checks
- **THEN** that path is selected without adding a more complex adapter, and its quality/long-input tradeoffs are documented

### Requirement: Explicit package-local MiniSBD resources
The backend SHALL select MINISBD before Argos imports and use the separately pinned Chinese Simplified ONNX resource in the installed package's `minisbd/` directory. Provisioning SHALL preserve original `.argosmodel` bytes. Missing, corrupt, or ambiguous ONNX resources SHALL fail before the detector can select a download/cache fallback. A successful host-local real translation spike SHALL permit local worker implementation and packaging; clean Windows 10/11 validation SHALL remain a final acceptance/publication gate rather than an early-development prerequisite.

#### Scenario: Package-local ONNX is unavailable
- **WHEN** the ONNX resource is missing, changed, or ambiguous
- **THEN** readiness reports an actionable model failure without attempting a download

#### Scenario: Clean virtual machines remain unavailable
- **WHEN** host-local compatibility passes while clean OS acceptance has not run
- **THEN** local development and executable production can proceed with VM tasks pending and no compatibility claim for untested platforms

### Requirement: Revalidate approved runtime replacements

An approved optional-Stanza Argos candidate SHALL revalidate the actual production provisioning and worker path using the unchanged translation archive and local MiniSBD ONNX hashes. Stanza/Torch SHALL be absent from the candidate environment and loaded modules; an unused spaCy/Thinc frozen exclusion SHALL require source absence tests plus packaged validation. Source-level experiments SHALL NOT count as frozen or clean-machine acceptance. Prior 1.11.0 spike results SHALL remain historical evidence rather than substitute for the replacement artifact's checks.

#### Scenario: Approved upstream revision replaces the runtime artifact
- **WHEN** the source-pinned optional-Stanza artifact is adopted after approval
- **THEN** local warm-up, repeated real zh-to-en translation, retained resources, representative quality checks, no-network-attempt instrumentation, and stdout purity pass before reduced frozen dependency collection is accepted

### Requirement: Unicode-safe package-local tokenizer
The pinned SentencePiece tokenizer SHALL load its verified serialized model through Python file I/O using a package-local adapter, with a bounded temporary buffer and one retained lazy processor. It SHALL inherit Argos encoding/decoding behavior, avoid global dependency modifications, and preserve model/dependency identities and provisioning integrity checks.

#### Scenario: Unicode tokenizer model location
- **WHEN** a validated model path contains spaces, accented letters, Chinese characters, or emoji
- **THEN** tokenizer initialization and repeated translation succeed with outputs matching the upstream tokenizer on identical model bytes and without repeated processor loading

### Requirement: Explicit isolated paths
The worker SHALL require a configured external installed-packages directory, taking `--models-dir` before `ARGOS_PACKAGES_DIR`, and an explicit writable `--state-dir`. It SHALL resolve relative paths at startup, configure isolated data/config/cache locations before backend imports, and avoid reading or modifying the user's global Argos configuration or package directories. It SHALL NOT discover models from the current working directory or executable bundle implicitly.

#### Scenario: Global installation remains untouched
- **WHEN** global Argos settings and packages exist while the worker uses explicitly configured directories
- **THEN** only the configured model directory is searched and the global installation remains unchanged

### Requirement: Validated readiness and actionable failure
Readiness SHALL require validated package identity, supported runtime compatibility, initialized tokenizer, translation model, and local sentence-boundary resources, including an offline warm-up. Missing, corrupt, ambiguous, or incompatible packages SHALL yield stable error codes and remediation guidance. Raw dependency tracebacks SHALL NOT appear in protocol errors.

A2 readiness implementation SHALL follow the successful early compatibility spike and use its validated offline path. Each running worker SHALL validate and warm its current configured installation before reporting ready; earlier spike results SHALL NOT substitute for this runtime check. A3 acceptance SHALL additionally revalidate readiness, repeated translation, and no-network-attempt behavior through production provisioning before A4 acceptance.

#### Scenario: Production provisioning follows the early spike
- **WHEN** A3 provisions the pinned model through the production path after the A2 spike passed
- **THEN** readiness and repeated offline translation are verified against that installation, and a failed resource or warm-up check prevents ready status and blocks A3 acceptance

#### Scenario: Incompatible resource
- **WHEN** model metadata or a required local resource fails compatibility or initialization checks
- **THEN** the worker remains available for inspection, reports not ready, and returns `MODEL_INCOMPATIBLE` or `BACKEND_UNAVAILABLE` as appropriate
