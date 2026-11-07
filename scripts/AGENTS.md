# Maintainer tooling

## Tool responsibilities

- `setup.cmd` bootstraps the exact Python baseline; `python.cmd` selects only
  `.venv`; `test.cmd` invokes pytest from the root. `setup_environment.py` verifies
  locks, rejects the old Stanza/Torch environment, builds the reviewed Argos wheel,
  downloads other hash-pinned wheels and installs without an index.
- `build_argos_wheel.py` consumes `packaging/argos-upstream.json` and
  `packaging/argos-build.lock`; `verify_dependency_locks.py` checks identity and
  runtime/dev graph agreement. Preserve hash checks and deterministic source/wheel
  identity; setup must not refresh locks. See [development](../docs/development.md).
- `acquire_assets.py` is explicit networked maintainer acquisition using recorded
  URLs/hashes. Worker execution/provisioning must remain local-only. Historical
  spikes (`spike_argos.py`, `reproduce_sentencepiece_paths.py`) are investigation
  tools, not production entry points.
- `build_windows.py` runs a monitored PyInstaller onedir build with unique
  diagnostic paths; `windows_resources.py` owns Windows job/process/memory helpers.
  Preserve headroom checks, pressure aborts and cleanup limited to the assigned
  process tree. These limits are host protection, not acceptance performance goals.
- `audit_windows_package.py` checks native inventory/imports and module origins;
  `validate_windows.py` exercises source/frozen provisioning, relocation, requests
  and measurements. Use explicit candidate paths and fresh report names; defaults
  can refer to older output. Read [release evidence and acceptance](../docs/releasing.md)
  before interpreting results.
- `verify_frozen_sources.py` compares embedded code to sources without executing
  package code; `stage_compliance.cjs` prepares pinned notices/sources/evidence;
  `assemble_release.cjs` assembles a local candidate from existing verified bytes.
  `verify_release_checksums.ps1` is the transferred checksum verifier. See
  [release procedures](../docs/releasing.md).

## Evidence and integration constraints

Run Python tools through the root interpreter wrapper. Node tools use built-in
CommonJS modules on Node.js 22+, with exported functions for fixture tests; no npm
installation is needed. Preserve stderr errors/nonzero failure behavior.

The build retention guard requires the ignored historical audit at
`build/diagnostic-20261107-133601/native-static-audit-complete.json`. Missing evidence
is a blocker, not permission to remove the guard. Preserve unique diagnostic
outputs and byte-pinned dossiers; do not rewrite prior reports to match new source.
Packaging changes must reconcile native inventory, spec and tests together.

Staging requires a fresh `candidate-staging/` destination; use `--check` for an
existing one. Valid blocked compliance preparation returns **2**, failure **1**.
Release assembly/check returns **0** for valid candidate or prepared stable assets,
retaining
`release_ready: false`. Neither tool publishes, rebuilds inference code or acquires
models. Do not treat an exit-zero assembly or source comparison as compliance
clearance. Avoid copying generation commands into checks that would overwrite
evidence. Full command sequences and prerequisites belong in the linked guides.

Documentation materials pinned to the existing candidate resolve from
`packaging/sources/candidate-documentation/` with their original hashes. New
assemblies carry current README and guides; `--check` verifies immutable rc.1
against its exact recorded manifest, archived configuration and complete artifact
hashes. It must not
rewrite that candidate to reflect newer instructions.

## Verification

From the root, select unit tests for lock identity, package auditing and packaging
policy when those helpers change; run the Node suites for stager/assembler changes:

```bat
scripts\test.cmd tests\unit\test_dependency_identity.py tests\unit\test_package_audit.py tests\unit\test_packaging_policy.py -q
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
scripts\python.cmd scripts\verify_dependency_locks.py
```

Use focused fixtures before heavy builds. Changes affecting frozen behavior need
new candidate evidence; retain previous reports and report unavailable clean-host
verification rather than inferring it from development-host runs.
