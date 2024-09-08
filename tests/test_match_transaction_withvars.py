import pytest

from beancount_importer_rules.data_types import (
    SimpleTxnMatchRule,
    StrExactMatch,
    Transaction,
    TxnMatchVars,
)
from beancount_importer_rules.processor.matchers import match_transaction_with_vars


@pytest.mark.parametrize(
    "txn, rules, common_cond, expected",
    [
        (
            Transaction(extractor="MOCK_EXTRACTOR"),
            [
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
                ),
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(
                        extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                    ),
                    vars=dict(foo="bar"),
                ),
            ],
            None,
            TxnMatchVars(
                cond=SimpleTxnMatchRule(
                    extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                ),
                vars=dict(foo="bar"),
            ),
        ),
        (
            Transaction(extractor="MOCK_EXTRACTOR"),
            [
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
                    vars=dict(eggs="spam"),
                ),
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(
                        extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                    ),
                    vars=dict(foo="bar"),
                ),
            ],
            SimpleTxnMatchRule(payee=StrExactMatch(equals="PAYEE")),
            None,
        ),
        (
            Transaction(extractor="MOCK_EXTRACTOR", payee="PAYEE"),
            [
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
                    vars=dict(eggs="spam"),
                ),
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(
                        extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                    ),
                    vars=dict(foo="bar"),
                ),
            ],
            SimpleTxnMatchRule(payee=StrExactMatch(equals="PAYEE")),
            TxnMatchVars(
                cond=SimpleTxnMatchRule(
                    extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                ),
                vars=dict(foo="bar"),
            ),
        ),
        (
            Transaction(extractor="MOCK_EXTRACTOR"),
            [
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
                    vars=dict(eggs="spam"),
                ),
                TxnMatchVars(
                    cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="NOPE")),
                    vars=dict(foo="bar"),
                ),
            ],
            None,
            None,
        ),
    ],
)
def test_match_transaction_with_vars(
    txn: Transaction,
    rules: list[TxnMatchVars],
    common_cond: SimpleTxnMatchRule | None,
    expected: TxnMatchVars,
):
    assert (
        match_transaction_with_vars(txn, rules, common_condition=common_cond)
        == expected
    )
