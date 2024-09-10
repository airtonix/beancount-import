export PATH := ".venv/bin:" + env_var('PATH')

default:
    @just --list

setup:
    @echo ""
    @echo "🍜 Setting up project"
    @echo ""

    pdm install

    @echo ""
    @echo "👍 Done"
    @echo ""

types:
    echo "Checking types..."

    pdm run pyright ./beancount_importer_rules

    @echo ""
    @echo "👍 Done"
    @echo ""


lint:
    echo "Linting files..."

    pdm run ruff check

    @echo ""
    @echo "👍 Done"
    @echo ""

test:
    echo "Testing files..."

    # Run python tests
    pdm run pytest --verbosity=0

    # find all .bats files in the repo and run them
    find . -type f -name "*.bats" -exec bats {} \;

    @echo ""
    @echo "👍 Done"
    @echo ""

citest REPORT_OUTPUT="/dev/tty":
    echo "Running tests..."

    pdm run pytest -v \
        --md-report \
        --md-report-flavor gfm \
        --md-report-exclude-outcomes passed skipped xpassed \
        --md-report-output "{{REPORT_OUTPUT}}"

    @echo ""
    @echo "👍 Done"
    @echo ""

unittest:
    echo "Running unit tests..."

    pdm run pytest

    @echo ""
    @echo "👍 Done"
    @echo ""

integrationtest:
    echo "Running integration tests..."

    pdm run beancount-import import \
        -w tests/fixtures/engine \
        -b books/main.bean \
        -c import.yaml

    @echo ""
    @echo "👍 Done"
    @echo ""

build:
    echo "Building project..."

    pdm build

    @echo ""
    @echo "👍 Done"
    @echo ""

secrets:
    echo "Checking for secrets..."

    pdm run detect-secrets scan \
        --baseline \
        --exclude-files ".secrets.baseline" \
        --exclude-files ".venv/.*" > .secrets.baseline

    @echo ""
    @echo "👍 Done"
    @echo ""

docs:
    echo "Generating documentation..."

    pdm run mkdocs build

    @echo ""
    @echo "👍 Done"
    @echo ""

docs-serve:
    echo "Serving documentation..."

    pdm run mkdocs serve

    @echo ""
    @echo "👍 Done"
    @echo ""

docs-deploy VERSION="" ALIAS="latest":
    echo "Deploying documentation..."

    pdm run mike deploy \
        --push \
        --update-aliases \
         --allow-empty \
        {{ VERSION }} \
        {{ ALIAS }}

    pdm run mike set-default latest

    @echo ""
    @echo "👍 Done"
    @echo ""

docs-deploy-local ALIAS="dev":
    #!/bin/bash

    echo "Deploying documentation locally..."

    commits_since_last_tag=$(git log $(git describe --tags --abbrev=0)..HEAD --oneline | wc -l)
    # strip v from tag
    last_tag=$(git describe --tags --abbrev=0 | sed 's/v//')

    version="${last_tag}.${commits_since_last_tag}"

    echo "Version: ${version}"

    just docs-deploy \
        "${version}" \
        {{ ALIAS }}

    echo ""
    echo "👍 Done"
    echo ""

publish ENV="testpypi":
    echo "Publishing package..."

    pdm publish --repository {{ENV}}

    @echo ""
    @echo "👍 Done"
    @echo ""

local-publish ENV="testpypi":
    echo "Locally Publishing package..."

    gopass env "websites/{{ENV}}/pdm" \
        sh -c "pdm publish --repository {{ENV}}"

    @echo ""
    @echo "👍 Done"
    @echo ""

schema:
    echo "Generating schema..."

    pdm run beancount-import schema

    @echo ""
    @echo "👍 Done"
    @echo ""
