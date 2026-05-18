.PHONY: install test run help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make run        - Run the Streamlit app"

install:
	uv sync --all-extras

test:
	uv run pytest tests/ -v

run:
	uv run streamlit run src/app.py