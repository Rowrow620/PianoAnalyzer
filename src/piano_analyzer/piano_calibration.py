"""
File: piano_calibration.py
Name: Juan Sanchez

Description:
Loads saved keyboard corners and octave anchors, or lets me select new ones.
The keyboard range is fixed at C3-C7 currently, though I could make it work for C2-C7 also
Moved from piano_handtracking.py to keep calibration in one place.
"""
import json

import cv2

from .piano_keyboard import KeyboardMap, note_name


def calibrate(frame, path, reset=False):
    # Load saved calibration
    if path.is_file():
        saved = json.loads(path.read_text())
        if not reset:
            return KeyboardMap(saved["corners"], octave_anchors=saved["octave_anchors"])

    # Select keyboard corners
    corners = []
    anchors = []
    anchor_notes = list(range(48, 97, 12))
    instructions = ("C3 back-left", "C7 back-right", "C7 front-right", "C3 front-left")
    window = "Keyboard calibration"
    keyboard = None

    def click(event, x, y, flags, parameter):
        nonlocal keyboard
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(corners) < 4:
                corners.append((x, y))
            elif len(anchors) < len(anchor_notes):
                anchors.append((x, y))
                if len(anchors) == len(anchor_notes):
                    keyboard = KeyboardMap(corners, octave_anchors=anchors)

    cv2.namedWindow(window)
    cv2.setMouseCallback(window, click)
    while True:
        preview = frame.copy()
        if len(corners) == 4:
            if keyboard is None:
                keyboard = KeyboardMap(corners)
            keyboard.draw(preview)
            if len(anchors) < len(anchor_notes):
                note = note_name(anchor_notes[len(anchors)])
                message = f"Click CENTER of {note} near front edge. U undoes; R resets; Q exits"
            else:
                message = "Check map. SPACE saves; U undoes last C; R resets; Q exits"
        else:
            message = f"Click {instructions[len(corners)]}. R resets; Q exits"
        for point in corners:
            cv2.circle(preview, point, 5, (0, 220, 255), -1)
        for point, note in zip(anchors, anchor_notes):
            cv2.circle(preview, point, 5, (0, 255, 0), -1)
            cv2.putText(preview, note_name(note), (point[0], point[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(preview, message, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 220, 255), 1, cv2.LINE_AA)
        cv2.imshow(window, preview)
        key = cv2.waitKey(20) & 0xff
        if key == ord("r"):
            corners.clear()
            anchors.clear()
            keyboard = None
        elif key == ord("u") and anchors:
            anchors.pop()
            keyboard = KeyboardMap(corners)
        elif key in (27, ord("q")):
            cv2.destroyWindow(window)
            raise SystemExit("Calibration cancelled")
        elif key == ord(" ") and len(anchors) == len(anchor_notes):
            break
    # Save reusable calibration
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"corners": corners, "start_note": 48,
                               "octave_anchors": anchors}, indent=2))
    cv2.destroyWindow(window)
    return keyboard
