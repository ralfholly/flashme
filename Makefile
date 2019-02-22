.PHONY: all test lint

all: lint test

test:
	python3 -m unittest discover tests

lint:
	pylint *.py tests/*.py
