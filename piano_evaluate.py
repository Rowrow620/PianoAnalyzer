"""Repeatable pitch/onset evaluation. Releases and velocity are not scored.

Uses one-to-one maximum matching, as in the original experimental evaluator.
"""
import argparse
from pathlib import Path

import pretty_midi


def read_notes(path):
    midi = pretty_midi.PrettyMIDI(str(path))
    return sorted((note.pitch, note.start) for track in midi.instruments for note in track.notes)


def score_onsets(reference, predicted, tolerance=.1):
    matches = {}

    def match(index, seen):
        choices = sorted((abs(predicted[index][1] - note[1]), j)
                         for j, note in enumerate(reference)
                         if predicted[index][0] == note[0] and abs(predicted[index][1] - note[1]) <= tolerance)
        for _, j in choices:
            if j in seen:
                continue
            seen.add(j)
            if j not in matches or match(matches[j], seen):
                matches[j] = index
                return True
        return False

    for index in range(len(predicted)):
        match(index, set())
    tp = len(matches)
    fp, fn = len(predicted) - tp, len(reference) - tp
    precision = tp / len(predicted) if predicted else 0.
    recall = tp / len(reference) if reference else 0.
    return dict(TP=tp, FP=fp, FN=fn, precision=precision, recall=recall,
                F1=2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 0.)


def print_score(label, score):
    print(f"{label}: TP {score['TP']}, FP {score['FP']}, FN {score['FN']}; "
          f"precision {score['precision']:.1%}, recall {score['recall']:.1%}, F1 {score['F1']:.1%}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--tolerance', type=float, default=.1)
    args = parser.parse_args()
    reference = read_notes(args.reference)
    print_score('Fused MIDI', score_onsets(reference, read_notes(args.results / 'performance.mid'), args.tolerance))
    print(f'Exact pitch, +/-{args.tolerance:.3f}s onset tolerance, one match per note; no alignment adjustment.')


if __name__ == '__main__':
    main()
