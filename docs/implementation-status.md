# Milestone A implementation evidence

Latest acceptance evidence (recorded 2026-11-08): the user's clean VirtualBox
Windows 10 x64 build 19045.3803 core smoke passed for exact candidate 0.1.0-rc.1
after resolving the external runtime prerequisite. See the
[transcript review](windows10-smoke-results.md) and
[current acceptance matrix/remaining gates](windows-acceptance.md).
Windows 10 full acceptance is partial; its OS-denied networking, native
origins and full target measurements remain pending. Separate Windows 11 clean
acceptance is explicitly waived for initial v0.1.0 by the maintainer on 2026-11-08;
Windows 11 is expected compatible but UNTESTED and optional future validation.
See the [scope decision](v0.1.0-acceptance-scope.md). No new top-level task is
complete: current progress is **38/54; LOCAL 37/37; PUBLIC 1/17** (5.2 is complete).
The Level A and earlier diagnostic snapshots below remain historical evidence.

**Level A is complete (2026-11-07): LOCAL 37/37; overall 37/54; PUBLIC 0/17.**
The user personally executed both manual guides using the existing diagnostic.
The supplied full CMD transcript is retained and reviewed in
[manual-test-results.md](manual-test-results.md), including artifact/asset hashes,
Unicode provisioning, persistence/custom translation, error recovery, stderr,
exit codes and cleanup. A supplied PowerShell log also records initial setup
failures, corrected provisioning, malformed-request recovery, translation and
shutdown; broader guide completion is user-confirmed beyond that capture, with
no invented outputs/timings. Tasks 4.10 and 4.8 are
complete; all Level B support/network/compliance/release gates remain pending.
This evidence update ran no new translation or heavy tests and changed no runtime.
See [current tasks](../openspec/changes/001-build-offline-translation-engine/tasks.md).

Current status after the approved migration: Argos source revision
`17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88` is adopted in a fresh environment.
The controlled reduced build succeeds. The subsequent package-local SentencePiece
adapter fixes Unicode-path provisioning; source and frozen Unicode relocation
pass on the development host. See [Unicode repair evidence](unicode-path-validation.md)
and [migration history](argos-migration.md). Both clean Windows rows remain pending.
The sections below preserve earlier milestones and failure/recovery history.

Subsequent local native packaging audit: all 53 AMD64 PE binaries and the
validated ZIP contents pass static inventory/import/export checks. Inference
loads application runtimes from the relocated bundle with a minimal child
environment. External Teruten modules prevent a strict clean-isolation pass on
this development host. See [native audit](native-dependencies.md); no build or
packaging correction was needed. Its historical progress snapshot was 29/47;
the current separate-level accounting appears above.

The user invoked `openspec-apply-change` for the reviewed
`001-build-offline-translation-engine` change on 2026-11-06. This authorizes
implementation; it does not authorize production release publication.

## A1 environment inspection

- Host: Windows x64, OS version `10.0.26300.0` (Windows 11 build family).
- Available interpreter verified by execution: CPython **3.12.10**, AMD64,
  Microsoft Store distribution, compiler MSC v.1943.
- The `py` launcher is absent. The interpreter was located from
  `HKCU\Software\Python\PythonCore\3.12\InstallPath`, not by assuming `python`
  aliases resolve in the restricted shell.
- Exact proposed Argos 1.11.0, CTranslate2 4.8.5, SentencePiece 0.2.1 and
  PyInstaller 6.22.3 releases were confirmed using official PyPI release JSON.
  Matching CPython 3.12 Windows x64 wheels exist for CTranslate2 and
  SentencePiece, and Windows x64/pure-Python wheels for the other two.
- Project dependencies will be installed only into `.venv`; no global project
  dependency installation is permitted.
- Recovery inspection found the nine reviewed planning Markdown files and
  `models/provenance.json` present but ignored and untracked. Tracking was
  restored explicitly, including the change's `.openspec.yaml`, without
  changing `.gitignore` or adding model binaries. No commit was created.
  `.venv`, downloads, runtime state, `build`, and `dist` remain ignored.

## Completed environment checks

- Created a fresh project-local `.venv` with the verified interpreter. Installed
  the pinned lock toolchain there, generated both transitive hash locks from
  `pyproject.toml`, and installed the development/build graph with
  `--require-hashes --only-binary=:all:`. Runtime selections are constrained to
  those same development/build versions. Installation completed successfully.
- `cmd /d /c scripts\setup.cmd` passed, including hash-locked dependencies,
  editable local package installation with `--no-deps --no-build-isolation`,
  and `pip check` reporting no broken requirements.
- `scripts\python.cmd scripts\check_environment.py` passed all imports:
  CTranslate2, SentencePiece, Torch, SpaCy, Stanza, MiniSBD, ONNX Runtime, Argos
  package/SBD/translation modules, and PyInstaller. Argos paths were isolated
  under temporary ignored `runtime/` state before import. No model was loaded.
  STANZA was selected only to avoid import-time fallback behavior in this
  import-only check; this is not an SBD strategy selection or offline proof.
- The module reports `0.1.0` through the CMD interpreter wrapper.
  `scripts\test.cmd --version` reports pytest 8.4.2. These initial checks
  preceded the unit/protocol/model tests described below.
- A copy of the interpreter wrapper in an ignored directory with no `.venv`
  refused to run and returned exit code 2. Foundation Python files passed
  `compileall` syntax checks.
- The restricted automation shell cannot launch the Microsoft Store base
  interpreter; execution with the permitted host access succeeded. Ordinary
  CMD outside that restricted shell is the documented contributor workflow.

Recorded tools: pip 25.3, pip-tools 7.5.2, setuptools 80.9.0, wheel 0.45.1,
build 1.3.0, pytest 8.4.2. Runtime imports include unchanged Argos 1.11.0,
CTranslate2 4.8.5, SentencePiece 0.2.1, Stanza 1.10.1, SpaCy 3.8.18,
Torch 2.15.0, MiniSBD 0.9.5, ONNX Runtime 1.31.1, and PyInstaller 6.22.3.
The complete transitive selections are in the locks.

| Lock | SHA-256 |
|---|---|
| `requirements.lock` | `fedef8fa7c20478bca60f3fb0374cd4fa8ac660fba30c5c39ec8b8ffa9bfb2b4` |
| `requirements-dev.lock` | `322fcb5f315dc12a2093084bd29bc2f88dafc7073250b434ac1ce8ffeefb65a9` |

## Current progress and remaining verification

The host-local A1 environment checks and A2 compatibility/protocol work passed
in the previous implementation session. Clean Windows 10 22H2 and Windows 11
images remain unavailable; this is an A4 acceptance gate, not an A1 blocker.
The development host reports build
26300.9818 / display version 26H2 / CoreSingleLanguage, but is a development
host with Python and dependencies. The Windows registry's legacy ProductName
string says Windows 10; build/platform reporting identifies the Windows 11
family. Do not use that legacy string as Windows 10 acceptance evidence.

No Windows Sandbox executable, VirtualBox/VMware executable at the checked
standard paths, or Hyper-V `Get-VM` command was found. This does not prove no VM
infrastructure exists elsewhere. The user confirmed that clean test environments
are not available yet; both OS acceptance rows remain pending.

The three initial Stanza configurations failed (implicit network attempt,
legacy `packages` metadata, then `feat_dropout` checkpoint incompatibility).
The subsequently authorized, supported package-local MiniSBD path passed nine
real translations with retained resources and zero audited Python network or
subprocess attempts. See [compatibility-spike.md](compatibility-spike.md) for
exact identities, commands, quality limitations, and historical failure evidence.
The original archive and dependency pins remain unchanged. Python audit hooks
are not OS-level network isolation or clean-machine proof.

The source worker implements bounded protocol v1, readiness, isolated paths,
retained Argos resources, and immutable staged local provisioning. The previous
session reported 38 passing unit/integration tests, successful `pip check`, and
syntax checks. Recovery found 38 cached pytest node IDs; that cache alone does
not prove a fresh successful run. Recovery added synthetic corrupt-archive,
identity/version, interrupted-staging, and existing-install preservation tests;
all 16 tests in `tests/unit/test_backend.py` passed without ML imports. Together
with the prior real active-worker concurrency check, this completes 3.6.
The task checklist now records 27/47 complete. Licensing clearance (3.2) and OS-denied networking
(3.8) remain pending. A3's recorded exit covers local validation only.

## Packaging failure and recovery evidence

The onedir build spec, build helper, and relocated validation harness exist.
An earlier build produced an executable, but frozen local provisioning failed
with `BACKEND_UNAVAILABLE`; `build/packaged-validation.json` records `passed:
false`. No standalone translation acceptance or complete performance baseline
has passed. The existing distribution must not be treated as the latest source.

The latest `build/build-result.json` records exit code 1 after 176.18 seconds.
Its log ends in `MemoryError` while PyInstaller's Torch hook collects submodules
in an isolated child process. Source hashes in that report still matched during
the read-only recovery audit. The failed build did not replace the earlier EXE.
Logs are overwritten by the build helper, so preserve them before another run.

The interrupted session also observed a source Torch `shm.dll` initialization
failure, CLR initialization failure, and Windows error 1450 (insufficient system
resources). These observations do not establish a Unicode-path defect or the
cause of the VS Code crash. On recovery, no Python/PyInstaller/worker process
was running; approximately 4.6 GiB RAM was available and committed memory was
12.1 GiB against a 23.8 GiB limit. No System event 2004 was found in the checked
two-day period. Crash-time memory measurements and a VS Code crash report are
missing. Heavy ML packaging resource pressure is a supported hypothesis, not a
confirmed editor-crash diagnosis.

The resumed session's single source readiness/shutdown diagnostic passed within
its 60-second limit (43.44 seconds elapsed). It used the existing provisioned
model and fresh state, with Python socket/process audit blocking before backend
imports. Health returned ready, stdout contained only the two expected protocol
responses, and stderr was empty. The report is `runtime/recovery-source.json`.
System committed memory before/after was about 11.7/12.9 GiB against a 23.8 GiB
limit; available RAM was about 5.1/3.9 GiB. These snapshots do not capture peak
usage or establish a cold-start performance baseline.

The existing executable then passed `info`, real warm-up/readiness, and shutdown
at its original location with development variables removed, System32-only
PATH, and a different working directory. Its diagnostic took 46.02 seconds with
empty stderr (`runtime/recovery-frozen.json`). It is still an older build, not
proof that the latest source has been frozen successfully.

The relocated smoke harness subsequently reproduced the generic frozen
provisioning failure (`runtime/recovery-packaged-validation.json`). Provisioning
failed before repeated translation and measurement/ZIP generation. During that
run, system available RAM fell to about 440 MiB and committed memory reached
18.1 GiB of 23.8 GiB. A process snapshot did not show the worker as the dominant
private-memory consumer; no claim is made that the harness alone caused the
pressure. Other applications were not stopped.

The passing original-location warm-up and failing relocated provisioning are
different operations. They do not isolate Unicode paths, provisioning/staging,
DLL resolution, or transient host pressure as the cause. The old executable
lacks the current source's initialization traceback diagnostic. Task 4.1 stays
open, and no new standalone or clean-machine acceptance is claimed. Pause
native runs/builds here; the next packaging investigation needs sufficient host
headroom and a diagnostic build that retains the underlying frozen traceback.
Preserved original reports are under `runtime/recovery-20261107-002631/`.

Do not reinstall, refresh locks,
redownload unchanged assets, or weaken native dependency/security checks to
work around this failure. Both clean OS rows, license/source-delivery review,
native runtime audit, and A5 release validation remain final completion gates.

## Proposed upstream optional-Stanza adoption

The subsequent isolated investigation passed actual model inference using
unmodified upstream commit `17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88`
(metadata 1.11.1), without installed/loaded Stanza or Torch. A simulated spaCy
exclusion and a minimal upstream backport comparison also passed. Prefer the
unmodified upstream source, subject to explicit adoption approval and reviewed
source/wheel provenance. See [evaluation and proposed next steps](upstream-argos-evaluation.md).
The working environment, production pins/locks, backend guard, and packaging
spec remain unchanged; no new executable build occurred. This supersedes the
recommendation to immediately retry the old graph's diagnostic build. Progress
remains 27/47; task 4.2 now includes approved adoption and actual-worker
revalidation before packaging. Frozen relocation, measured memory reduction,
licensing and clean OS acceptance remain unresolved.
