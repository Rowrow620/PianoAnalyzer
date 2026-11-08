# Calibration example

`keyboard.example.json` is a synthetic illustration of the calibration file format. It describes a rectangular keyboard in a hypothetical 1200 by 400 pixel image. It is not derived from a personal recording and is not a working calibration for your camera.

The `corners` order is C3 back-left, C7 back-right, C7 front-right, and C3 front-left. `octave_anchors` contains the five C-key centers from C3 through C7 in the original image coordinates. `start_note` is retained for compatibility with saved files; the current mapper fixes its range at C3-C7.

Use `--calibrate` on your own recording to create `calibration/performance/keyboard.json`. Recording-specific files in `calibration/` remain local.
