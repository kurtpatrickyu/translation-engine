import importlib.util
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('verify_dependency_locks', ROOT / 'scripts/verify_dependency_locks.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def lock_root(tmp_path):
    (tmp_path / 'packaging').mkdir()
    for name in ('requirements.lock', 'requirements-dev.lock', 'packaging/argos-upstream.json'):
        shutil.copyfile(ROOT / name, tmp_path / name)
    return tmp_path


def test_rejects_same_version_unreviewed_argos_hash(lock_root):
    path = lock_root / 'requirements.lock'
    path.write_text(path.read_text().replace('825b1bf872390547bad6c1fcf1f12e5967e2fe6b44ca1e8a82e17a8dd79a2aa0', '0' * 64))
    with pytest.raises(ValueError, match='Unreviewed Argos hash'):
        module.verify(lock_root)


def test_rejects_reintroduced_torch(lock_root):
    path = lock_root / 'requirements-dev.lock'
    path.write_text(path.read_text() + '\ntorch==2.15.0\n')
    with pytest.raises(ValueError, match='Forbidden dependency'):
        module.verify(lock_root)


def test_rejects_inconsistent_runtime_pin(lock_root):
    path = lock_root / 'requirements.lock'
    path.write_text(path.read_text().replace('ctranslate2==4.8.5', 'ctranslate2==4.8.6'))
    with pytest.raises(ValueError, match='version mismatch'):
        module.verify(lock_root)
