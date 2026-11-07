"""Application operations over a minimal explicitly constructed backend."""

import importlib.metadata

from . import __version__
from .errors import EngineError
from .protocol import COMMANDS, LIMITS

PAIR = {"source": "zh", "target": "en"}


class Service:
    def __init__(self, backend):
        self.backend = backend
        self.initialized = False
        self.failure = None

    def ensure_ready(self):
        if not self.initialized:
            self.initialized = True
            try:
                self.backend.initialize()
            except EngineError as error:
                self.failure = error
            except Exception:
                self.failure = EngineError("BACKEND_UNAVAILABLE", "Backend initialization failed; verify local resources and restart.")
        if self.failure:
            raise self.failure

    def ready_pairs(self):
        return [dict(PAIR)] if self.initialized and self.failure is None else []

    def dispatch(self, request):
        command = request["command"]
        if command == "info":
            try:
                version = importlib.metadata.version("argostranslate")
            except importlib.metadata.PackageNotFoundError:
                version = None
            return {"engine_version": __version__, "protocol_version": 1, "backend": "argos",
                    "argos_version": version, "commands": list(COMMANDS),
                    "configured_pairs": [{**PAIR, "model_version": "1.9", "sbd_version": "v0.0.1"}],
                    "ready_pairs": self.ready_pairs(), "limits": dict(LIMITS)}
        if command == "health":
            try:
                self.ensure_ready()
            except EngineError:
                pass
            return {"alive": True, "ready": self.failure is None,
                    "ready_pairs": self.ready_pairs(), "error": self.failure.payload() if self.failure else None}
        if command == "shutdown":
            return {"shutdown": True}
        if (request["source"], request["target"]) != ("zh", "en"):
            raise EngineError("UNSUPPORTED_LANGUAGE", "Only configured zh to en translation is supported.")
        self.ensure_ready()
        return {**PAIR, "text": self.backend.translate(request["text"])}

    def close(self):
        self.backend.close()
