#!/usr/bin/env bats

debug() {
    echo "# ${*}" >&3
}

@test "doesn't explode on empty input" {
    run "$BATS_TEST_DIRNAME/get-release-version"
    [ "$status" -eq 0 ]
    [ "$output" = "" ]
}

@test "provides a dev version" {
    run "$BATS_TEST_DIRNAME/get-release-version" \
        '{"prs_created": true, "releases_created": false, "release_version": null}' \
        "$BATS_TEST_TMPDIR/output"

    [ "$status" -eq 0 ]
    [ -s "$BATS_TEST_TMPDIR/output" ]

    output="$(cat "$BATS_TEST_TMPDIR/output")"
    # each line is a key=value pair
    output_version=$(echo "$output" | grep '^Version=' | cut -d= -f2)
    debug "output_version: $output_version"

    output_track=$(echo "$output" | grep '^Track=' | cut -d= -f2)
    debug "output_track: $output_track"

    expected_git_tag=$(git describe --tags --abbrev=0)
    expected_commits=$(git rev-list --count "${expected_git_tag}..HEAD")
    expected_version="${expected_git_tag#v}.dev${expected_commits}"

    debug "expected_version: $expected_version"
    # test with grep that the output contains the expected version
    [ "$output_version" = "${expected_version}" ]
    [ "$output_track" = "dev" ]
}

@test "provides a stable version" {
    expected_version="1.2.3"
    run "$BATS_TEST_DIRNAME/get-release-version" \
        "{\"releases_created\": true, \"release_version\": \""${expected_version}\""}" \
        "$BATS_TEST_TMPDIR/output"

    [ "$status" -eq 0 ]
    [ -s "$BATS_TEST_TMPDIR/output" ]

    output="$(cat "$BATS_TEST_TMPDIR/output")"
    # each line is a key=value pair
    output_version=$(echo "$output" | grep '^Version=' | cut -d= -f2)
    debug "output_version: $output_version"

    output_track=$(echo "$output" | grep '^Track=' | cut -d= -f2)
    debug "output_track: $output_track"

    debug "expected_version: $expected_version"
    [ "${output_version}" = "${expected_version}" ]
    [ "${output_track}" = "stable" ]
}
