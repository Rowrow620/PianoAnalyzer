"""Run the full pipeline on generated video and silence; no personal media needed."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import wave

import cv2
import imageio_ffmpeg
import numpy as np
import pretty_midi

ROOT = Path(__file__).resolve().parent.parent


def main():
    with TemporaryDirectory(prefix='piano-analyzer-smoke-') as directory:
        folder = Path(directory)
        silent_video = folder / 'silent.mp4'
        writer = cv2.VideoWriter(str(silent_video), cv2.VideoWriter_fourcc(*'mp4v'), 10., (1200, 400))
        if not writer.isOpened():
            raise RuntimeError('Cannot create the synthetic test video.')
        try:
            for _ in range(10):
                writer.write(np.full((400, 1200, 3), 180, dtype=np.uint8))
        finally:
            writer.release()
        audio = folder / 'silence.wav'
        with wave.open(str(audio), 'wb') as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(44100)
            output.writeframes(bytes(44100 * 2 * 2))
        video = folder / 'synthetic.mp4'
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-y',
                        '-i', str(silent_video), '-i', str(audio), '-c:v', 'copy',
                        '-c:a', 'aac', '-shortest', str(video)], check=True)
        results = folder / 'output'
        subprocess.run([sys.executable, '-m', 'piano_analyzer',
                        '--input', str(video), '--output', str(results),
                        '--calibration', str(ROOT / 'examples' / 'keyboard.example.json'),
                        '--save-evidence'], cwd=ROOT, check=True, timeout=240)
        for name in ['performance.mid', 'annotated.mp4', 'evidence.csv']:
            if not (results / name).is_file() or (results / name).stat().st_size == 0:
                raise RuntimeError(f'Expected output missing or empty: {name}')
        pretty_midi.PrettyMIDI(str(results / 'performance.mid'))
        capture = cv2.VideoCapture(str(results / 'annotated.mp4'))
        try:
            if not capture.isOpened() or int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) != 10:
                raise RuntimeError('Annotated test video could not be read or has the wrong frame count.')
        finally:
            capture.release()
    print('Full pipeline smoke test passed. Temporary media removed. This is not an accuracy benchmark.')


if __name__ == '__main__':
    main()
