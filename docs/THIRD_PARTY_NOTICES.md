# Third party notices

The root [MIT license](../LICENSE) covers original project contributions. Third-party software, models, examples, and datasets retain their own copyright and license terms. Dependencies and pretrained weights are obtained separately; they are not vendored into this repository.

## Transkun

[Transkun](https://github.com/Yujia-Yan/Transkun), by Yujia Yan and collaborators, supplies the audio transcription model. The upstream project is distributed under the [MIT license](https://github.com/Yujia-Yan/Transkun/blob/main/LICENSE), copyright 2021 Yujia Yan. This project uses its packaged pretrained V2 resources and does not claim authorship or training of that model.

Relevant publications:

- Yujia Yan and Zhiyao Duan. *Scoring Time Intervals Using Non-Hierarchical Transformer for Automatic Piano Transcription*. ISMIR, 2024. [Paper](https://arxiv.org/abs/2404.09466).
- Yujia Yan, Frank Cwitkowitz, and Zhiyao Duan. *Skipping the Frame-Level: Event-Based Piano Transcription With Neural Semi-CRFs*. NeurIPS, 2021. [Project reference](https://github.com/Yujia-Yan/Transkun#citation).

## MediaPipe and earlier examples

Google's [MediaPipe GestureRecognizer guide](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer/python) and [MediaPipe examples](https://github.com/googlesamples/mediapipe) informed hand tracking and landmark rendering. The GestureRecognizer model is downloaded from Google's model hosting and remains outside version control. Consult [MediaPipe's upstream license](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE) and the model documentation for the applicable terms.

The earlier hand-tracking prototype also drew on the external CannyCam example (`cannycam.cpp`). That example title is retained as provenance; its starter source file is not distributed in this checkout.

## Libraries and tools

| Dependency | Use | Upstream |
| --- | --- | --- |
| OpenCV | Video I/O, perspective mapping, and overlays | [Project and license](https://github.com/opencv/opencv) |
| NumPy | Coordinate and array operations | [Project and license](https://github.com/numpy/numpy) |
| PyTorch and torchaudio | Transkun inference environment | [PyTorch](https://github.com/pytorch/pytorch) |
| pretty_midi | MIDI reading and writing | [Project and license](https://github.com/craffel/pretty-midi) |
| imageio-ffmpeg and FFmpeg | Audio extraction and final video encoding | [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg), [FFmpeg legal information](https://ffmpeg.org/legal.html) |
| SciPy, soxr, moduleconf, and ncls | Transkun dependencies | Installed distributions carry their upstream notices |
| Shields.io | README badges and navigation images | [Shields](https://shields.io/) |

FFmpeg licensing depends on the downloaded binary's build configuration. The project does not redistribute an FFmpeg executable.

## Oxford MIDI test dataset

Earlier development used the Oxford MIDI test dataset associated with A. S. Koepke, O. Wiles, Y. Moses, and A. Zisserman, *Sight to sound: An end-to-end approach for visual piano transcription*, ICASSP 2020. [Dataset source](https://www.robots.ox.ac.uk/~vgg/research/sighttosound/).

The local dataset notice identifies Creative Commons Attribution 4.0 terms. Dataset recordings and MIDI files are not included in this repository. Obtain them from the original source and retain its notices if using them. Their use during development does not make them independent test data.

## Development assistance and recordings

ChatGPT assisted with calibration, audio processing, MIDI output, hand tracking, testing, and documentation. A pianist helped perform the original development recordings. Raw recordings, recording-specific calibration, and generated performance videos remain local. Selected annotated screenshots are included in `assets/examples/`.

The original report retains its diagrams, performance screenshots, and source acknowledgements. Its embedded images are part of the historical document; separate raw media are not bundled.
