#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

isort --profile black . --skip-gitignore
black .
# sqlfluff fix --show-lint-violations --verbose sql/*.sql --dialect postgres
mypy --strict *.py services/*.py & pylint *.py services/*.py
