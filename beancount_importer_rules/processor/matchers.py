import pathlib
import re

import arrow

from beancount_importer_rules.data_types import (
    DateAfterMatch,
    DateBeforeMatch,
    DateSameDayMatch,
    DateSameMonthMatch,
    DateSameYearMatch,
    SimpleFileMatch,
    SimpleTxnMatchRule,
    StrContainsMatch,
    StrExactMatch,
    StrMatch,
    StrOneOfMatch,
    StrPrefixMatch,
    StrRegexMatch,
    StrSuffixMatch,
    Transaction,
    TxnMatchVars,
)


def match_file(
    pattern: SimpleFileMatch, filepath: pathlib.Path | pathlib.PurePath
) -> bool:
    if isinstance(pattern, str):
        return filepath.match(pattern)
    if isinstance(pattern, StrRegexMatch):
        return re.match(pattern.regex, str(filepath)) is not None
    elif isinstance(pattern, StrExactMatch):
        return str(filepath) == pattern.equals
    else:
        raise ValueError(f"Unexpected file match type {type(pattern)}")


def match_str(pattern: StrMatch | None, value: str | None) -> bool:
    if value is None:
        return False

    if isinstance(pattern, str):
        return re.match(pattern, value) is not None
    elif isinstance(pattern, StrRegexMatch):
        return re.match(pattern.regex, value) is not None
    elif isinstance(pattern, StrExactMatch):
        return value == pattern.equals
    elif isinstance(pattern, StrPrefixMatch):
        return value.startswith(pattern.prefix)
    elif isinstance(pattern, StrSuffixMatch):
        return value.endswith(pattern.suffix)
    elif isinstance(pattern, StrContainsMatch):
        return pattern.contains in value
    elif isinstance(pattern, StrOneOfMatch):
        return value in pattern.one_of
    elif isinstance(pattern, DateAfterMatch):
        # is the value string a date and does the date occur after the date in the pattern
        try:
            value_as_date = arrow.get(value, pattern.format)
            match_date = arrow.get(pattern.date_after, pattern.format)
            return match_date < value_as_date
        except ValueError:
            return False

    elif isinstance(pattern, DateBeforeMatch):
        # is the value string a date and does the date occur before the date in the pattern
        try:
            value_as_date = arrow.get(value, pattern.format)
            match_date = arrow.get(pattern.date_before, pattern.format)
            return match_date > value_as_date
        except ValueError:
            return False

    elif isinstance(pattern, DateSameDayMatch):
        try:
            # reduce the value to the day only
            value_as_date = arrow.get(value, pattern.format).floor("day")
            match_date = arrow.get(pattern.date_same_day, pattern.format).floor("day")
            return value_as_date == match_date
        except ValueError:
            return False

    elif isinstance(pattern, DateSameMonthMatch):
        try:
            # reduce the value to the month only
            value_as_date = arrow.get(value, pattern.format).floor("month")
            match_date = arrow.get(pattern.date_same_month, pattern.format).floor(
                "month"
            )
            # set the day to 1 to compare only the month
            return value_as_date == match_date
        except ValueError:
            return False

    elif isinstance(pattern, DateSameYearMatch):
        try:
            # reduce the value to the year only
            value_as_date = arrow.get(value, pattern.format).floor("year")
            match_date = arrow.get(pattern.date_same_year, pattern.format).floor("year")
            # set the day and month to 1 to compare only the year
            return value_as_date == match_date
        except ValueError:
            return False
    else:
        raise ValueError(f"Unexpected str match type {type(pattern)}")


def match_transaction(
    txn: Transaction,
    rule: SimpleTxnMatchRule,
) -> bool:
    items = rule.model_dump().keys()
    for key in items:
        pattern = getattr(rule, key)
        if pattern is None:
            continue
        value = getattr(txn, key)

        if not match_str(pattern, value):
            return False

    return True


def match_transaction_with_vars(
    txn: Transaction,
    rules: list[TxnMatchVars],
    common_condition: SimpleTxnMatchRule | None = None,
) -> TxnMatchVars | None:
    for rule in rules:
        if match_transaction(txn, rule.cond) and (
            common_condition is None or match_transaction(txn, common_condition)
        ):
            return rule
