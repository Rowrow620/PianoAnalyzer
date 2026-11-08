"""Visual evidence only. Fingertip proximity is not proof of a physical
key press or release. This module never reads audio.
"""
from .piano_keyboard import HEIGHT

TIPS = {4: 'thumb', 8: 'index', 12: 'middle', 16: 'ring', 20: 'pinky'}


def nearby_keys(keyboard, x, y):
    primary = keyboard.key_at(x, y)
    candidates = {}
    for pitch, key in keyboard.keys.items():
        left, top, right, bottom = key['rect']
        dx = max(left - x, 0, x - right)
        dy = max(top - y, 0, y - bottom)
        margin = (right - left) * .18
        if dx <= margin and dy <= HEIGHT * .03:
            candidates[pitch] = 1.0 if pitch == primary else .35 * (1 - dx / margin)
    return candidates


def observe_fingers(frame, result, keyboard, seconds):
    height, width = frame.shape[:2]
    tips = []
    for index, hand in enumerate(result.hand_landmarks):
        side = result.handedness[index][0].category_name
        points = [(hand[tip].x * width, hand[tip].y * height) for tip in TIPS]
        for tip, (x, y) in zip(TIPS, keyboard.to_keyboard(points)):
            tips.append(dict(hand=side, finger=TIPS[tip],
                             candidates=nearby_keys(keyboard, float(x), float(y))))
    return dict(time=seconds, tips=tips)


def support_at(frames, pitch, seconds, radius=.12):
    """Count separate frames, not several fingers in the same frame."""
    nearby = [frame for frame in frames if abs(frame['time'] - seconds) <= radius]
    supported = []
    for frame in nearby:
        matches = [tip for tip in frame['tips'] if tip['candidates'].get(pitch, 0) > 0]
        if matches:
            tip = max(matches, key=lambda item: item['candidates'][pitch])
            supported.append((tip['candidates'][pitch], tip))
    supported.sort(key=lambda item: item[0], reverse=True)
    score = sum(item[0] for item in supported[:2]) / 2
    best = supported[0][1] if len(supported) >= 2 and score >= .6 else None
    visible = any(frame['tips'] for frame in nearby)
    return dict(score=score, frames=len(supported),
                hand=best['hand'] if best else '', finger=best['finger'] if best else '',
                visibility='tracked_hands' if visible else 'tracking_missing')
