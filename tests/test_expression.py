"""Visual presence at an ending must not change the model's note duration."""
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from piano_analyzer.piano_expression import describe_endings
from piano_analyzer.piano_fusion import fuse_notes, save_evidence


def note():
    return dict(midi_pitch=60, start_seconds=1., end_seconds=2., velocity=50,
                audio_source='transkun', end_source='transkun', velocity_source='transkun')


class ExpressionTests(unittest.TestCase):
    def test_missing_tracking_does_not_shorten_a_note(self):
        updated = describe_endings([note()], [dict(time=2., tips=[])])[0]
        self.assertEqual(updated['end_seconds'], 2.)
        self.assertEqual(updated['end_visual_state'], 'tracking_missing')

    def test_resting_finger_does_not_extend_a_note(self):
        frames = [dict(time=t, tips=[dict(candidates={60: 1.}, hand='Right', finger='thumb')])
                  for t in [1.98, 2.02, 3.]]
        updated = describe_endings([note()], frames)[0]
        self.assertEqual(updated['end_seconds'], 2.)
        self.assertEqual(updated['end_visual_state'], 'finger_over_key')

    def test_visible_hand_elsewhere_is_not_missing_tracking(self):
        frames = [dict(time=2., tips=[dict(candidates={64: 1.}, hand='Right', finger='thumb')])]
        updated = describe_endings([note()], frames)[0]
        self.assertEqual(updated['end_visual_state'], 'hand_visible')

    def test_description_preserves_the_model_output(self):
        original = note()
        updated = describe_endings([original], [])[0]
        self.assertEqual((updated['start_seconds'], updated['end_seconds'], updated['velocity']), (1., 2., 50))
        self.assertNotIn('end_visual_state', original)

    def test_evidence_contains_the_sources_and_visual_observations(self):
        notes = describe_endings(fuse_notes([note()], []), [])
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'evidence.csv'
            save_evidence(path, notes)
            with path.open() as file:
                row = next(csv.DictReader(file))
        self.assertEqual(row['velocity_source'], 'transkun')
        self.assertEqual(row['end_visual_state'], 'tracking_missing')


if __name__ == '__main__':
    unittest.main()
