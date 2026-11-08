## Purpose

Give contributors and CI an isolated, reproducible environment for developing, testing, and building the standalone engine.

## ADDED Requirements

### Requirement: Project-local reproducible environment
Development and builds SHALL use project-local `.venv/`, dependencies declared in `pyproject.toml`, and a committed exact-version, hash-verified transitive dependency lock for the supported Windows x64 Python baseline. Setup SHALL NOT install project dependencies globally. CI SHALL create its own environment from the same lock.

#### Scenario: Fresh contributor setup
- **WHEN** a contributor follows the Windows CMD setup instructions
- **THEN** setup creates `.venv/` and installs the locked dependencies using its interpreter without modifying global packages

#### Scenario: Independent CI setup
- **WHEN** a new Windows CI job starts
- **THEN** it creates an independent environment and verifies dependency hashes and consistency before tests or builds

### Requirement: Reviewed source-pinned dependency adoption

An explicitly approved source-pinned Argos replacement SHALL retain a full upstream commit and source digest, reviewed source-to-wheel recipe with pinned tools, wheel digest, and regenerated hash-verified runtime/development locks. Metadata version alone SHALL NOT identify the artifact. Floating branches, silent same-version artifact substitution, and disabling hash enforcement SHALL NOT satisfy reproducibility. The current 1.11.0 environment and locks SHALL remain unchanged until adoption approval; isolated experiments SHALL use separate environment/state paths.

#### Scenario: Upstream optional-dependency candidate
- **WHEN** adoption of the exact optional-Stanza upstream revision is approved
- **THEN** a fresh environment consumes the reviewed identified wheel, retains other referenced runtime pins, passes dependency consistency and Stanza/Torch absence checks, and records provenance before worker or executable acceptance

### Requirement: Scripts and repository hygiene
Local setup, test, provisioning, and build instructions SHALL use the virtual environment interpreter after environment creation. Generated models, environments, build outputs, and temporary files SHALL be ignored. Documentation SHALL cover activation and invocation without activation and identify the supported Python baseline.

OpenSpec planning artifacts and reviewed provenance metadata SHALL be tracked in Git while preserving the user's existing ignore entries. Explicitly adding reviewed text files under ignored directories SHALL NOT add downloaded models, `.venv`, build outputs, or adjacent planning ZIP exports.

#### Scenario: Missing environment
- **WHEN** a local test or build script runs without `.venv/`
- **THEN** it fails with an actionable setup message instead of falling back to a global interpreter

#### Scenario: Planning files under an ignored directory
- **WHEN** the repository contains an `openspec/` ignore entry
- **THEN** the reviewed proposal, design, specs, and tasks are explicitly tracked and generated outputs remain ignored
