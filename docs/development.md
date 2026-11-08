# Development and architecture

The current development/build baseline is CPython **3.12.10 x64**. Keep Python
3.12, the approved runtime pins, and model version unchanged until compatibility
evidence justifies a reviewed amendment. Platform evidence and publication requirements are recorded in [releasing](releasing.md).

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

## Running and testing

From the repository root, explicitly acquire the pinned assets for local tests:

```bat
scripts\python.cmd scripts\acquire_assets.py
scripts\python.cmd -m translation_engine provision-model --file downloads\translate-zh_en-1_9.argosmodel --sbd-file downloads\zh-hans.onnx --models-dir runtime\local-models --state-dir runtime\local-state
scripts\python.cmd -m translation_engine --models-dir runtime\local-models --state-dir runtime\local-state
scripts\test.cmd tests\unit -q
node --test tests\compliance-staging.test.cjs tests\release-assembly.test.cjs
```

Acquisition is a separate networked maintainer operation using recorded URLs and
hashes. Provisioning and execution use local files. For real-model regressions:

```bat
set ENGINE_INTEGRATION=1
scripts\test.cmd tests\integration -q
```

The integration suite skips without that flag and both expected assets in
`downloads/`. Python audit hooks cover exercised network/process attempts, not
OS firewall isolation. Node.js 22+ uses built-in modules with no npm dependencies
and is needed only for maintainer tooling. There is no checked-in CI pipeline or
configured formatter/linter. Do not run inference/build suites for doc-only edits.

## Structure and current architecture

| Location | Responsibility |
| --- | --- |
| `src/translation_engine/` | CLI, configuration, bounded framing, sequential service, Argos backend, tokenizer and local provisioning |
| `scripts/` | Setup, explicit acquisition, monitored build, native/source audit, staging and assembly |
| `packaging/` | Frozen entry/spec, upstream identities, compliance inventory and candidate metadata |
| `tests/` | Fake-backend unit contracts, opt-in real-model regressions and Node artifact tests |
| `models/provenance.json` | Original external asset identities and unresolved terms |
| `LICENSES/`, `packaging/sources/` | Original supplier materials and retained source inputs |

CLI configuration resolves paths before lazy backend imports. Protocol/service
initialization imports no ML libraries. The backend validates the pinned direct
pair and warms once; later requests reuse the translator, MiniSBD detector and
lazy SentencePiece tokenizer. The package-local tokenizer reads bounded serialized
bytes through Python for Windows Unicode paths, preserving upstream encode/decode
behavior without a process-global monkeypatch. Initialization failure stays cached
until restart. Provisioning safely stages, validates and warms before atomic
promotion; failure preserves an existing installation. Models are immutable.

State/config/cache paths are isolated from installed models. Requests are serial;
the supervising host drains stderr, imposes timeouts and owns termination/restart.
Shutdown drops service references; full native reclamation belongs to process exit.
See [protocol v1](protocol-v1.md) for the public contract and [runtime guidance](../src/translation_engine/AGENTS.md)
for component responsibilities. Translation quality is model-dependent, including
punctuation, mixed-language and paragraph normalization.

## Building or modifying the Windows worker

Use Windows x64, CPython 3.12.10 x64 and the separately installed official VC++
v14 x64 runtime. No model is required to freeze the worker. Run focused checks
before a build:

```bat
scripts\test.cmd tests\unit\test_packaging_policy.py -q
scripts\python.cmd scripts\build_windows.py
```

The helper uses `packaging/worker.spec`, unique `build/diagnostic-*` and
`dist/diagnostic-*` directories, process-tree monitoring and host-memory limits.
These limits protect the build host; they are not acceptance performance budgets.
Its historical native-retention input is required at
`build/diagnostic-20261107-133601/native-static-audit-complete.json`. Missing
evidence blocks the build; do not remove the guard or fetch a substitute.
The matching source delivery retains it under `sources/worker/build/`.

The console PyInstaller onedir includes required metadata and excludes
Stanza/Torch/spaCy and exactly `msvcp140.dll`, `msvcp140_1.dll`,
`vcruntime140.dll`, `vcruntime140_1.dll`. NumPy's differently named DLL stays.
Keep the entire directory. Byte-identical builds across supplier installations
are unproven; each new build needs new hashes and frozen/native validation.

To modify worker code, edit `src/translation_engine/`; frozen entry is
`packaging/worker_entry.py`. Preserve notices and record changes/date. MiniSBD
and tqdm matching source tarballs are in `packaging/sources/`. For a direct-source
freeze, extract the matching tarball separately and copy edited package `.py`
files into the prepared `.venv/Lib/site-packages/`, keeping metadata honest.
Ordinary setup reinstalls unmodified hash-locked wheels. Upstream MiniSBD declares
Hatchling and tqdm setuptools/setuptools-scm; publisher wheel-build tool versions
are unknown, and repacking original wheel bytes is not claimed reproducible.
Rebind modified source identities and rerun source correspondence before release.

Use a full repository checkout plus retained dossier for compliance regeneration;
the minimal staged `sources/worker/` tree is a rebuild input, not a second active
compliance workspace. No signing key, activation secret or project server is
required to run a modified worker. See [releasing](releasing.md) for validation,
source delivery and publication gates.
