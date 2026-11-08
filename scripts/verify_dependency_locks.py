"""Fail closed on a same-version Argos substitution or inconsistent lock graphs."""
import json
from pathlib import Path
import re


def verify(root):
    spec = json.loads((root / 'packaging/argos-upstream.json').read_text())
    graphs = []
    for filename in ('requirements.lock', 'requirements-dev.lock'):
        text = (root / filename).read_text()
        blocks = dict(re.findall(r'(?ms)^([A-Za-z0-9_.-]+)==(.*?)(?=^[A-Za-z0-9_.-]+==|\Z)', text))
        if {'stanza', 'torch'} & blocks.keys():
            raise ValueError('Forbidden dependency in ' + filename)
        argos = blocks['argostranslate']
        if argos.split()[0] != spec['version']:
            raise ValueError('Wrong Argos version')
        if re.findall(r'--hash=sha256:([a-f0-9]{64})', argos) != [spec['wheel_sha256']]:
            raise ValueError('Unreviewed Argos hash')
        graphs.append({name: block.split()[0] for name, block in blocks.items()})
    if not graphs[0].keys() <= graphs[1].keys():
        raise ValueError('Runtime requirement absent from development lock')
    if not all(graphs[0][name] == graphs[1][name] for name in graphs[0]):
        raise ValueError('Runtime/development version mismatch')
    return graphs


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    graphs = verify(root)
    print(f'Verified Argos identity and reduced graphs: {len(graphs[0])} runtime, {len(graphs[1])} development packages')
