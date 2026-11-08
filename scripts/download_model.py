"""Download the MediaPipe GestureRecognizer model without overwriting local files."""
import argparse
import hashlib
from pathlib import Path
import tempfile
from urllib.request import urlopen

MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'
MODEL_SHA256 = '97952348cf6a6a4915c2ea1496b4b37ebabc50cbbf80571435643c455f2b0482'
ROOT = Path(__file__).resolve().parent.parent


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'models' / 'gesture_recognizer.task')
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination.exists():
        if sha256(destination) != MODEL_SHA256:
            raise SystemExit(f'Existing file does not match the expected model; left unchanged: {destination}')
        print(f'Model already verified: {destination}')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.download', delete=False) as output:
            temporary = Path(output.name)
            with urlopen(MODEL_URL, timeout=60) as response:
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    output.write(chunk)
        if sha256(temporary) != MODEL_SHA256:
            raise SystemExit('Downloaded model digest did not match; no model was installed.')
        # Exclusive creation also protects a file created while the download ran.
        with destination.open('xb') as output, temporary.open('rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                output.write(chunk)
        print(f'Downloaded and verified: {destination}')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
