venv: venv/touchfile

venv/touchfile: requirements.txt
	python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt; pip install -Ur requirements-dev.txt
	touch venv/touchfile

test: venv
	. venv/bin/activate; python3 -m pytest .

black: venv
	. venv/bin/activate; python3 -m black -l 120 --check .

flake8: venv
	. venv/bin/activate; python3 -m flake8 --exclude=venv .

mypy: venv
	. venv/bin/activate; python3 -m mypy .