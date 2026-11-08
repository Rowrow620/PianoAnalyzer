"""Record visual observations near audio-estimated note endings.

Fingertip presence is not proof that a key is held. Missing tracking does
not force a note to end. Velocity and endings come from Transkun.
"""
from .piano_press import support_at


def describe_endings(notes, fingers):
    described = []
    for original in notes:
        note = dict(original)
        visual = support_at(fingers, note['midi_pitch'], note['end_seconds'])
        state = ('finger_over_key' if visual['score'] >= .6 else
                 'hand_visible' if visual['visibility'] == 'tracked_hands' else 'tracking_missing')
        note.update(end_visual_state=state, end_visual_score=visual['score'],
                    end_visual_frames=visual['frames'])
        described.append(note)
    return described
