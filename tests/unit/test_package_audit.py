import importlib.util
from pathlib import Path


spec = importlib.util.spec_from_file_location('package_audit', Path(__file__).resolve().parents[2] / 'scripts/audit_windows_package.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_visual_cpp_is_never_assumed_to_be_in_windows():
    assert audit.dependency_kind('MSVCP140.dll', set()) == 'unresolved'
    assert audit.dependency_kind('VCRUNTIME140_1.dll', set()) == 'unresolved'
    assert audit.dependency_kind('MSVCP140.dll', {'msvcp140.dll'}) == 'bundled'
    assert audit.dependency_kind('unknown.dll', set()) == 'unresolved'
    assert audit.dependency_kind('MSVCP140.dll', set(), external_vc_runtime=True) == 'external_vc_runtime_required'
    assert audit.dependency_kind('unknown.dll', set(), external_vc_runtime=True) == 'unresolved'
    assert audit.dependency_kind('msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll', set(),
                                 external_vc_runtime=True) == 'unresolved'


def test_api_contract_is_distinct_from_bundled_or_missing_file():
    assert audit.dependency_kind('api-ms-win-crt-runtime-l1-1-0.dll', set()) == 'windows_api_contract'
    assert audit.dependency_kind('KERNEL32.dll', set()) == 'windows_desktop_dll'


def test_side_by_side_os_components_do_not_exempt_external_host_modules(tmp_path):
    bundle, windows = tmp_path / 'bundle', tmp_path / 'Windows'
    assert audit.module_scope(bundle / '_internal/python312.dll', bundle, windows) == 'bundle'
    assert audit.module_scope(windows / 'System32/ucrtbase.dll', bundle, windows) == 'windows_system32'
    known = windows / 'WinSxS/amd64_microsoft.windows.gdiplus_6595b64144ccf1df_1.1_test/GdiPlus.dll'
    assert audit.module_scope(known, bundle, windows) == 'windows_side_by_side_component'
    for path in [windows / 'SysWOW64/T_Prevent64.dll', windows / 'WinSxS/arbitrary/vendor.dll', tmp_path / '.venv/python312.dll']:
        assert audit.module_scope(path, bundle, windows) == 'external_host'
