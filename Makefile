PYTHON=python

.DEFAULT: help
help:
	@echo "make clean"
	@echo "       Cleans all build and pyc files"
	@echo "make docker-build"
	@echo "       Build docker image"
	@echo "make docker-test"
	@echo "       Run all tests in docker"
	@echo "make test"
	@echo "       run tests"

clean:
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete

docker-build:
	@docker-compose build

docker-test:
	@docker-compose run test

test:
	@pytest tests