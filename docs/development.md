# Windows development

The current development/build baseline is CPython **3.12.10 x64**. Keep Python
3.12, the approved runtime pins, and model version unchanged until compatibility
evidence justifies a reviewed amendment. Windows 10 22H2 x64 and Windows 11 x64
remain candidate acceptance targets, not verified compatibility claims.

Use Windows CMD from the repository root. No dependency installation is global.
If `python` resolves to the selected interpreter:

```bat
scripts\setup.cmd
call .venv\Scripts\activate.bat
.venv\Scripts\python.exe -m translation_engine --version
scripts\python.cmd scripts\check_environment.py
scripts\test.cmd
```

If Python is elsewhere, pass its full executable path to setup:

```bat
scripts\setup.cmd "C:\path to Python312\python.exe"
```

The wrapper uses standard `python -m venv .venv` and then only that environment's
interpreter. Activation is optional. Equivalent manual steps are:

```bat
python -m venv .venv
.venv\Scripts\python.exe scripts\setup_environment.py
```

`pyproject.toml` declares runtime, development, and build dependencies.
`requirements-dev.lock` fixes the complete development/build graph with hashes;
`requirements.lock` fixes the runtime graph constrained to the same selections.
Argos 1.11.1 is the exact source revision and wheel identified by
`packaging/argos-upstream.json`, not an interchangeable PyPI version. Setup first
uses `packaging/argos-build.lock` for pinned build tools, then verifies/builds the
unmodified source wheel with `scripts/build_argos_wheel.py`. It verifies the
source and output hashes and fixes `SOURCE_DATE_EPOCH`; two local builds matched.
All other wheels are acquired with hash checks, then the complete graph installs
from the controlled wheelhouse with `--no-index`. No floating VCS dependency or
implicit build-environment download is used. A missing compatible wheel is a blocker to investigate,
not a reason to disable hash checks or substitute dependencies.

Local Python helpers must be invoked via `scripts\python.cmd` or
`.venv\Scripts\python.exe`; `scripts\test.cmd` uses that same wrapper. The
wrapper refuses a missing `.venv` rather than selecting global Python.

Setup refuses an old environment containing Stanza/Torch: preserve the old
environment and create a fresh `.venv`. This migration preserved the former one
at `runtime/approved-migration-baseline/.venv`; it is an archived environment,
not a claim that relocated activation/entry-point scripts remain portable.

## Lock maintenance

Run the pinned pip-tools version from the environment. Lock updates are an
explicit maintainer operation; setup never refreshes them automatically.

```bat
.venv\Scripts\python.exe scripts\build_argos_wheel.py
.venv\Scripts\python.exe -m piptools compile --strip-extras --generate-hashes --allow-unsafe --no-emit-index-url --no-emit-trusted-host --no-emit-find-links --find-links downloads/wheels --constraint requirements-dev.lock --extra dev --extra build --output-file requirements-dev.lock pyproject.toml
.venv\Scripts\python.exe -m piptools compile --strip-extras --generate-hashes --allow-unsafe --no-emit-index-url --no-emit-trusted-host --no-emit-find-links --find-links downloads/wheels --constraint requirements-dev.lock --output-file requirements.lock pyproject.toml
.venv\Scripts\python.exe scripts\verify_dependency_locks.py
```

Record Python, pip, pip-tools, setuptools, wheel, OS build, and lock digests with
validation evidence. These locks target Windows CPython 3.12 x64. CI must create
its own environment and consume them; it must not reuse a contributor's `.venv`.

## Implementation gates

New change-003 builds exclude the four ordinary VC++ DLLs and require the
[official installed x64 runtime](native-dependencies.md#external-vc-prerequisite-for-change-003).
Run the focused policy check before the single monitored candidate build:
`scripts\python.cmd -m pytest tests\unit\test_packaging_policy.py -q`.
Existing build/native/ZIP checks verify the retained dependencies; no installer
or model is added. Preserve earlier diagnostic outputs and use new report names.
The focused diagnostic build's retention guard uses the preserved local
`build/diagnostic-20261107-133601/native-static-audit-complete.json` inventory;
retain that evidence with this workflow. It is not fetched automatically.
Supplying reviewed native-inventory/build inputs with public source/build
instructions remains part of the separate PUBLIC release preparation.

For the existing executable, use the [local manual guide](manual-usage.md).
It requires no environment setup or new build. Level A local usability is
complete; the [manual validation results](manual-test-results.md) retain the
user's walkthrough evidence. Public support and release gates remain separate.

The host-local real-model spike passed using package-local MiniSBD; local worker
development and Windows builds can proceed. Explicit acquisition/provisioning
is documented in [model-provisioning.md](model-provisioning.md). Run the worker
with explicit model/state paths as described in [protocol-v1.md](protocol-v1.md).

```bat
scripts\python.cmd scripts\build_windows.py
```

The controlled build uses unique `build/diagnostic-*` and `dist/diagnostic-*`
directories, preserving earlier reports and outputs. It samples its process
tree and system memory, and terminates only its assigned job on sustained host
pressure. These host-protection limits are not performance acceptance budgets.
The approved migration's diagnostic succeeded; its original Unicode-path
failure was subsequently fixed and all five relocation scenarios passed. See
[migration history](argos-migration.md) and [Unicode evidence](unicode-path-validation.md).
Use the existing verified diagnostic for manual testing rather than rebuilding
as part of usage. Local output is not cleared for publication. Clean Windows
10/11 acceptance and bundled-code/native compliance gate Level B public support
and release, independently of Level A local testing/documentation/completion.
Neither public gate has been declared complete.

See [implementation-status.md](implementation-status.md) for actual evidence
and outstanding environment/model verification. Do not interpret an environment
setup or module version check as successful translation or clean-machine proof.
