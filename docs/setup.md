# Setup

## Environments

Use Python 3.10. The core dependencies are declared in `pyproject.toml`; CPU audio-inference dependencies are pinned separately in `requirements-transkun.txt`.

| Environment | Purpose | Main dependencies |
| --- | --- | --- |
| `.venv` | Video tracking, calibration, MIDI, rendering, tests | MediaPipe 0.10.21, OpenCV 4.11.0.86, NumPy 1.26.4, pretty_midi, imageio-ffmpeg |
| `.venv-transkun` | Audio-model inference | Transkun 2.0.1, PyTorch/torchaudio 2.11.0 CPU, SciPy, soxr, moduleconf |

The audio wrapper resolves `.venv-transkun` relative to `piano_transkun.py`. Create both environments in the repository root and run the entry-point file from the checkout. The core editable install keeps the source modules and local model path together.

The setuptools pin retains compatibility with dependencies that use `pkg_resources`. Avoid combining these environments or upgrading individual pinned packages without checking the complete pipeline.

## Windows

In PowerShell, from the repository root:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .

py -3.10 -m venv .venv-transkun
.\.venv-transkun\Scripts\python.exe -m pip install --upgrade pip
.\.venv-transkun\Scripts\python.exe -m pip install -r requirements-transkun.txt

.\.venv\Scripts\python.exe scripts/download_model.py
.\.venv\Scripts\python.exe scripts/check_setup.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Transkun's dependencies include `ncls`, a native extension. If pip needs to build it from source on your platform, a working C/C++ build toolchain is required. On Windows this is the Microsoft C++ Build Tools with the Windows SDK. Setup diagnostics report the installed versions and model-resource locations without running transcription.

## Linux

The code selects POSIX environment paths on Linux. The following is the equivalent setup; complete Linux video/model processing has not been validated for this release.

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .

python3.10 -m venv .venv-transkun
.venv-transkun/bin/python -m pip install --upgrade pip
.venv-transkun/bin/python -m pip install -r requirements-transkun.txt

.venv/bin/python scripts/download_model.py
.venv/bin/python scripts/check_setup.py
.venv/bin/python -B -m unittest discover -s tests -v
```

OpenCV/MediaPipe may need the distribution's graphics libraries, including OpenGL/EGL support. Interactive calibration and `--show` require a desktop display. The application is not a headless automatic-calibration service.

## Models

`scripts/download_model.py` downloads Google's Gesture Recognizer model to `models/gesture_recognizer.task` and checks its SHA-256 digest. An existing matching model is reused; an unexpected file is never overwritten.

Transkun's installed package supplies `pretrained/2.0.conf` and `pretrained/2.0.pt`. The application loads those resources in the audio environment. Weights remain local; this repository does not redistribute them. See [upstream Transkun](https://github.com/Yujia-Yan/Transkun) for model details and conditions.

The default path runs Transkun on CPU. The main application does not expose a GPU-selection option; this setup does not claim CUDA acceleration.

## Recording and calibration

Use a constant-frame-rate video containing piano audio. Keep the camera fixed, with the C3-C7 keyboard region and fingertips visible. The timestamp calculation uses frame index divided by the video-reported FPS; variable-frame-rate timing has not been validated.

The first run should use `--calibrate`. Click the keyboard corners in the order shown by the application, then select the five C-key centers for C3 through C7. The saved coordinates apply to that camera position and frame size. See the [synthetic format example](../examples/README.md); its coordinates are not a calibration for your recording.

```powershell
.\.venv\Scripts\python.exe piano_handtracking.py --input "videos/performance.mp4" --calibration "calibration/performance/keyboard.json" --calibrate --output "results/performance" --save-evidence --show
```

With GNU Make installed, equivalent targets are available:

```text
make test
make run INPUT=videos/performance.mp4 CALIBRATION=calibration/performance/keyboard.json OUTPUT=results/performance FLAGS="--calibrate --save-evidence --show"
make evaluate OUTPUT=results/performance REFERENCE=videos/performance.mid
```

GNU Make is optional; the direct Python commands work without it.

## Full pipeline check

After installing both environments and models, run:

```powershell
.\.venv\Scripts\python.exe scripts/smoke_test.py
```

The script generates one second of blank video and silence in a temporary directory, uses the synthetic calibration example, and runs the actual MediaPipe/Transkun pipeline. It checks that MIDI, video, and evidence CSV outputs can be produced, then removes the generated media. It requires the real models and does not measure transcription quality. CI runs the faster unit suite without model downloads.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Gesture Recognizer model missing | Run `scripts/download_model.py` with the core interpreter |
| Audio subprocess cannot start | Create `.venv-transkun` in the repository root |
| Missing `2.0.conf` or `2.0.pt` | Check the pinned Transkun installation in the audio environment |
| `pkg_resources` import failure | Reinstall the declared setuptools version; keep environments separate |
| Input video cannot be read | Confirm the path, video codec, and readable audio/video streams |
| Key mapping is incorrect | Recalibrate after changing the camera, resolution, or keyboard |
| GUI/display failure | Use a desktop session for calibration and preview |
| Audio inference is slow | CPU inference and the second rendering pass are included in runtime; no real-time guarantee is made |

## Local files

The Git ignore rules keep recordings, recording-specific calibration, model files, virtual environments, and generated analysis out of version control. Selected documentation images belong in `assets/`. Do not use `git add -f` to bypass these rules for personal recordings or third-party weights.
