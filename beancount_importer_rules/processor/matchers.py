import datetime
import pathlib
import re

from beancount_importer_rules.data_types import (
    SimpleTxnMatchRule,
    StrMatch,
    StrRegexMatch,
    Transaction,
    TxnMatchVars,
    stringify_value,
)


def is_valid_regex(pattern: str) -> bool:
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def match_file(pattern: StrMatch, filepath: pathlib.Path | pathlib.PurePath) -> bool:
    if isinstance(pattern, str):
        return filepath.match(pattern)

    return pattern.test(str(filepath))


def match_str(
    pattern: StrMatch, value: str | datetime.date | datetime.datetime | None
) -> bool:
    if value is None:
        return False

    # Most patterns that are just strings are valid regexes.
    if isinstance(pattern, str) and is_valid_regex(pattern):
        pattern = StrRegexMatch(regex=pattern)

    # if the pattern turns out to not be a regex, we can just compare the strings.
    if isinstance(pattern, str):
        return stringify_value(value) == pattern

    # otherwise we assume it's a complex matcher
    return pattern.test(stringify_value(value))


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
        matches_rule = match_transaction(txn, rule.cond)
        matches_common = (
            match_transaction(txn, common_condition) if common_condition else True
        )

        if matches_rule and matches_common:
            return rule
