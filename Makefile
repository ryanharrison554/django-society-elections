migrations:
	python src/makemigrations.py

build: migrations
	python setup.py build

install: migrations
	python setup.py install