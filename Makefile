.PHONY: install test run help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make run        - Run the agent interactively"

install:
	uv sync

test:
	uv run pytest tests/ -v

run:
	uv run python -c "from src.agent.agent import run_agent; print(run_agent(input('Enter your message: ')))"
