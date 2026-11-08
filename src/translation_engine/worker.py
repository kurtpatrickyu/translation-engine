"""One sequential process, response-only stdout, immediate per-frame flush."""

import logging

from .errors import EngineError
from .protocol import encode, frames, parse, valid_id, validate


def run(stream, output, service):
    try:
        for frame in frames(stream):
            identifier = None
            shutdown = False
            try:
                if isinstance(frame, EngineError):
                    raise frame
                request = parse(frame)
                if isinstance(request, dict) and valid_id(request.get("id")):
                    identifier = request["id"]
                validate(request)
                result = service.dispatch(request)
                shutdown = request["command"] == "shutdown"
                response = encode(identifier, result=result)
            except EngineError as error:
                response = encode(identifier, error=error)
            except Exception as error:
                logging.error("Request failed with %s", type(error).__name__)
                response = encode(identifier, error=EngineError("INTERNAL_ERROR", "Unexpected worker failure."))
            output.write(response)
            output.flush()
            if shutdown:
                return 0
        return 0
    except (OSError, BrokenPipeError):
        logging.error("Protocol pipe failed.")
        return 1
    finally:
        service.close()
