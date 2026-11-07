# Standard hooks first. Add targeted hooks only for demonstrated frozen failures.
from pathlib import Path
from PyInstaller.utils.hooks import copy_metadata
project = Path(SPECPATH).parent
# Frozen smoke test: version checks failed because these dist-info directories
# were absent under the default hooks. No broad data/hidden-import collection.
metadata = []
for distribution in ('argostranslate', 'ctranslate2', 'sentencepiece', 'minisbd'):
    metadata += copy_metadata(distribution)
a = Analysis(
    [str(Path(SPECPATH) / 'worker_entry.py')],
    pathex=[str(project / 'src')],
    binaries=[],
    datas=metadata,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    # Actual source-worker tests pass with spaCy unavailable. Frozen validation
    # must independently confirm this reduced MiniSBD-only graph is complete.
    excludes=['spacy', 'stanza', 'torch'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='translation-engine-worker',
    debug=False,
    strip=False,
    upx=False,
    console=True,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='translation-engine-worker')
