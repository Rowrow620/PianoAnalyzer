"""Check worker overlap, ordered outputs, and error propagation."""
from threading import Barrier
import unittest
from unittest.mock import patch

from piano_handtracking import analyze_streams


class ThreadingTests(unittest.TestCase):
    def test_independent_workers_overlap_and_keep_their_outputs(self):
        ready = Barrier(2, timeout=5)

        def video(*args):
            ready.wait()
            return ['fingers'], ['landmarks'], 30

        def audio(*args):
            ready.wait()
            return ['notes']

        with patch('piano_handtracking.track_video', side_effect=video), \
             patch('piano_handtracking.transcribe_audio', side_effect=audio):
            result = analyze_streams('video', 'audio', type('Keyboard', (), {'keys': {60: None}})())
        self.assertEqual(result, (['fingers'], ['landmarks'], 30, ['notes']))

    def test_sequential_mode_returns_the_same_outputs(self):
        keyboard = type('Keyboard', (), {'keys': {60: None}})()
        with patch('piano_handtracking.track_video', return_value=([], [], 30)), \
             patch('piano_handtracking.transcribe_audio', return_value=['notes']):
            parallel = analyze_streams('video', 'audio', keyboard)
            sequential = analyze_streams('video', 'audio', keyboard, sequential=True)
        self.assertEqual(parallel, sequential)

    def test_audio_failure_reaches_caller(self):
        keyboard = type('Keyboard', (), {'keys': {60: None}})()
        with patch('piano_handtracking.track_video', return_value=([], [], 30)), \
             patch('piano_handtracking.transcribe_audio', side_effect=RuntimeError('audio failed')):
            with self.assertRaisesRegex(RuntimeError, 'audio failed'):
                analyze_streams('video', 'audio', keyboard)


if __name__ == '__main__':
    unittest.main()
