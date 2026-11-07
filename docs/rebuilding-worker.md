# Building and modifying the worker

Start with the immutable source commit identified by the eventual GitHub
Release, plus its matching source/compliance assets. No such release is published
yet. The candidate's original worker/build files are also staged individually
under `sources/worker/`; copy that tree to an empty working directory. Preserve
the adjacent `sources/` and `evidence/` trees for the third-party source and
verification records. Consult `SOURCE_AVAILABILITY.md` and `BLOCKERS.txt` first.

Use Windows x64, CPython **3.12.10 x64**, and CMD. Install the latest supported
official Microsoft VC++ v14 x64 Redistributable separately. Locally tested
14.50.35719.0 is not a proven minimum. Keep compatible newer runtimes.

```bat
scripts\setup.cmd "C:\path to Python312\python.exe"
scripts\python.cmd scripts\check_environment.py
scripts\python.cmd -m pytest tests\unit -q
```

Setup uses the unchanged `requirements-dev.lock` and `requirements.lock`, with
hash checking and a controlled local wheelhouse. It builds Argos from commit
`17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88`, using
`packaging/argos-build.lock`, `packaging/argos-upstream.json` and
`scripts/build_argos_wheel.py`. Do not substitute the same-version PyPI Argos
wheel or regenerate locks. Source and wheel digests must match the identity
file. Internet access for dependency acquisition is a maintainer build step;
it is not part of worker execution. No model is needed to freeze the worker.

The monitored build helper requires its historical native retention baseline.
The matching source delivery includes the original audit at
`sources/worker/build/diagnostic-20261107-133601/native-static-audit-complete.json`
for this purpose. This is the build helper's comparison input, not the current
candidate inventory. Current candidate evidence is `evidence/audit.json`, with
176 files and no ordinary VC++ DLLs. Preserve both records with their hashes.

```bat
scripts\python.cmd scripts\build_windows.py
```

The helper runs PyInstaller with `packaging/worker.spec`, unique diagnostic
build/dist paths, resource monitoring and native retention checks. It refuses
unapproved graph changes and never downloads models. PyInstaller 6.22.3 embeds
Python code with optimization level 0. The spec excludes Stanza/Torch/spaCy and
exactly the four ordinary VC++ DLL basenames; keep NumPy's renamed DLL.
Byte-identical output across different Windows/Python supplier installations
has not been demonstrated. Record the new executable/ZIP hashes and rerun the
existing frozen/native verification against each new candidate.

To modify the application, edit `src/translation_engine/`; the wire interface
is [protocol v1](protocol-v1.md). The worker entry point is
`packaging/worker_entry.py`. Rebuild with the same commands and record your
changes and date. Preserve copyright, license and inherited notices.

To modify MiniSBD or tqdm without needing their original wheel build tools,
extract the matching source tarball into a separate directory, then copy the
edited package `.py` files over the corresponding package in the prepared
`.venv/Lib/site-packages/` before freezing. Keep package metadata/version identity
honest, record each modification/date, and regenerate source correspondence and
release materials. This is an explicit local source modification procedure;
ordinary setup reinstalls the hash-locked, unmodified wheels. MiniSBD's original
`pyproject.toml` also supports building a wheel with Hatchling; tqdm declares
setuptools/setuptools-scm. Those publisher wheel-build tool versions are not
known or needed for the direct-source freeze procedure. No claim is made that
repacking either publisher wheel reproduces its original bytes.

The source comparison helper compiles source without executing it and reads the
actual executable's embedded PYZ and runtime modules:

Run compliance regeneration from the full public repository checkout with the
retained candidate dossier and wheels. The minimal staged `sources/worker/`
tree preserves historical build inputs, including historical compliance metadata;
it is for rebuilding the worker. It is not a second compliance workspace. Use
the active inventory in the full checkout for the commands below.

```bat
scripts\python.cmd scripts\verify_frozen_sources.py --report runtime\new-source-correspondence.json
node --test tests\compliance-staging.test.cjs
node scripts\stage_compliance.cjs candidate-staging\NEW-NAME
node scripts\stage_compliance.cjs --check candidate-staging\NEW-NAME
```

The comparison uses the candidate in the reviewed compliance inventory; rebind
that inventory after reviewing a new build. A modified package is expected to
fail comparison against the old locked wheel until its new source and identity
are explicitly recorded. The current stager verifies candidate and build hashes,
material pins, retained blockers, and no model binaries. It returns code 2 for
valid preparation with unresolved readiness; code 1 indicates failure.

For runtime installation extract the complete worker onedir, install the official
VC++ prerequisite separately, and use [model provisioning](model-provisioning.md)
and [the manual CMD guide](manual-testing-cmd.md). Users acquire model/ONNX assets
from the recorded upstream URLs and verify expected hashes. No signing key,
activation secret or project server is required to install/run a modified worker.
Clean Windows acceptance, native rights and complete native source/notice
mapping remain pending; successful rebuilding alone does not clear them.
