init:
	git submodule update --init --recursive
	git submodule foreach git pull origin master
	pip install pipenv
	pipenv install --dev

style-check:
	pipenv run ruff format --check --config code-quality/python/ruff.toml ntripbrowser

lint:
	pipenv run ruff check --config code-quality/python/ruff.toml ntripbrowser

reformat:
	pipenv run ruff format --config code-quality/python/ruff.toml ntripbrowser
	pipenv run ruff check --fix --config code-quality/python/ruff.toml ntripbrowser

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
