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
	@find . -type d -name ".tmontmp" -delete
	@find . -type d -name ".pytest_cache" -delete
	@find . -type f -name ".testmondata" -delete

docker-build:
	@docker-compose build

docker-test:
	@docker-compose run test

test:
	@pytest --cov-report=html --cov-report=term --cov=stateman ./tests

lint:
	@flake8

test-watch:
	ptw -- --testmon
