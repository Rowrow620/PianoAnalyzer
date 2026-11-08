# Evaluation

## Current implementation

The current implementation uses Transkun audio transcription and independent fingertip evidence. No held-out accuracy, throughput, release-timing, or velocity benchmark is published for this version.

The 21 unit tests exercise evaluation matching, evidence fusion, note-ending descriptions, parallel/sequential orchestration, and the Transkun subprocess interface. The model interface is mocked. Passing these tests is not an end-to-end transcription benchmark.

## Reproducing pitch and onset scoring

After processing a recording, compare its generated MIDI with a reference MIDI:

```powershell
.\.venv\Scripts\python.exe -m piano_analyzer.piano_evaluate --results "results/performance" --reference "videos/performance.mid" --tolerance 0.10
```

The evaluator requires the same pitch and an onset difference of at most the specified tolerance. It uses one-to-one maximum matching, so duplicate predictions cannot match the same reference note twice. A wrong pitch can count as both a false positive and a false negative.

| Metric | Definition |
| --- | --- |
| Precision | TP / (TP + FP) |
| Recall | TP / (TP + FN) |
| F1 | 2 TP / (2 TP + FP + FN) |

No automatic audio/MIDI alignment adjustment is applied. Verify the reference timing and scoring range before running the comparison. The analyzer filters to C3-C7, while a source MIDI may contain a wider range. Any restriction or alignment must be disclosed and reproducible; preserve the original reference.

The Oxford MIDI test recording used during earlier development has a preliminary alignment note in the local reference collection. It should not be treated as unseen data or scored without checking its timing and range. The media itself is not included here.

## Original implementation October 2026

The [public technical report](reports/Piano_Analyzer_Public_Report.pdf) and [editable DOCX](reports/Piano_Analyzer_Public_Report.docx) describe the original implementation. That version combined visual candidates with librosa onset detection and FFT confirmation, used placeholder note durations, and did not estimate dynamic velocity.

Seven recordings were used during development and tuning, so these are development results rather than independent held-out test results.

| Historical result | Reported value |
| --- | --- |
| True positives / false positives / false negatives | 229 / 32 / 43 |
| Reference notes | 272 |
| Precision | 87.74% |
| Recall | 84.19% |
| F1 | 85.93% |
| Aggregate frames | 3,436 |
| Aggregate processing time | 209.91 seconds |
| Aggregate throughput | 16.37 FPS |
| Recordings meeting the 15 FPS minimum | Six of seven |

The original 30 FPS goal was not achieved.

### Frame-count discrepancy

The original table contains six named recordings totaling 2,951 frames and a 492-frame value placed in its Combined row. If 492 is interpreted as the seventh recording's count, the individual values total 3,443 frames, seven more than the reported aggregate of 3,436. The recording identity and individual processing time/FPS for that entry are not established by the table. The aggregate count of six recordings meeting 15 FPS is not independently verifiable from the available individual rows.

The public report preserves the source value, corrects the aggregate as documented, and flags the discrepancy. No replacement individual measurements have been invented. The original benchmark records are needed to resolve it.

These historical measurements must not be presented as evaluation of the current Transkun implementation.

## Next evaluation

Use recording-level separation between development and unseen evaluation data. Record the code revision, environment versions, hardware, model/checkpoint, input frame count, reference provenance, and alignment procedure. Report audio-only and fused results under the same matching rules; this implementation preserves audio notes, so added visual evidence should be assessed for its review and attribution value rather than assumed to improve note accuracy.

Measure complete processing time and compare parallel and sequential modes on identical recordings. Release and velocity evaluation requires suitable ground truth and remains separate from the implemented onset evaluator.
