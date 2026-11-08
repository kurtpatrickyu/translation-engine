from types import SimpleNamespace

import pytest
from argostranslate.tokenizer import SentencePieceTokenizer

from translation_engine.backends.tokenizer import (
    MAX_MODEL_PROTO_BYTES, SerializedSentencePieceTokenizer, adapt_package_tokenizer,
)


@pytest.mark.parametrize('folder', ['ascii', 'ascii spaces', 'Caf\u00e9 \u4e2d\u6587 \U0001f60a'])
def test_lazy_bounded_load_reuses_processor_and_inherits_behavior(tmp_path, monkeypatch, folder):
    path = tmp_path / folder / 'sentencepiece.model'
    path.parent.mkdir()
    path.write_bytes(b'local serialized model')
    calls = []
    processor = SimpleNamespace(encode=lambda text, out_type: [text], decode_pieces=lambda tokens: '\u2581a_b')

    def construct(**kwargs):
        calls.append(kwargs)
        return processor

    monkeypatch.setattr('translation_engine.backends.tokenizer.spm.SentencePieceProcessor', construct)
    original = SentencePieceTokenizer(path)
    package = SimpleNamespace(tokenizer=original)
    adapt_package_tokenizer(package)
    assert original.processor is None and package.tokenizer.processor is None and not calls
    assert package.tokenizer.encode('你好') == ['你好']
    assert package.tokenizer.decode(['a']) == ' a b'
    assert package.tokenizer.lazy_processor() is processor
    assert calls == [{'model_proto': b'local serialized model'}]
    assert SerializedSentencePieceTokenizer.encode is SentencePieceTokenizer.encode
    assert SerializedSentencePieceTokenizer.decode is SentencePieceTokenizer.decode
    assert set(vars(package.tokenizer)) == {'model_file', 'processor'}


@pytest.mark.parametrize('data', [b'', b'x' * (MAX_MODEL_PROTO_BYTES + 1), b'not a sentencepiece model'],
                         ids=['empty', 'oversized', 'invalid-protobuf'])
def test_invalid_model_never_retains_processor(tmp_path, data):
    path = tmp_path / 'sentencepiece.model'
    path.write_bytes(data)
    tokenizer = SerializedSentencePieceTokenizer(path)
    with pytest.raises((ValueError, RuntimeError)):
        tokenizer.lazy_processor()
    assert tokenizer.processor is None


def test_adapter_rejects_unexpected_or_initialized_tokenizer(tmp_path):
    with pytest.raises(ValueError):
        adapt_package_tokenizer(SimpleNamespace(tokenizer=object()))
    tokenizer = SentencePieceTokenizer(tmp_path / 'model')
    tokenizer.processor = object()
    with pytest.raises(ValueError):
        adapt_package_tokenizer(SimpleNamespace(tokenizer=tokenizer))
