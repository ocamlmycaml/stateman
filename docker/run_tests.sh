#!/usr/bin/env bash

echo "Running pytest..."
pytest --cov-report html --cov=stateman ./tests

echo "Running flake8..."
flake8
