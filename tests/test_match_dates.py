import arrow
import pytest

from beancount_importer_rules.data_types import (
    DateAfterMatch,
    DateBeforeMatch,
    DateSameDayMatch,
    DateSameMonthMatch,
    DateSameYearMatch,
)
from beancount_importer_rules.processor.matchers import (
    match_str,
)

now = arrow.utcnow()


@pytest.mark.parametrize(
    "pattern, value, expected",
    [
        (
            DateBeforeMatch(date_before=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=-1).format("YYYY-MM-DD"),
            True,
        ),
        (
            DateBeforeMatch(date_before=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=-10).format("YYYY-MM-DD"),
            True,
        ),
        (
            DateBeforeMatch(date_before=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=1).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateBeforeMatch(date_before=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=10).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateAfterMatch(date_after=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=10).format("YYYY-MM-DD"),
            True,
        ),
        (
            DateAfterMatch(date_after=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=1).format("YYYY-MM-DD"),
            True,
        ),
        (
            DateAfterMatch(date_after=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=-1).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateAfterMatch(date_after=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"),
            now.shift(days=-10).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateSameDayMatch(
                date_same_day=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"
            ),
            now.shift(days=-10).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateSameDayMatch(
                date_same_day=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"
            ),
            now.format("YYYY-MM-DD"),
            True,
        ),
        (
            DateSameMonthMatch(
                date_same_month=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"
            ),
            now.shift(months=-1).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateSameMonthMatch(
                date_same_month=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"
            ),
            now.format("YYYY-MM-DD"),
            True,
        ),
        (
            DateSameYearMatch(
                date_same_year=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"
            ),
            now.shift(years=-1).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateSameYearMatch(
                date_same_year=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"
            ),
            now.shift(years=1).format("YYYY-MM-DD"),
            False,
        ),
        (
            DateSameYearMatch(
                date_same_year=now.format("YYYY-MM-DD"), format="YYYY-MM-DD"
            ),
            now.format("YYYY-MM-DD"),
            True,
        ),
    ],
)
def test_match_dates(
    pattern: str
    | DateAfterMatch
    | DateBeforeMatch
    | DateSameDayMatch
    | DateSameMonthMatch
    | DateSameYearMatch,
    value: str | None,
    expected: bool,
):
    assert match_str(pattern, value) == expected
