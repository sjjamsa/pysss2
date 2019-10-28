SOURCES=pysss2/__init__.py

distfiles : setup.py $(SOURCES)
	python3 setup.py sdist bdist_wheel

install : distfiles
	 # python3 setup.py install does not allow uninstalling automagically
	pip install .

testpypi: distfiles
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
