"""Combine Transkun notes with fingertip evidence from video.

Audio supplies note events. Video identifies supporting fingers and marks
notes needing review. Missing hands do not veto an audible note.
"""
import csv

from piano_press import support_at


def fuse_notes(audio_notes, frames):
    notes = []
    for audio in sorted(audio_notes, key=lambda note: (note['start_seconds'], note['midi_pitch'])):
        note = dict(audio)
        visual = support_at(frames, note['midi_pitch'], note['start_seconds'])
        supported = visual['score'] >= .6
        note.update(visual_score=visual['score'], visual_frames=visual['frames'],
                    visibility=visual['visibility'], hand=visual['hand'], finger=visual['finger'],
                    decision='audio_and_video' if supported else 'audio_only', needs_review=not supported)
        notes.append(note)
    return notes


def save_evidence(path, notes):
    fields = ['midi_pitch', 'start_seconds', 'end_seconds', 'velocity', 'decision', 'needs_review',
              'audio_source', 'end_source', 'velocity_source', 'visual_score', 'visual_frames',
              'visibility', 'hand', 'finger', 'end_visual_state', 'end_visual_score', 'end_visual_frames']
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(notes)
