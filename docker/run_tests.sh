#!/usr/bin/env bash

set -e

eval "$(pyenv init -)"

pyenv activate stateman

pytest --cov=stateman ./tests

echo "Running flake8..."

flake8