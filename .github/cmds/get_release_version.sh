#!/bin/sh

payload="${1}"
output="${2}"

prs_created=$(echo "${payload}" | jq -r '.prs_created')
releases_created=$(echo "${payload}" | jq -r '.releases_created')
release_version=$(echo "${payload}" | jq -r '.release_version')

if [ "${prs_created}" = "true" ]; then
    last_tag=$(git describe --tags --abbrev=0)
    hash=$(git rev-parse --short HEAD)
    commits_since_last_tag=$(git log "${last_tag}..HEAD" --oneline | wc -l)

    # https://packaging.python.org/en/latest/discussions/versioning/#local-version-identifiers
    # https://discuss.python.org/t/pip-pre-and-beta-dev-versions/9665
    # https://stackoverflow.com/a/24293364/454615
    echo "Version=${last_tag#v}.dev${commits_since_last_tag}+${hash}" >>"$output"
    echo "Track=dev" >>"$output"
fi

if [ "${releases_created}" = "true" ]; then
    echo "Version=${release_version}" >>"$output"
    echo "Track=stable" >>"$output"
fi
