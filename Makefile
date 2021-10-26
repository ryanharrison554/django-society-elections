migrations:
	python src/manage.py makemigrations society_elections

test:
	python src/manage.py test society_elections

build: migrations
	python setup.py build

install: migrations
	python setup.py install

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*