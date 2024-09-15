import pathlib

from beancount_importer_rules.data_types import (
    SimpleTxnMatchRule,
    StrMatch,
    StrRegexMatch,
    Transaction,
    TxnMatchVars,
)


def match_file(pattern: StrMatch, filepath: pathlib.Path | pathlib.PurePath) -> bool:
    if isinstance(pattern, str):
        return filepath.match(pattern)

    return pattern.test(str(filepath))


def match_str(pattern: StrMatch | None, value: str | None) -> bool:
    if value is None:
        return False

    if pattern is None:
        return True

    if isinstance(pattern, str):
        pattern = StrRegexMatch(regex=pattern)

    return pattern.test(value)


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
