.PHONY: install test lint format run clean build

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
SRC_DIR = src
TEST_DIR = tests

# Automatic venv creation and installation
$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)
	$(PIP) install PySide6 pytest ruff pyinstaller

test:
	$(PYTHON) -m pytest $(TEST_DIR)

lint:
	$(VENV)/bin/ruff check $(SRC_DIR)

format:
	$(VENV)/bin/ruff format $(SRC_DIR)

run:
	$(PYTHON) $(SRC_DIR)/main.py

build:
	$(VENV)/bin/pyinstaller --noconfirm --onefile --windowed \
		--name "simple-lyric-display" \
		--add-data "assets:assets" \
		--add-data "src:src" \
		--paths "src" \
		src/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.spec
