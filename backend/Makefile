.PHONY: run test lint format fuzz

run:
	uvicorn app.main:app --reload

test:
	pytest --cov=app --cov-report=term-missing

lint:
	flake8 app/ tests/

format:
	black app/ tests/
	isort app/ tests/

fuzz:
	pytest tests/test_fuzz.py -v
