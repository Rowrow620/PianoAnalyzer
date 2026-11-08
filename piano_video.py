"""
File: piano_video.py
Name: Juan Sanchez

Description:
Draws the keyboard, hand skeletons, and fingertip dots on the output video.
Uses the saved hand results so tracking only runs once.
Drawing code was moved from piano_handtracking.py.

Source:
https://developers.google.com/edge/mediapipe/solutions/vision/gesture_recognizer/python
"""
import cv2

from piano_keyboard import note_name
from piano_press import TIPS


# Hand landmark connections
CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14),
    (14, 15), (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]

# Adapted from earlier MediaPipe drawing code.
# Highlight only the fingertips used for mapping notes.
def annotate(frame, result):
    height, width = frame.shape[:2]
    for hand in result.hand_landmarks:
        points = [(int(point.x * width), int(point.y * height)) for point in hand]
        for a, b in CONNECTIONS:
            cv2.line(frame, points[a], points[b], (0, 230, 0), 2)
        for tip in TIPS:
            cv2.circle(frame, points[tip], 4, (0, 220, 255), -1)


def render_video(video, output, keyboard, notes, hand_results, fps, show):
    cap = cv2.VideoCapture(str(video))
    writer = None
    try:
        # Open the output video before drawing frames
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        writer = cv2.VideoWriter(str(output / 'annotated-silent.mp4'),
                                 cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
        if not writer.isOpened():
            raise RuntimeError('Cannot open the output video writer')
        for seconds, result in hand_results:
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError('Video ended before all tracked frames were drawn')
            active = {note['midi_pitch'] for note in notes
                      if note['start_seconds'] <= seconds < note['end_seconds']}
            uncertain = {note['midi_pitch'] for note in notes if note.get('needs_review')
                         and note['start_seconds'] <= seconds < note['end_seconds']}
            keyboard.draw(frame, active, uncertain)
            annotate(frame, result)
            label = ', '.join(note_name(note) + ('?' if note in uncertain else '')
                              for note in sorted(active)) or 'No detected note'
            cv2.putText(frame, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                        .5, (0, 220, 255), 1, cv2.LINE_AA)
            # Save processed output
            writer.write(frame)
            if show:
                cv2.imshow('Piano Analyzer', frame)
                key = cv2.waitKey(1) & 0xff
                if key in (27, ord('q')):
                    show = False
                    cv2.destroyAllWindows()
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()
