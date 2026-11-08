"""
File: piano_handtracking.py
Name: Juan Sanchez

Description:
PianoAnalyzerEx combines independent visual observations and audio transcription.
It saves MIDI and annotated video, with optional evidence CSV for review.
Transkun estimates note starts, durations, and velocity from piano audio.
The keyboard range is fixed at C3 through C7.

Hand tracking builds on Google's MediaPipe GestureRecognizer example and the
external CannyCam example (cannycam.cpp), adapted through an earlier prototype.
Keyboard mapping now uses manual corners and octave anchors.
The automatic line and contour checks from earlier versions were removed.

Sources:
Earlier development assistance from ChatGPT:
https://chatgpt.com/share/6ac48fa6-b19c-83e8-8288-d06208dc5931
Goes over adapting the starter code for piano hand tracking and removing
the finger counting and confusion matrix features, input, and saved output.

More recent conversation with ChatGPT to help build the earlier piano analyzer:
https://chatgpt.com/share/6acdb5d3-832c-83e8-b40c-f1add5a9f94b
Explained the code and helped me adapt it to my project.
Further assistance from ChatGPT was used for audio analysis, testing,
and simplifying this version.

https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer/python
https://github.com/googlesamples/mediapipe/tree/main/examples/gesture_recognizer/python

MediaPipe supplies landmarks; Transkun independently proposes audio notes.
The fusion module combines their evidence and marks uncertain notes for review.
Audio note endings and velocity are estimates, not measured physical releases.
Input videos are prepared at a constant frame rate.
"""
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from .piano_calibration import calibrate
from .piano_notes import write_midi
from .piano_press import observe_fingers
from .piano_transkun import transcribe_audio
from .piano_fusion import fuse_notes, save_evidence
from .piano_expression import describe_endings
from .piano_sound import extract_audio, add_audio
from .piano_video import render_video

def track_video(video, keyboard):
    # Track fingertips before drawing anything on the video
    model = Path(__file__).resolve().parents[2] / 'models' / 'gesture_recognizer.task'
    options = vision.GestureRecognizerOptions(
        base_options=python.BaseOptions(model_asset_path=str(model)),
        num_hands=2, running_mode=vision.RunningMode.VIDEO)
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        cap.release()
        raise ValueError('Input needs valid frame timing; use a prepared constant-frame-rate video')
    fingers, hand_results = [], []
    try:
        with vision.GestureRecognizer.create_from_options(options) as recognizer:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                # Frame number gives time for the prepared constant-FPS videos
                timestamp = round(len(hand_results) * 1000 / fps)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                result = recognizer.recognize_for_video(image, timestamp)
                fingers.append(observe_fingers(frame, result, keyboard, timestamp / 1000))
                # Keep landmarks, not full video frames, for the drawing pass.
                hand_results.append((timestamp / 1000, result))
    finally:
        cap.release()
    return fingers, hand_results, fps


def analyze_streams(video, audio, keyboard, sequential=False):
    """Gather independent evidence, then return it for fusion."""
    pitches = set(keyboard.keys)
    if sequential:
        fingers, hand_results, fps = track_video(video, keyboard)
        audio_notes = transcribe_audio(audio, pitches)
    else:
        # Each worker owns its model and input. Drawing stays on the main thread.
        with ThreadPoolExecutor(max_workers=2) as workers:
            video_job = workers.submit(track_video, video, keyboard)
            audio_job = workers.submit(transcribe_audio, audio, pitches)
            fingers, hand_results, fps = video_job.result()
            audio_notes = audio_job.result()
    return fingers, hand_results, fps, audio_notes


def main():
    # Read input options
    parser = argparse.ArgumentParser(
        description='Transcribe recorded piano video using audio and fingertip evidence.')
    parser.add_argument('--input', required=True, type=Path, help='Recorded video with piano audio')
    parser.add_argument('--output', required=True, type=Path, help='Output folder')
    parser.add_argument('--calibration', type=Path,
                        default=Path(__file__).resolve().parents[2] / 'calibration' / 'keyboard.json',
                        help='Keyboard calibration JSON; use --calibrate to create it')
    parser.add_argument('--calibrate', action='store_true', help='Replace saved octave calibration')
    parser.add_argument('--show', action='store_true', help='Preview rendering; Q closes preview')
    parser.add_argument('--save-evidence', action='store_true', help='Also save audio/video observations to CSV')
    parser.add_argument('--sequential', action='store_true', help='Run video and audio one at a time for speed comparisons')
    args = parser.parse_args()
    # Open selected input
    cap = cv2.VideoCapture(str(args.input))
    ok, first = cap.read()
    cap.release()
    if not ok:
        raise ValueError(f'Cannot read input video: {args.input}')
    # Load or select the keyboard map
    keyboard = calibrate(first, args.calibration, args.calibrate)
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    # Keep intermediate audio and video in a temporary folder
    with TemporaryDirectory() as temporary:
        work = Path(temporary)
        extract_audio(args.input, work / 'audio.wav')
        mode = 'sequentially' if args.sequential else 'in parallel'
        print(f'Tracking video and analyzing audio (Transkun) {mode}...', flush=True)
        fingers, hand_results, fps, audio_notes = analyze_streams(
            args.input, work / 'audio.wav', keyboard, args.sequential)
        notes = fuse_notes(audio_notes, fingers)
        notes = describe_endings(notes, fingers)
        write_midi(notes, args.output / 'performance.mid')
        if args.save_evidence:
            save_evidence(args.output / 'evidence.csv', notes)
        render_video(args.input, work, keyboard, notes, hand_results, fps, args.show)
        add_audio(work / 'annotated-silent.mp4', work / 'audio.wav', args.output / 'annotated.mp4')
    elapsed = time.perf_counter() - start
    frames = len(hand_results)
    # Print processing speed
    print(f'Detected notes: {len(notes)}')
    print(f'Audio + video: {sum(note["decision"] == "audio_and_video" for note in notes)}; '
          f'audio-only notes retained: {sum(note["decision"] == "audio_only" for note in notes)}')
    print(f'Notes needing review: {sum(note["needs_review"] for note in notes)}')
    print(f'Total runtime including video output: {elapsed:.2f}s ({frames / elapsed:.2f} FPS)')


if __name__ == '__main__':
    main()
