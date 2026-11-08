"""Check the core environment and optional model environment without transcription."""
import argparse
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
MODEL_SHA256 = '97952348cf6a6a4915c2ea1496b4b37ebabc50cbbf80571435643c455f2b0482'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core-only', action='store_true', help='Check only core dependencies; no models required')
    args = parser.parse_args()
    issues = []
    print(f'Python: {sys.version.split()[0]}')
    if sys.version_info[:2] != (3, 10):
        issues.append('Use Python 3.10 for this dependency set.')
    for package in ['numpy', 'opencv-contrib-python', 'mediapipe', 'pretty_midi', 'imageio-ffmpeg', 'setuptools']:
        try:
            print(f'{package}: {version(package)}')
        except PackageNotFoundError:
            issues.append(f'Missing core dependency: {package}')
    if not issues:
        import cv2
        import mediapipe
        import pretty_midi
        import imageio_ffmpeg
        result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-version'], capture_output=True, text=True, timeout=20)
        if result.returncode:
            issues.append('The bundled FFmpeg executable did not start.')
        else:
            print(result.stdout.splitlines()[0])
    if not args.core_only:
        model = ROOT / 'models' / 'gesture_recognizer.task'
        if not model.is_file():
            issues.append('GestureRecognizer model missing; run scripts/download_model.py.')
        elif hashlib.sha256(model.read_bytes()).hexdigest() != MODEL_SHA256:
            issues.append('GestureRecognizer model digest does not match the supported file.')
        else:
            print('GestureRecognizer model: verified')
        executable = 'Scripts/python.exe' if os.name == 'nt' else 'bin/python'
        audio_python = ROOT / '.venv-transkun' / executable
        if not audio_python.is_file():
            issues.append('Audio environment missing; create .venv-transkun and install requirements/transkun.txt.')
        else:
            probe = (
                "from importlib.metadata import version; from importlib.resources import files; "
                "import json, torch, soxr, moduleconf; "
                "p=files('transkun').joinpath('pretrained'); "
                "assert p.joinpath('2.0.conf').is_file() and p.joinpath('2.0.pt').is_file(), 'Transkun V2 resources missing'; "
                "print(json.dumps({k:version(k) for k in ['transkun','torch','torchaudio','numpy','pretty_midi']}))"
            )
            result = subprocess.run([str(audio_python), '-c', probe], capture_output=True, text=True, timeout=90)
            if result.returncode:
                issues.append('Audio environment check failed: ' + result.stderr.strip())
            else:
                print('Audio environment: ' + result.stdout.strip())
    if issues:
        for issue in issues:
            print('ERROR: ' + issue, file=sys.stderr)
        raise SystemExit(1)
    print('Setup checks passed' + (' (core only).' if args.core_only else '.'))


if __name__ == '__main__':
    main()
