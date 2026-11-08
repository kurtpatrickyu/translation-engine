"""Package-local SentencePiece loading through Python's Unicode filesystem API."""

import sentencepiece as spm
from argostranslate.tokenizer import SentencePieceTokenizer


# The unchanged pinned model is 804,374 bytes. Bound the temporary serialized
# buffer; validate_install verifies its receipt hash before this adapter is used.
MAX_MODEL_PROTO_BYTES = 1024 * 1024


class SerializedSentencePieceTokenizer(SentencePieceTokenizer):
    """Inherit Argos encode/decode; retain one lazily initialized processor."""

    def lazy_processor(self):
        if self.processor is None:
            with self.model_file.open('rb') as stream:
                model_proto = stream.read(MAX_MODEL_PROTO_BYTES + 1)
            if not model_proto or len(model_proto) > MAX_MODEL_PROTO_BYTES:
                raise ValueError('SentencePiece model exceeds the reviewed serialized size bound or is empty')
            # Native filename opening fails for Unicode paths on Windows 0.2.1.
            # No byte buffer is retained by this adapter after initialization.
            self.processor = spm.SentencePieceProcessor(model_proto=model_proto)
        return self.processor


def adapt_package_tokenizer(package):
    """Adapt only this validated package, before PackageTranslation/warm-up."""
    if type(package.tokenizer) is not SentencePieceTokenizer or package.tokenizer.processor is not None:
        raise ValueError('Unexpected Argos tokenizer type or lifecycle; review compatibility')
    package.tokenizer = SerializedSentencePieceTokenizer(package.tokenizer.model_file)
