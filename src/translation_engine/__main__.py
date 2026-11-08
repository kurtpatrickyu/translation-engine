"""Standalone worker and explicit local provisioning entry point."""

import argparse
import logging
from pathlib import Path
import sys

from translation_engine import __version__
from translation_engine.config import Config
from translation_engine.errors import EngineError


def main() -> int:
    parser = argparse.ArgumentParser(description="Standalone offline translation engine")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--models-dir")
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("command", nargs="?", choices=("provision-model",))
    parser.add_argument("--file", type=Path)
    parser.add_argument("--sbd-file", type=Path)
    args = parser.parse_args()
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    try:
        config = Config.resolve(args.models_dir, args.state_dir)
        if args.command == "provision-model":
            if not args.file or not args.sbd_file:
                parser.error("provision-model requires --file and --sbd-file")
            from translation_engine.provision import provision
            from translation_engine.backends.argos import ArgosBackend
            def check_runtime(packages):
                backend = ArgosBackend(Config(packages, config.state))
                try:
                    backend.initialize()
                finally:
                    backend.close()
            path = provision(args.file, args.sbd_file, config.models, check_runtime)
            print(f"Provisioned {path}. Restart any running worker.", file=sys.stderr)
            return 0
        if args.file or args.sbd_file:
            parser.error("Asset files apply only to provision-model")
        from translation_engine.backends.argos import ArgosBackend
        from translation_engine.service import Service
        from translation_engine.worker import run
        return run(sys.stdin.buffer, sys.stdout.buffer, Service(ArgosBackend(config)))
    except (ValueError, EngineError, OSError) as error:
        print(f"Startup/provisioning failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
