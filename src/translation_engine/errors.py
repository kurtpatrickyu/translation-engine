"""Stable public failures, without dependency tracebacks on the wire."""


class EngineError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.code, self.message, self.retryable = code, message, retryable

    def payload(self) -> dict:
        return {"code": self.code, "message": self.message, "retryable": self.retryable}
