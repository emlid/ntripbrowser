init:
	git submodule update --init --recursive
	git submodule foreach git pull origin master
	pip install pipenv
	pipenv install --dev

style-check:
	pipenv run flake8 --config code-quality/python/flake8 ntripbrowser

lint:
	pipenv run pylint --rcfile code-quality/python/pylintrc ntripbrowser

test:
	pipenv run pytest tests

install:
	pipenv run pip install -e .

clean:
	rm -rf build
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .tox
