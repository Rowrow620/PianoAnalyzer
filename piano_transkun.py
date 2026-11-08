"""Transkun audio transcription, isolated from MediaPipe's Python environment.

The main program calls transcribe_audio. This file also runs inside
.venv-transkun to load the model and write temporary MIDI.
Source: https://github.com/Yujia-Yan/Transkun
"""
import argparse
from importlib.resources import files
import os
from pathlib import Path
import subprocess

import pretty_midi


def transcribe_audio(audio, pitches):
    root = Path(__file__).parent
    executable = 'Scripts/python.exe' if os.name == 'nt' else 'bin/python'
    python = root / '.venv-transkun' / executable
    midi = audio.parent / 'transkun.mid'
    subprocess.run([str(python), str(Path(__file__).resolve()), '--input', str(audio),
                    '--output', str(midi)], check=True)
    performance = pretty_midi.PrettyMIDI(str(midi))
    return [dict(midi_pitch=note.pitch, start_seconds=note.start, end_seconds=note.end,
                 velocity=note.velocity, audio_source='transkun', end_source='transkun',
                 velocity_source='transkun')
            for instrument in performance.instruments for note in instrument.notes
            if note.pitch in pitches]


def predict_midi(path, device='cpu'):
    import moduleconf
    import numpy as np
    from scipy.io import wavfile
    import soxr
    import torch
    from transkun.Data import writeMidi

    resources = files('transkun').joinpath('pretrained')
    settings = moduleconf.parseFromFile(str(resources.joinpath('2.0.conf')))['Model']
    model = settings.module.TransKun(conf=settings.config).to(device)
    checkpoint = torch.load(str(resources.joinpath('2.0.pt')), map_location=device, weights_only=True)
    weights = checkpoint['best_state_dict'] if 'best_state_dict' in checkpoint else checkpoint['state_dict']
    model.load_state_dict(weights)
    model.eval()
    sample_rate, samples = wavfile.read(path)
    if samples.dtype != np.int16:
        raise ValueError('Transkun input must be PCM16 WAV audio')
    samples = samples.astype(np.float32) / 32768
    if samples.ndim == 1:
        samples = samples[:, None]
    if sample_rate != model.fs:
        samples = soxr.resample(samples, sample_rate, model.fs)
    with torch.inference_mode():
        events = model.transcribe(torch.from_numpy(samples).to(device), discardSecondHalf=False)
    return writeMidi(events)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--device', default='cpu')
    args = parser.parse_args()
    midi = predict_midi(args.input, args.device)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    midi.write(str(args.output))


if __name__ == '__main__':
    main()
