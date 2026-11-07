"""Explicit maintainer acquisition; never called by the worker or inference."""

import argparse
import hashlib
from pathlib import Path
import sys
import tempfile
import urllib.request

from translation_engine.assets import MODEL_SHA256, MODEL_URL, SBD_SHA256, SBD_URL


def main():
    root = Path(__file__).resolve().parents[1]
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        raise SystemExit("Run with the project .venv interpreter.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=root / "downloads")
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    for name, url, expected in (
        ("translate-zh_en-1_9.argosmodel", MODEL_URL, MODEL_SHA256),
        ("zh-hans.onnx", SBD_URL, SBD_SHA256),
    ):
        target = args.destination / name
        if target.exists():
            from translation_engine.provision import sha256
            if sha256(target) != expected:
                raise SystemExit(f"Checksum mismatch in {target}; refusing to replace or update the pin.")
            print(f"Verified {target}")
            continue
        temporary = None
        try:
            digest, size = hashlib.sha256(), 0
            with tempfile.NamedTemporaryFile(dir=args.destination, suffix=".tmp", delete=False) as output:
                temporary = Path(output.name)
                with urllib.request.urlopen(url, timeout=120) as response:
                    while chunk := response.read(1024 * 1024):
                        size += len(chunk)
                        if size > 512 * 1024**2:
                            raise ValueError("Pinned asset download exceeds size limit")
                        digest.update(chunk)
                        output.write(chunk)
            if digest.hexdigest() != expected:
                raise ValueError("Downloaded bytes differ from the reviewed pin")
            temporary.rename(target)
            print(f"Acquired and verified {target}")
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()


if __name__ == "__main__":
    main()
