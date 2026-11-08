# Repository guidance

## Purpose and boundaries

This repository provides a standalone offline Argos translation worker, currently
supporting only direct Chinese (`zh`) to English (`en`) translation. Consumers
own process supervision and integrate through [protocol v1](docs/protocol-v1.md),
not application-specific imports or paths. Model installation is a separate,
explicit local CLI operation; requests never acquire resources or use a cloud
fallback.

Windows 10 clean-VM core smoke testing passed with disclosed limitations.
Windows 11 is **expected compatible, UNTESTED**; separate acceptance is deferred
for v0.1.0. Remaining testing, evidence collection and provenance research are
deferred until after v0.1.0; unperformed coverage is not a test pass. The two
unresolved permission reviews are also deferred for this release by maintainer
direction, without asserting legal clearance. Follow the [release policy](docs/releasing.md):
required distribution materials, integrity, source identity, demonstrated
redistribution prohibitions and explicit approval still govern publication.
Reassess deferrals before the next release. Historical checklists are not gates.

README.md and docs/ describe current installation, usage, architecture and release
procedures. OpenSpec is development history and optional change tracking; it is
not required for everyday development. Consult historical records only for context.

## Navigation and responsibility

| Location | Responsibility / guidance |
| --- | --- |
| `src/translation_engine/` | CLI, framing, service, Argos lifecycle and local provisioning; [runtime guide](src/translation_engine/AGENTS.md). |
| `scripts/` | Environment setup, asset acquisition, build/audit/validation and release preparation; [tooling guide](scripts/AGENTS.md). |
| `packaging/` | Frozen entry/spec, upstream identity and candidate/compliance metadata; [packaging guide](packaging/AGENTS.md). |
| `tests/` | Python unit/real-model tests and Node artifact tests; [test guide](tests/AGENTS.md). |
| `models/provenance.json` | External model/ONNX identities, provenance and unresolved terms. |
| `docs/` | Protocol, setup, usage, build, evidence and acceptance references. |
| `openspec/` | Historical proposals, decisions and change tracking. |
| `LICENSES/`, `packaging/sources/` | Collected supplier materials; preserve original bytes and provenance. |

`downloads/`, `runtime/`, `.venv/`, `build/`, `dist/` and `candidate-staging/`
hold ignored local assets, environments or evidence. A fresh checkout does not
include them. Do not delete retained diagnostic inputs or assume they can be
regenerated automatically. There is no checked-in CI pipeline; local commands
below are the verification entry points.

## Environment and commands

Run from the repository root on Windows x64. The supported development/build
baseline is CPython **3.12.10 x64**, although package metadata permits Python
3.12 generally. Use the project interpreter; never install project dependencies
globally. CMD commands (also callable as scripts from PowerShell):

```bat
scripts\setup.cmd "C:\path to Python312\python.exe"
scripts\python.cmd scripts\check_environment.py
scripts\python.cmd -m translation_engine --version
scripts\test.cmd tests\unit -q
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
scripts\python.cmd scripts\build_windows.py
```

The interpreter path above is a user-supplied placeholder. Setup can omit it
when `python` resolves to the exact baseline. `python.cmd` refuses a missing
`.venv`. Node.js 22+ is used for maintainer tooling with built-in modules, without
npm dependencies; it is not required on worker targets. Build only when needed:
it performs native freezing and resource monitoring, not a lightweight check.
See [development](docs/development.md) for setup, lock maintenance, build
prerequisites and retained inputs.

Source entry is `python -m translation_engine`; frozen entry is
`packaging/worker_entry.py`. Ordinary execution requires `--models-dir` (or
`ARGOS_PACKAGES_DIR`) and `--state-dir`; `--version` needs neither. See
[README](README.md) for local-asset provisioning and executable-only CMD usage.

## Dependency, implementation and verification rules

- `pyproject.toml` uses setuptools and a `src` layout. The runtime and dev/build
  hash locks must agree on runtime versions. Argos is the exact source/wheel in
  `packaging/argos-upstream.json`; a same-version PyPI artifact is not a substitute.
  Setup builds that reviewed source and installs the complete graph from a
  controlled wheelhouse with hash checks. Lock updates are explicit maintainer
  work; do not weaken checks or add Stanza/Torch to fix setup failures.
- Follow nearby Python modules: small explicit components, standard-library
  framing/configuration, lazy backend imports and structured `EngineError`
  failures. Keep ML imports out of protocol and service initialization. There is
  no configured formatter/linter; do not invent a formatting gate.
- Stdout is strictly flushed protocol responses. Route diagnostics to stderr;
  do not log request/translation text or expose dependency tracebacks on the wire.
  Preserve stable public error codes, correlation and malformed-frame recovery.
- Keep model/state paths isolated, installed models immutable, and acquisition
  separate from offline execution. Avoid process-global dependency monkeypatches.
  Hosts own timeout/termination/restart; the worker processes requests serially.
- Run focused unit tests for affected contracts, then real-model tests for
  backend/resource behavior when assets are available. Frozen changes require
  appropriate relocation/native verification; see the scoped guides. Do not run
  expensive inference/build/acceptance suites for documentation-only changes.
  Report skipped checks and missing evidence honestly.
- The project's source is MIT; the bundle has separately licensed components,
  including AGPLv3 MiniSBD. Preserve notices, source identity and outstanding
  obligations in [third-party notices](THIRD_PARTY_NOTICES.md),
  [source availability](SOURCE_AVAILABILITY.md) and the compliance inventory.
  Local success, checksum checks or separate processes do not establish clearance.
  No model/ONNX binary or prerequisite installer belongs in distributed artifacts.

## Documentation Maintenance Policy

### After every implementation iteration

Before considering any coding task complete:

1. Review the task's changes and identify affected `AGENTS.md` files and project
   documentation.
2. Update affected documentation when architecture, behavior, interfaces,
   configuration, commands, ownership or important constraints change.
3. Correct or remove obsolete instructions; repair references to moved, renamed
   or deleted modules/files.
4. Check guidance for new components. Add nested `AGENTS.md` files only for
   meaningful responsibility boundaries; consolidate redundant or contradictory
   guidance and keep repository-wide rules here.
5. Verify that documentation describes the resulting implementation, not an
   older intended design, and that paths and commands remain valid.

### Stale documentation policy

Actively prevent drift. Do not preserve claims that contradict verified
implementation or accumulate historical exceptions instead of correcting obsolete
instructions. Prefer one authoritative description with links over duplicated
behavior descriptions. Delete genuinely obsolete documents only when obsolescence
is established and removal is safe. Preserve relevant history, architectural
decisions and migration evidence. Do not silently erase intentional decisions or
unresolved requirements. When canonical behavior is uncertain, report the conflict
instead of guessing.

### Documentation update boundaries

Review documentation during every coding task, but edit it only for behavior
changed by the task or existing inaccuracies it reveals. Do not rewrite unrelated
documents, introduce speculative plans as current behavior, or expand maintenance
into unrelated refactoring. Keep instructions concise and specific. Preserve
user-authored guidance unless demonstrably obsolete or contradictory; flag
ambiguous conflicts.

### Completion requirement

Documentation review is part of the definition of done for every implementation
task. In the final summary, state which `AGENTS.md` and documentation files were
updated, which stale instructions were corrected/removed, whether review found
no changes necessary where applicable, and any discrepancies needing a future
decision. Verify parent/nested consistency and review the diff before completion.
