import pathlib

import pytest

from beancount_importer_rules.data_types import (
    SimpleFileMatch,
    StrExactMatch,
    StrRegexMatch,
)
from beancount_importer_rules.processor.matchers import (
    match_file,
)


@pytest.mark.parametrize(
    "pattern, path, expected",
    [
        ("/path/to/*/foo*.csv", "/path/to/bar/foo.csv", True),
        ("/path/to/*/foo*.csv", "/path/to/bar/foo-1234.csv", True),
        ("/path/to/*/foo*.csv", "/path/to/eggs/foo-1234.csv", True),
        ("/path/to/*/foo*.csv", "/path/to/eggs/foo.csv", True),
        ("/path/to/*/foo*.csv", "/path/from/eggs/foo.csv", False),
        ("/path/to/*/foo*.csv", "foo.csv", False),
        (StrRegexMatch(regex=r"^/path/to/([0-9]+)"), "/path/to/0", True),
        (StrRegexMatch(regex=r"^/path/to/([0-9]+)"), "/path/to/0123", True),
        (StrRegexMatch(regex=r"^/path/to/([0-9]+)"), "/path/to/a0123", False),
        (StrExactMatch(equals="foo.csv"), "foo.csv", True),
        (StrExactMatch(equals="foo.csv"), "xfoo.csv", False),
    ],
)
def test_match_file(pattern: SimpleFileMatch, path: str, expected: bool):
    assert match_file(pattern, pathlib.PurePosixPath(path)) == expected
