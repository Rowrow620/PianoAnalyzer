# PianoAnalyzerEx
.DEFAULT_GOAL := run

ifeq ($(OS),Windows_NT)
PYTHON ?= .venv/Scripts/python.exe
else
PYTHON ?= .venv/bin/python
endif
INPUT ?= videos/c4_cmajor/c4_cmajor.MOV
CALIBRATION ?= calibration/c4_cmajor/keyboard.json
OUTPUT ?= results/c4_cmajor
REFERENCE ?= videos/c4_cmajor/c4_cmajor.mid
FLAGS ?=

SOURCES = $(wildcard src/piano_analyzer/*.py)

.PHONY: check test run evaluate
check:
	"$(PYTHON)" -m py_compile $(SOURCES)

run: check
	"$(PYTHON)" -m piano_analyzer --input "$(INPUT)" --calibration "$(CALIBRATION)" --output "$(OUTPUT)" $(FLAGS)

test:
	"$(PYTHON)" -m unittest discover -s tests

evaluate:
	"$(PYTHON)" -m piano_analyzer.piano_evaluate --results "$(OUTPUT)" --reference "$(REFERENCE)"
