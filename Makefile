.PHONY: all test lint

all: lint test

test:
	python3 -m unittest discover tests

lint:
	pylint3 *.py tests/*.py
