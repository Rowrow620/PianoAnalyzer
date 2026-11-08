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

from piano_keyboard import drawing_scale, note_name
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
    scale = drawing_scale(frame)
    for hand in result.hand_landmarks:
        points = [(int(point.x * width), int(point.y * height)) for point in hand]
        for a, b in CONNECTIONS:
            cv2.line(frame, points[a], points[b], (0, 230, 0), max(1, round(2 * scale)), cv2.LINE_AA)
        for tip in TIPS:
            cv2.circle(frame, points[tip], max(2, round(4 * scale)), (0, 220, 255), -1, cv2.LINE_AA)


def draw_note_summary(frame, active, uncertain):
    scale = drawing_scale(frame)
    margin, padding = round(16 * scale), round(10 * scale)
    thickness = max(1, round(2 * scale))
    label = 'Notes: ' + ', '.join(note_name(note) + ('?' if note in uncertain else '')
                                 for note in sorted(active)) if active else 'No detected note'
    font_scale = .9 * scale
    (width, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    available = frame.shape[1] - 2 * (margin + padding)
    font_scale *= min(1., available / max(width, 1))
    (width, height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    legend_scale = .45 * scale
    legend = '? Needs visual review' if uncertain else ''
    (legend_width, legend_height), legend_baseline = cv2.getTextSize(
        legend, cv2.FONT_HERSHEY_SIMPLEX, legend_scale, max(1, round(scale)))
    panel_width = min(frame.shape[1] - margin, max(width, legend_width) + 2 * padding)
    panel_height = height + baseline + 2 * padding
    if legend:
        panel_height += legend_height + legend_baseline + padding
    region = frame[margin:margin + panel_height, margin:margin + panel_width]
    region[:] = cv2.convertScaleAbs(region, alpha=.25)
    position = (margin + padding, margin + padding + height)
    cv2.putText(frame, label, position, cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (245, 245, 245), thickness, cv2.LINE_AA)
    if legend:
        cv2.putText(frame, legend, (position[0], position[1] + baseline + padding + legend_height),
                    cv2.FONT_HERSHEY_SIMPLEX, legend_scale, (0, 190, 255),
                    max(1, round(scale)), cv2.LINE_AA)


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
            draw_note_summary(frame, active, uncertain)
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
