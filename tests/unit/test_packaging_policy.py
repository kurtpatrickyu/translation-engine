"""Exercise the spec's actual post-Analysis policy without running PyInstaller."""

import ast
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace


def test_spec_excludes_only_four_ordinary_vc_basenames():
    spec = Path(__file__).resolve().parents[2] / 'packaging/worker.spec'
    tree = ast.parse(spec.read_text(encoding='utf-8'))
    policy = [node for node in tree.body if isinstance(node, ast.Assign) and any(
        (isinstance(target, ast.Name) and target.id == 'external_vc')
        or (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
            and target.value.id == 'a' and target.attr == 'binaries')
        for target in node.targets)]
    removed = ['msvcp140.dll', 'package/MSVCP140_1.DLL',
               r'package\VCRUNTIME140.dll', 'VCRUNTIME140_1.dll']
    retained = ['numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll',
                'python312.dll', 'ctranslate2/ctranslate2.dll', 'ctranslate2/libiomp5md.dll',
                'onnxruntime/capi/onnxruntime.dll', 'sentencepiece/_sentencepiece.pyd',
                'numpy.libs/libscipy_openblas64_.dll', 'msvcp140_2.dll', 'other.dll']
    entries = [(name, 'source/' + name, 'BINARY') for name in removed + retained]
    analysis = SimpleNamespace(binaries=entries)
    namespace = {'Path': PureWindowsPath, 'a': analysis}
    exec(compile(ast.Module(body=policy, type_ignores=[]), str(spec), 'exec'), namespace)
    assert analysis.binaries == entries[len(removed):]
