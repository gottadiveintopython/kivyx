PYTEST = python -m pytest
FLAKE8 = python -m flake8

test:
	env KCFG_GRAPHICS_MAXFPS=0 $(PYTEST) -m "not slow" ./tests

test_all:
	env KCFG_GRAPHICS_MAXFPS=0 $(PYTEST) ./tests

style:
	$(FLAKE8) --count --select=E9,F63,F7,F82 --show-source --statistics ./tests ./src ./examples

apidoc:
	sphinx-apidoc --separate -o ./sphinx ./src/kivyx

html:
	sphinx-build -M html ./sphinx ./docs
