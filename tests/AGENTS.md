# Verification boundaries

Run commands from the repository root using the project `.venv` via
`scripts\test.cmd`. Pytest discovers `tests/` and declares `integration` and
`packaging` markers in `pyproject.toml`; a marker alone does not provide assets
or a packaged executable. No checked-in CI pipeline supplies those prerequisites.

## Focused suites

| Tests | Responsibility |
| --- | --- |
| `unit/test_worker.py` | Fake-backend byte-stream protocol, validation/recovery, readiness, shutdown, cleanup and subprocess CLI checks. |
| `unit/test_backend.py` | Configuration isolation and synthetic archive/receipt safety, failed staging and existing-install preservation. |
| `unit/test_tokenizer.py` | Mocked serialized loading bounds, Unicode paths, lazy reuse and inherited Argos behavior; imports installed tokenizer dependencies. |
| `unit/test_dependency_identity.py` | Reviewed Argos hash and runtime/dev lock agreement. |
| `unit/test_package_audit.py`, `unit/test_packaging_policy.py` | Native classification and spec/payload policy using lightweight fixtures. |
| `integration/test_minisbd.py` | Real assets, warm-up/translation, retained native resources, Unicode paths, offline Python audit hooks and immutable active-worker installs. |
| `compliance-staging.test.cjs`, `release-assembly.test.cjs` | Determinism, archive safety, ownership/coverage, tampering, candidate metadata and release constraints. |

```bat
scripts\test.cmd tests\unit -q
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
```

Prefer temporary directories, synthetic small archives and monkeypatched fixture
hashes for safety tests. Never loosen production hashes to accept fixtures or
write tests into real installations/dossiers. Follow the existing subprocess
timeouts and `finally` kill/wait cleanup. Fake-backend success cannot establish
translation quality or native compatibility. Node tests use built-in `node:test`;
the real-candidate check skips when local candidate directories are absent.

## Opt-in and acceptance evidence

Explicitly acquire the pinned files using [provisioning instructions](../README.md),
then opt in from CMD:

```bat
set ENGINE_INTEGRATION=1
scripts\test.cmd tests\integration -q
```

The suite skips unless both the environment flag and the two expected files in
`downloads/` exist. It provisions fresh temporary installs and exercises actual
backend resources. Test backend/tokenizer/resource changes with this suite when
assets are available; report skips rather than calling them passes. Do not make
unit tests download resources or start heavyweight inference implicitly.

Python audit hooks block exercised connection/DNS/send/process attempts; they
are not OS firewall or clean-machine proof. The frozen relocation/native harness
is `scripts/validate_windows.py`, separate from pytest. Follow
[release acceptance procedures](../docs/releasing.md) and
[Unicode evidence](../docs/unicode-path-validation.md) for target-host
checks, with fresh reports and explicit candidate identity. No development-host
test alone establishes clean Windows support, legal clearance or release readiness.
