"""Check the isolated model interface without loading its weights."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import pretty_midi

from piano_transkun import transcribe_audio


class TranskunTests(unittest.TestCase):
    def test_range_filter_preserves_the_estimated_velocity_and_ending(self):
        def model_output(command, check):
            midi = pretty_midi.PrettyMIDI()
            track = pretty_midi.Instrument(0)
            track.notes = [pretty_midi.Note(45, 60, 1., 2.), pretty_midi.Note(80, 40, 1., 3.)]
            midi.instruments.append(track)
            midi.write(command[command.index('--output')+1])

        with TemporaryDirectory() as folder, patch('piano_transkun.subprocess.run', side_effect=model_output):
            notes = transcribe_audio(Path(folder) / 'audio.wav', {60})
        self.assertEqual(len(notes), 1)
        self.assertEqual((notes[0]['midi_pitch'], notes[0]['velocity'], notes[0]['end_seconds']), (60, 45, 2.))
        self.assertEqual(notes[0]['audio_source'], 'transkun')

    def test_model_failure_is_reported_instead_of_loading_stale_midi(self):
        with TemporaryDirectory() as folder, patch('piano_transkun.subprocess.run',
                side_effect=subprocess.CalledProcessError(1, 'model')):
            with self.assertRaises(subprocess.CalledProcessError):
                transcribe_audio(Path(folder) / 'audio.wav', {60})


if __name__ == '__main__':
    unittest.main()
