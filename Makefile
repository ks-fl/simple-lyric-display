.PHONY: install test lint format run clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
SRC_DIR = src
TEST_DIR = tests

install:
	$(PIP) install PySide6 pytest ruff

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
