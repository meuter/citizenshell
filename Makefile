SHELL := bash

devshell:
	docker-compose build
	docker-compose run --rm -ti devshell /bin/bash

test: test2 test3

env2: env2/bin/activate

env2/bin/activate: test/requirements.txt
	test -d env2 || python2 -m pip install virtualenv
	test -d env2 || python2 -m virtualenv env2
	source env2/bin/activate; \
		pip install -Ur test/requirements.txt; \
		pip install -e .;
	touch env2/bin/activate

test2: env2
	source env2/bin/activate; \
		pytest test --tb=short

env3: env3/bin/activate

env3/bin/activate: test/requirements.txt
	test -d env3 || python3 -m pip install virtualenv
	test -d env3 || python3 -m virtualenv env3
	source env3/bin/activate; \
		pip install -Ur test/requirements.txt; \
		pip install -e .;
	touch env3/bin/activate

test3: env3
	source env3/bin/activate; \
		pytest test --tb=short

clean:
	rm -rf env2 env3
	find -iname "*.pyc" -delete

dist: env3
	source env3/bin/activate; \
		python setup.py sdist

.PHONY: dist clean
