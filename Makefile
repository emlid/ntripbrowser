install:
	python setup.py install

package:
	python setup.py clean
	python setup.py sdist

test:
	pytest -v

clean:
	rm -rf build
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .tox
