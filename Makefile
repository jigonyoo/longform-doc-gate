.PHONY: demo test clean
demo:
	@cd "$(CURDIR)" && PYTHONPATH=src python3 src/cli.py
test:
	@cd "$(CURDIR)" && PYTHONPATH=src python3 -m unittest discover -s tests -v
clean:
	@rm -rf out/* src/__pycache__ tests/__pycache__
