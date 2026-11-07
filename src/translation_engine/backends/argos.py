"""The sole backend: retained direct Argos translation with explicit local MiniSBD."""

from contextlib import redirect_stdout
import importlib.metadata
import logging
import sys

from ..assets import PACKAGE_NAME
from ..errors import EngineError
from ..provision import validate_install


class ArgosBackend:
    def __init__(self, config):
        self.config = config
        self.engine = None

    def initialize(self):
        if self.engine is not None:
            return
        path = self.config.models / PACKAGE_NAME
        alternatives = [candidate for candidate in self.config.models.glob("*/metadata.json")
                        if candidate.parent != path and not candidate.parent.name.startswith(".")]
        if alternatives:
            raise EngineError("MODEL_INCOMPATIBLE", "Use an isolated directory containing only the pinned direct model.")
        validate_install(path)
        for name, version in {"argostranslate": "1.11.1", "ctranslate2": "4.8.5",
                              "sentencepiece": "0.2.1", "minisbd": "0.9.5"}.items():
            try:
                if importlib.metadata.version(name) != version:
                    raise EngineError("BACKEND_UNAVAILABLE", "Restore the reviewed dependency lock.")
            except importlib.metadata.PackageNotFoundError as error:
                logging.error("Required runtime distribution metadata is missing: %s", name)
                raise EngineError("BACKEND_UNAVAILABLE", "Required runtime metadata is missing; restore dependencies or rebuild the worker.") from error
        self.config.configure_argos()
        try:
            # Argos settings can print config failures; keep those on stderr.
            with redirect_stdout(sys.stderr):
                from argostranslate import package, translate
                # Argos explicitly sets INFO on this child logger and logs text.
                logging.getLogger("argostranslate.utils").setLevel(logging.WARNING)
                model = package.Package(path)
                from .tokenizer import adapt_package_tokenizer
                adapt_package_tokenizer(model)
                engine = translate.PackageTranslation(
                    translate.Language("zh", "Chinese"), translate.Language("en", "English"), model,
                )
                if type(engine.sentencizer).__name__ != "MiniSBDSentencizer":
                    raise EngineError("BACKEND_UNAVAILABLE", "Restart with isolated MiniSBD configuration.")
                if not engine.translate("你好，世界！").strip():
                    raise ValueError("Warm-up produced no output")
            self.engine = engine
        except EngineError:
            raise
        except Exception as error:
            # Initialization uses only the fixed warm-up, never request text.
            logging.exception("Local Argos initialization failed")
            raise EngineError("BACKEND_UNAVAILABLE", "Local Argos initialization failed; inspect stderr and verify dependencies/resources.") from error

    def translate(self, text):
        try:
            with redirect_stdout(sys.stderr):
                return self.engine.translate(text) if text else ""
        except Exception as error:
            raise EngineError("TRANSLATION_FAILED", "Translation failed; restart the worker if the failure persists.") from error

    def close(self):
        self.engine = None
