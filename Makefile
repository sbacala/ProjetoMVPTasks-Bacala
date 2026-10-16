VENV ?= .venv

ifeq ($(OS),Windows_NT)
PYTHON ?= py
VENV_PYTHON ?= $(VENV)/Scripts/python.exe
else
PYTHON ?= python3
VENV_PYTHON ?= $(VENV)/bin/python
endif

.PHONY: help install install-dev run test

help:
	@echo "Targets:"
	@echo "  install      Create the virtual environment and install runtime dependencies"
	@echo "  install-dev  Create the virtual environment and install development dependencies"
	@echo "  run          Start the FastAPI development server"
	@echo "  test         Run the pytest suite"

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)

install: $(VENV_PYTHON)
	$(VENV_PYTHON) -m pip install -r requirements.txt

install-dev: $(VENV_PYTHON)
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt

run: $(VENV_PYTHON)
	$(VENV_PYTHON) -m uvicorn app.main:app --reload

test: $(VENV_PYTHON)
	$(VENV_PYTHON) -m pytest
