# Changelog

## 0.1.0

### Current implementation

- Uses Transkun audio note proposals and independent MediaPipe fingertip observations.
- Preserves audio-estimated note endings and velocity and flags notes without sufficient visual support.
- Supports parallel or sequential audio/video analysis and optional evidence CSV output.
- Includes 21 unit tests for evidence handling, evaluation, orchestration, and the audio subprocess interface.

### Repository packaging

- Adds installation, architecture, evaluation, and attribution documentation.
- Documents separate core and audio environments and adds model download/setup checks.
- Keeps raw recordings, private calibration, generated results, environments, and weights out of Git.
- Includes the public October 2026 report as historical documentation, distinct from the current implementation.

## Original implementation October 2026

The original evaluated system used librosa onsets and FFT confirmation with visual candidates. It used placeholder note durations and fixed MIDI velocity. See [the original report](reports/Piano_Analyzer_Public_Report.pdf) for its development measurements and limitations.
