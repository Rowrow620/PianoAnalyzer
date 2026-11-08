import unittest

from piano_analyzer.piano_evaluate import score_onsets


class EvaluationTests(unittest.TestCase):
    def test_duplicate_predictions_cannot_match_one_reference_twice(self):
        result = score_onsets([(60, 1.)], [(60, .99), (60, 1.01)])
        self.assertEqual((result['TP'], result['FP'], result['FN']), (1, 1, 0))

    def test_wrong_pitch_is_an_extra_and_a_miss(self):
        result = score_onsets([(60, 1.)], [(61, 1.)])
        self.assertEqual((result['TP'], result['FP'], result['FN']), (0, 1, 1))

    def test_matching_reassigns_a_note_to_recover_both_valid_events(self):
        result = score_onsets([(60, 1.), (60, 1.15)], [(60, 1.07), (60, .95)])
        self.assertEqual((result['TP'], result['FP'], result['FN']), (2, 0, 0))
