.PHONY: test lint validate mock

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src/autonomy_evals

validate:
	uv run autonomy-evals validate

mock:
	uv run autonomy-evals run --config configs/experiment_mock.yaml --run-id mock-demo
	uv run autonomy-evals analyze --run mock-demo
	uv run autonomy-evals report --run mock-demo
