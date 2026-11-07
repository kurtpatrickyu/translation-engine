# Optional-Stanza upstream evaluation

Status: investigation completed on 2026-11-07; the user subsequently approved A.
See [adoption results](../../../docs/argos-migration.md) for the subsequent runtime and diagnostic.
The following records the investigation before approval: no executable build was run. The working `.venv`, application source,
`pyproject.toml`, and production locks remain unchanged. OpenSpec progress remains
27/47; these experiments do not complete packaging acceptance.

## Exact source and relevant differences

Preferred candidate: [upstream commit
17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88](https://github.com/argosopentech/argos-translate/commit/17ed1a9b055c5ba1b51d76b683bbb0c64e2a4a88),
committed 2026-08-08, parent `75169ae18e1c243fc0a55eff79f96b846d773a23`.
Its package metadata reports 1.11.1; that version alone is not its source identity
and does not identify an interchangeable PyPI artifact.

The optional-Stanza change has four functional/metadata parts:

- `sbd.py`: catch a missing Stanza import and retain `stanza = None`.
- `translate.py`: avoid choosing Stanza automatically when it is absent.
- `requirements.txt`: remove Stanza from default requirements.
- `setup.py`: expose `stanza==1.10.1` through the `stanza` extra.

spaCy remains required by default and its existing guarded import is unchanged.
This change tolerates Stanza being absent; it still imports Stanza if installed.
Therefore a fresh candidate environment must omit the extra and unrelated Torch
requirements. An upgrade over the old environment can leave both installed.

Relative to v1.11.0, the exact revision includes 13 commits. Relevant additional
differences are metadata version 1.11.1 and omission of the explicit CTranslate2
compute argument when configured as `auto`; there is also a CLI fix and unrelated
documentation changes. `package.py` has only a removed comment. MiniSBD/tokenizer
algorithms are unchanged in the compared source. Both tested candidates resolved
to `int8_float32` on this host; other hosts still need validation.

## Isolated experiments

All disposable materials are under ignored
`runtime/optional-stanza-investigation/`: source/API snapshots, wheels,
`constraints.txt`, separate `env/`, test scripts, and JSON results. No system-site
packages were enabled. Source wheels were built with the existing pinned build
tools, without dependency installation into the working environment. Default
candidate dependencies were installed only into the disposable environment,
constrained to versions extracted from the existing runtime lock. That pilot
installation was version-constrained, not a newly established hash-locked setup.

| Input/artifact | Captured SHA-256 |
|---|---|
| Exact-commit source ZIP | `0cedceb52ca288b12bb4a33de97f7a8df13bc45dd46f6338754194a27b746343` |
| Upstream experimental 1.11.1 wheel | `f63e8e3ef4e556a4a67bc216f374841c6d81051b8fd3258b3563817649becc3f` |
| Published 1.11.0 source archive | `be43fa826cbac15399a33a90c842dfe504ad6b8fa55e252514e7071f5425b406` |
| Experimental backport wheel | `b81fa900273192c6714d5aa99c7019f2e60bcd740f81dee29c7c8c0b66395829` |

These identify the captured experimental bytes, not a final approved wheel or
proof of byte-identical rebuilding. Retain source revision, source digest,
build-tool versions/recipe, wheel digest, dependency identities, and attribution
when preparing the production candidate.

The commit's signature/authorship was not independently authenticated. Full
revision and captured hash pins do not remove trust in upstream or build tools.
This is a reviewed source snapshot reporting 1.11.1, not evidence of a published
PyPI release. Normal setup should consume the approved wheel rather than execute
remote source builds on every installation.

### A: exact upstream revision

Built the unmodified source archive into a wheel and installed its default
dependencies without the Stanza extra. `pip check` passed. CTranslate2 4.8.5,
SentencePiece 0.2.1, MiniSBD 0.9.5, ONNX Runtime 1.31.1, spaCy 3.8.18, and Thinc
8.3.14 were retained. Stanza and Torch were not installed.

`upstream-default.json` passed ten real translation cases. It loaded 153 spaCy
and 101 Thinc module entries but zero Stanza/Torch entries. A fresh subprocess
with an audit-hook simulation of an unavailable spaCy import also passed
(`upstream-no-spacy.json`), with zero entries for all four frameworks. This is a
source-level exclusion test, not proof of a PyInstaller exclusion or native DLL
completeness. Installed spaCy remains available for default-dependency checks.

### B: minimal upstream backport

Built a disposable `1.11.0+upstream.17ed1a9` wheel using only the four relevant
source/metadata changes, retaining v1.11.0's compute argument behavior. The
published source archive omits `requirements.txt` although `setup.py` reads it;
the experiment reconstructed that file from the archive's own `requires.txt`
metadata. This extra recipe and the patch would need maintenance. The local
version identifies a derivative instead of misrepresenting it as unchanged
1.11.0. The recipe and resulting diff are retained in ignored investigation
storage, not adopted into production tooling.

Replaced only Argos inside the disposable environment. `pip check` passed, as
did the ten-case spaCy-excluded run (`backport-no-spacy.json`). Stanza/Torch were
absent and all ten outputs matched approach A for this corpus.

The disposable environment currently ends with the backport installed. To repeat
A, explicitly reinstall the captured upstream wheel there with `--no-deps`, then
run `test_candidate.py --label upstream`, followed in a fresh subprocess by
`--label upstream --exclude-spacy`. These ignored experiment scripts are not
production adoption tooling or contributor setup commands.

### What the tests establish

Each subprocess uses fresh model/state/cache paths, verifies the unchanged
translation archive and ONNX hashes, calls the current local provisioning
function, and constructs Argos `PackageTranslation` directly. Python audit hooks
block and record socket/DNS/send and process-launch attempts before Argos imports.
The corpus covers Chinese sentences, product details, punctuation, mixed English,
Unicode/emoji, paragraphs, forty sentences, repeated input, and empty text.
Resources are reused and the package-local MiniSBD implementation is selected.
All three runs recorded zero forbidden attempts. Temporary package paths were
cleaned after each run; original model assets were not modified.

At the time of that investigation, the production backend rejected versions other than 1.11.0;
these experiments do not bypass that guard in production or establish worker
protocol conformance for 1.11.1. They do not prove OS-level network isolation,
universal translation equivalence, frozen startup, relocated provisioning,
Windows 10 compatibility, memory reduction, or final distribution size.

## Recommendation and proposed implementation gate

Prefer A: unmodified upstream source at the full commit, built into a reviewed
wheel. It requires no maintained Argos source patch. B works on the exercised
path but adds a backport, derivative identity, source-package repair, and future
rebasing burden without a demonstrated benefit for this engine.

After explicit adoption approval:

1. Retain the full source revision/digest and reviewed changes, use pinned build
   tools, and produce an identified wheel through a small reproducible recipe.
   Record timestamp policy and wheel hash; do not promise byte reproducibility
   before checking it. Consume that exact wheel through hash-verified locks and
   controlled artifact storage/wheelhouse, never a floating branch or an
   unqualified PyPI `1.11.1` substitution. Do not weaken hash enforcement for VCS.
2. Update the project's Argos declaration and runtime version guard, spike pin,
   both lock graphs, and runtime/source provenance. Keep the other retained
   runtime versions and both model hashes unchanged. Regenerate dependency
   closure; remove Stanza/Torch and dependencies now unreferenced, but retain
   shared dependencies and default spaCy requirements. Validate a newly created
   environment with `pip check` and explicit absence checks.
3. Revalidate the actual worker/provisioning path, audit offline imports and
   inference, and enforce response-only stdout. Test a spaCy packaging exclusion;
   confirm Thinc is not collected. Prevent Stanza/Torch collection in the reduced
   candidate and inspect the analysis graph. Retain required CTranslate2,
   SentencePiece, ONNX Runtime, NumPy, and app-local DLL collection.
4. Before the first approved diagnostic build, preserve logs and sample aggregate
   build-process-tree working set/private bytes, per-process peaks, and system
   commit/available memory. Stop on failures; avoid parallel builds. Compare
   runtime idle/ready/peak memory, repeated translation, and ZIP/extracted bytes
   against identified candidate evidence without inventing budgets.
5. Test frozen startup/protocol, missing-resource failures, relocated local
   provisioning and repeated translation using spaces/Unicode paths. The earlier
   relocated failure remains a separate unresolved observation until it passes.

The source contains MIT attribution to retain; removing Torch/Stanza does not
clear MiniSBD AGPLv3 or ONNX/translation-model redistribution obligations.
Licensing/source-delivery review and both clean Windows acceptance rows remain
pending. No publication or production dependency update is authorized by this
investigation.
