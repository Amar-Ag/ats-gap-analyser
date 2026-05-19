.PHONY: install test run help merge label batch

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make run        - Run the Streamlit app"
	@echo "  make batch      - Run evaluation batch"
	@echo "  make merge      - Merge eval results"
	@echo "  make label      - Open labeling tool"

install:
	uv sync --all-extras

test:
	uv run pytest tests/ -v

run:
	uv run streamlit run src/app.py

batch:
	uv run python scripts/batch_run.py

merge:
	uv run python scripts/merge_results.py

label:
	uv run streamlit run scripts/label_results.py