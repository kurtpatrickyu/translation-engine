"""Compare Python/native path loading and serialized loading of the pinned model."""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import tempfile
import zipfile

from translation_engine.assets import MODEL_SHA256, PACKAGE_NAME
from translation_engine.provision import sha256


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        raise SystemExit('Refusing to overwrite existing evidence')
    attempts = []

    def audit(event, arguments):
        if event in {'socket.connect', 'socket.getaddrinfo', 'socket.sendto', 'subprocess.Popen', 'os.system'}:
            attempts.append(event)
            raise RuntimeError('Forbidden network/process attempt: ' + event)

    sys.addaudithook(audit)
    import sentencepiece as spm
    archive = root / 'downloads/translate-zh_en-1_9.argosmodel'
    if sha256(archive) != MODEL_SHA256:
        raise ValueError('Pinned archive hash mismatch')
    with zipfile.ZipFile(archive) as source:
        data = source.read(PACKAGE_NAME + '/sentencepiece.model')
    report = dict(python=sys.version, os=platform.platform(), sentencepiece=importlib.metadata.version('sentencepiece'),
                  model_sha256=hashlib.sha256(data).hexdigest(), model_bytes=len(data), paths=[], network_attempts=attempts)
    corpus = ['你好，世界！', '不锈钢保温杯，容量500毫升。', 'Alice café 😊 _ underscores']
    baseline = spm.SentencePieceProcessor(model_proto=data)
    with tempfile.TemporaryDirectory(prefix='sentencepiece-repro-', dir=root / 'runtime') as temporary:
        for name in ('ascii', 'ascii spaces', 'Caf\u00e9 \u4e2d\u6587 \U0001f60a'):
            path = Path(temporary) / name / 'sentencepiece.model'
            path.parent.mkdir()
            path.write_bytes(data)
            read = path.read_bytes()
            observation = dict(path=str(path), python_read_matches=read == data)
            try:
                native = spm.SentencePieceProcessor(model_file=str(path))
                observation['native_file_load'] = 'passed'
                assert all(native.encode(text, out_type=str) == baseline.encode(text, out_type=str) for text in corpus)
            except OSError as error:
                observation.update(native_file_load='failed', native_error=str(error))
            serialized = spm.SentencePieceProcessor(model_proto=read)
            assert all(serialized.encode(text, out_type=str) == baseline.encode(text, out_type=str)
                       and serialized.decode_pieces(serialized.encode(text, out_type=str)) ==
                       baseline.decode_pieces(baseline.encode(text, out_type=str)) for text in corpus)
            observation['serialized_load_and_outputs'] = 'passed'
            report['paths'].append(observation)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
