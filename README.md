# Piano Analyzer

Transcribe recorded piano performances using audio and visual evidence. Transkun proposes notes from audio; MediaPipe fingertip observations provide supporting evidence and mark uncertain notes for review.

[![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.11-5C3EE8?style=flat-square)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-0097A7?style=flat-square)](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-334155?style=flat-square)](LICENSE)

[![Quick Start](https://img.shields.io/badge/Quick_Start-1F2937?style=for-the-badge)](#quick-start)
[![Architecture](https://img.shields.io/badge/Architecture-1F2937?style=for-the-badge)](docs/architecture.md)
[![Evaluation](https://img.shields.io/badge/Evaluation-1F2937?style=for-the-badge)](docs/evaluation.md)
[![Original Report](https://img.shields.io/badge/Original_Report-1F2937?style=for-the-badge)](docs/reports/Piano_Analyzer_Public_Report.pdf)

![Audio and video evidence flow](assets/architecture.svg)

## What it does

- Processes recorded piano video with audio over a calibrated C3-C7 range: 49 keys.
- Tracks up to two hands using MediaPipe's fingertip landmarks.
- Runs audio transcription and video tracking independently, in parallel by default.
- Retains audio notes when hands are occluded and flags notes lacking visual support.
- Exports `performance.mid`, `annotated.mp4`, and optional `evidence.csv`.

Audio-estimated note endings and velocity are preserved. Fingertip proximity does not establish physical key depression, key release, or strike strength. The application uses a pretrained Transkun model; it does not train a new transcription model.

## Quick start

The current setup targets **Python 3.10** and was developed on Windows. It uses two Python environments: `.venv` for MediaPipe and output processing, and `.venv-transkun` for audio inference.

From the repository root in PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .

py -3.10 -m venv .venv-transkun
.\.venv-transkun\Scripts\python.exe -m pip install --upgrade pip
.\.venv-transkun\Scripts\python.exe -m pip install -r requirements-transkun.txt

.\.venv\Scripts\python.exe scripts/download_model.py
.\.venv\Scripts\python.exe scripts/check_setup.py
```

See the [setup guide](docs/setup.md) for dependency details, Linux commands, and troubleshooting. Model downloads are kept local and are not committed.

Place your own constant-frame-rate recording with piano audio at `videos/performance.mp4`, then calibrate and run:

```powershell
.\.venv\Scripts\python.exe piano_handtracking.py --input "videos/performance.mp4" --calibration "calibration/performance/keyboard.json" --calibrate --output "results/performance" --save-evidence --show
```

Select four keyboard corners and the five C-key anchors when prompted. Subsequent runs can omit `--calibrate` while the keyboard and camera position remain unchanged. `--show` enables the rendering preview; pressing Q closes the preview. Use `--sequential` to run the two analysis stages one after another for timing comparisons.

Recordings and generated results are excluded from Git. [Example calibration format](examples/README.md).

## Outputs

| File | Contents |
| --- | --- |
| `performance.mid` | Detected pitches with audio-estimated onset, ending, and velocity |
| `annotated.mp4` | Input video and audio with keyboard, hand, and note overlays |
| `evidence.csv` | Optional per-note audio provenance, fingertip support, visibility, and review flags |

`audio_and_video` means sufficient fingertip support was found near the onset. `audio_only` means the note is retained from audio and needs review. These labels describe evidence, not a calibrated probability of correctness.

## Verification

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

The 21 existing unit tests cover note matching, evidence fusion, ending descriptions, worker overlap, and the isolated Transkun interface. Model inference is mocked in the interface tests. Unit-test success does not measure transcription accuracy or confirm a complete video run. The [CI workflow](.github/workflows/tests.yml) installs the core environment and runs the suite on Windows.

With both environments and models installed, exercise the full pipeline without a personal recording:

```powershell
.\.venv\Scripts\python.exe scripts/smoke_test.py
```

This generates one second of blank video and silence, runs both models, checks MIDI/video/CSV output, and removes its temporary files. It verifies setup and integration, not piano-transcription accuracy. CPU model loading makes it substantially slower than the unit suite.

## Results and limitations

The [October 2026 technical report](docs/reports/Piano_Analyzer_Public_Report.pdf) evaluates the **original implementation**, before the current Transkun-based pipeline. Its reported accuracy and throughput are not results for this version.

The current version has no published held-out accuracy or throughput benchmark. See [evaluation methodology and the historical frame-count discrepancy](docs/evaluation.md).

Current limitations include manual calibration, a fixed keyboard range, sensitivity to camera movement and occlusion, and audio-model errors on difficult passages. Audio note endings and velocity are estimates; physical key releases and playing dynamics are not directly measured. Only pitch and onset matching are implemented in the project evaluator.

## Project structure

```text
piano_handtracking.py     CLI and parallel analysis coordination
piano_calibration.py      Manual keyboard calibration
piano_keyboard.py         Perspective transform and key geometry
piano_press.py            Fingertip observations and support scoring
piano_transkun.py         Isolated audio-model subprocess
piano_fusion.py           Audio/video evidence and CSV output
piano_expression.py       Visual observations near note endings
piano_notes.py            MIDI export
piano_video.py            Overlay rendering
piano_sound.py            FFmpeg audio extraction and remuxing
piano_evaluate.py         One-to-one pitch/onset evaluation
tests/                   Unit tests
scripts/                 Model download and environment checks
docs/                    Setup, architecture, evaluation, and original report
examples/                Synthetic calibration example
```

## Attribution and license

Original project code is licensed under [MIT](LICENSE). Transkun is by Yujia Yan and collaborators; MediaPipe is by Google. Earlier prototype work also drew on the CannyCam example. ChatGPT assisted with implementation and documentation. Full acknowledgements, upstream links, and dataset references are in [third-party notices](THIRD_PARTY_NOTICES.md).
