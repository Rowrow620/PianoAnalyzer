"""
File: piano_notes.py
Name: Juan S

Description:
Saves fused note events using their audio-estimated durations and velocities.
These are estimates rather than measured key releases or physical strike strength.

Sources:
The pretty_midi example shows how to create notes and save a MIDI file:
https://craffel.github.io/pretty-midi/
Standard MIDI Files format:
https://midi.org/standard-midi-files-specification
"""
import pretty_midi


def write_midi(notes, path):
    # Add the notes to a piano track
    midi = pretty_midi.PrettyMIDI(resolution=480, initial_tempo=120)
    piano = pretty_midi.Instrument(program=0)
    for note in notes:
        piano.notes.append(pretty_midi.Note(
            velocity=note['velocity'], pitch=note['midi_pitch'],
            start=note['start_seconds'], end=note['end_seconds']))
    midi.instruments.append(piano)
    midi.write(str(path))
