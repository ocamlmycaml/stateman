#!/usr/bin/env bash

echo "Running pytest..."
pytest --cov-report html --cov-report term --cov=stateman ./tests

echo "Running flake8..."
flake8
