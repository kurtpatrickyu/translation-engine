# Source availability

Project code is [MIT licensed](LICENSE). The worker also includes MiniSBD under
AGPLv3 and other separately licensed code; the complete bundle is not MIT-only.

Each executable download must have adjacent, no-extra-charge
translation-engine-corresponding-source.zip and translation-engine-compliance.zip
on the same GitHub Release. Identify these links in the release description and
keep source accessible for as long as the binary is offered. This is the chosen
AGPL section 6(d) delivery method.

SOURCE_COMMIT.json identifies the immutable binary source commit and original
build-input hashes. repository/ contains that source; sources/worker/ preserves
the build inputs, locks, spec and helpers; evidence/build.json records the original
build. Later packaging and documentation are separated under assembly/.
See [rebuilding instructions](docs/development.md).

The matching MiniSBD 0.9.5 publisher source archive and Python sources are under
sources/minisbd/. Preserve its complete AGPL text, LibreTranslate/Piero Toffanin
attribution and inherited Stanza copyright, Apache notice and credits. No local
MiniSBD modifications were found. sources/tqdm/ supplies the matching MPL-covered
source; preserve the complete MPL/MIT attribution and MPL 2.0 text. The exact
approved Argos source archive and wheel recipe are retained under sources/.

Original supplier texts are retained in LICENSES/ in the repository and licenses/
in generated packages. The inventory and package checksums bind their bytes.
[Third-party notices](THIRD_PARTY_NOTICES.md) index the materials; the
[release policy](docs/releasing.md) records remaining material decisions and
approval requirements. Preserve applicable source duties when redistributing or
modifying the worker.
