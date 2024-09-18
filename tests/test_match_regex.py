import arrow
import pytest

from beancount_importer_rules.data_types import StrRegexMatch
from beancount_importer_rules.processor.matchers import (
    match_str,
)

now = arrow.utcnow()


@pytest.mark.parametrize(
    "pattern, value, expected",
    [
        (
            r"2021-01-01",
            r"2021-01-01",
            True,
        ),
        (
            r"2021-01-01",
            r"2021-01-02",
            False,
        ),
        (
            r"2021-01-01",
            None,
            False,
        ),
        (
            r"2021-01-01",
            now.format("YYYY-MM-DD"),
            False,
        ),
        (
            r"2021-01-01",
            "2021-01-01",
            True,
        ),
        (
            r"2021-01-01",
            "2021-01-02",
            False,
        ),
        (
            r"2021-01-.*",
            "2021-01-02",
            True,
        ),
        (
            "2021",
            "2021-01-02",
            True,
        ),
    ],
)
def test_match_regex(
    pattern: str | StrRegexMatch,
    value: str | None,
    expected: bool,
):
    outcome = match_str(pattern, value) == expected
    assert outcome
