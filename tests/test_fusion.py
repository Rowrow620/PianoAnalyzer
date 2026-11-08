"""Behavior checks for audio/video agreement, hovering, and occlusion."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pretty_midi

from piano_analyzer.piano_fusion import fuse_notes
from piano_analyzer.piano_notes import write_midi


def sound(pitch=60, start=1., end=1.6, velocity=82):
    return dict(midi_pitch=pitch, start_seconds=start, end_seconds=end, velocity=velocity,
                audio_source='transkun', end_source='transkun', velocity_source='transkun')


def tip(pitch=60, weight=1.):
    return dict(candidates={pitch: weight}, hand='Right', finger='index')


def visible(pitch=60, weight=1.):
    return [dict(time=.98, tips=[tip(pitch, weight)]), dict(time=1.02, tips=[tip(pitch, weight)])]


class FusionTests(unittest.TestCase):
    def test_audible_note_survives_hand_occlusion_and_is_flagged(self):
        notes = fuse_notes([sound()], [dict(time=1., tips=[])])
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]['decision'], 'audio_only')
        self.assertTrue(notes[0]['needs_review'])

    def test_two_frames_can_assign_a_supporting_finger(self):
        note = fuse_notes([sound()], visible())[0]
        self.assertEqual(note['decision'], 'audio_and_video')
        self.assertEqual((note['hand'], note['finger']), ('Right', 'index'))
        self.assertFalse(note['needs_review'])

    def test_several_fingers_in_one_frame_are_not_two_frames_of_support(self):
        notes = fuse_notes([sound()], [dict(time=1., tips=[tip(), tip(), tip()])])
        self.assertEqual(notes[0]['decision'], 'audio_only')

    def test_neighbor_only_support_does_not_confirm_the_key(self):
        notes = fuse_notes([sound()], visible(weight=.35))
        self.assertEqual(notes[0]['decision'], 'audio_only')

    def test_hovering_without_an_audio_note_creates_no_midi_note(self):
        self.assertEqual(fuse_notes([], visible()), [])

    def test_chord_keeps_pitches_endings_and_velocities(self):
        source = [sound(pitch=pitch, velocity=velocity) for pitch, velocity in [(60, 48), (64, 82), (67, 110)]]
        notes = fuse_notes(source, [])
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'chord.mid'
            write_midi(notes, path)
            actual = pretty_midi.PrettyMIDI(str(path)).instruments[0].notes
        self.assertEqual([note.pitch for note in actual], [60, 64, 67])
        self.assertEqual([note.velocity for note in actual], [48, 82, 110])
        self.assertTrue(all(abs(note.end-1.6)<.003 for note in actual))

    def test_repeated_strikes_remain_separate_without_inventing_another_attack(self):
        notes = fuse_notes([sound(start=2., end=2.5), sound(start=1., end=1.5)], [])
        self.assertEqual([note['start_seconds'] for note in notes], [1., 2.])
        self.assertEqual(len(notes), 2)

    def test_fusion_does_not_mutate_the_model_output(self):
        source = sound()
        fuse_notes([source], visible())
        self.assertNotIn('decision', source)


if __name__ == '__main__':
    unittest.main()
