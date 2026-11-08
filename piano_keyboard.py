"""
File: piano_keyboard.py
Name: Juan S.
Description:
Maps a manually calibrated piano range to white and black keys.
The range is C3 through C7, including all 49 keys

Uses four keyboard corners and manually selected C key centers
White keys are spaced between the C keys, with black keys placed between them.
"""
import cv2
import numpy as np

WIDTH, HEIGHT = 1160, 400
BLACK_NOTES = {1, 3, 6, 8, 10}
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def note_name(note):
    return f"{NOTE_NAMES[note % 12]}{note // 12 - 1}"


class KeyboardMap:
    def __init__(self, corners, octave_anchors=None):
        # Warp keyboard perspective
        source = np.float32(corners)
        destination = np.float32([[0, 0], [WIDTH - 1, 0],
                                  [WIDTH - 1, HEIGHT], [0, HEIGHT]])
        self.transform = cv2.getPerspectiveTransform(source, destination)
        self.inverse = cv2.getPerspectiveTransform(destination, source)
        whites = [note for note in range(48, 97)
                  if note % 12 not in BLACK_NOTES]
        if octave_anchors is None:
            # Show evenly spaced keys until the octave anchors are selected
            boundaries = np.linspace(0, WIDTH, len(whites) + 1)
        else:
            boundaries = self.octave_boundaries(octave_anchors, len(whites))
        self.keys = {}
        # Map white keys
        for index, note in enumerate(whites):
            self.add_key(note, boundaries[index], boundaries[index + 1], HEIGHT)
        # Map black keys
        for note in range(48, 97):
            if note % 12 in BLACK_NOTES:
                index = sum(white < note for white in whites)
                center = boundaries[index]
                key_spacing = (boundaries[index + 1] - boundaries[index - 1]) / 2
                self.add_key(note, center - key_spacing * 0.31,
                             center + key_spacing * 0.31, HEIGHT * 0.63)

    def add_key(self, note, left, right, bottom):
        # Keep each key's rectangle and drawing positions together
        corners = np.float32([[left, 0], [right, 0],
                              [right, bottom], [left, bottom]]).reshape(-1, 1, 2)
        polygon = cv2.perspectiveTransform(corners, self.inverse)
        position = np.float32([[(left + right) / 2, bottom - 20]]).reshape(-1, 1, 2)
        label = cv2.perspectiveTransform(position, self.inverse)[0, 0].astype(int)
        self.keys[note] = {"black": note % 12 in BLACK_NOTES,
                           "rect": (left, 0, right, bottom),
                           "polygon": np.rint(polygon).astype(np.int32),
                           "label": tuple(label)}

    def octave_boundaries(self, anchors, count):
        # C-key centers occur every seven white keys. Keep the outer corners fixed.
        centers = self.to_keyboard(anchors)[:, 0]
        positions = [0] + [index * 7 + .5 for index in range(len(centers))] + [count]
        return np.interp(range(count + 1), positions, [0] + list(centers) + [WIDTH])

    def to_keyboard(self, points):
        points = np.float32(points).reshape(-1, 1, 2)
        return cv2.perspectiveTransform(points, self.transform).reshape(-1, 2)

    def key_at(self, x, y):
        # Prefer black keys
        for note in reversed(self.keys):
            left, top, right, bottom = self.keys[note]["rect"]
            if left <= x < right and top <= y < bottom:
                return note
        return None

    def draw(self, frame, active_notes=(), uncertain_notes=()):
        # Draw calibrated keys
        for note, key in self.keys.items():
            if note in uncertain_notes:
                color = (0, 165, 255)
            elif note in active_notes:
                color = (0, 230, 0)
            elif key["black"]:
                color = (255, 170, 0)
            else:
                color = (90, 90, 90)
            cv2.polylines(frame, [key["polygon"]], True, color, 1)
            if not key["black"] or note in active_notes:
                cv2.putText(frame, note_name(note), key["label"],
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.3, color, 1, cv2.LINE_AA)
