from beancount_importer_rules.data_types import (
    SimpleTxnMatchRule,
    StrExactMatch,
    Transaction,
    TxnMatchVars,
)
from beancount_importer_rules.processor.matchers import match_transaction_with_vars


def test_match_transaction_with_vars_empty():
    txn = Transaction(extractor="MOCK_EXTRACTOR")
    rules = [
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
        ),
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="MOCK_EXTRACTOR")),
            vars=dict(foo="bar"),
        ),
    ]

    common_cond = None
    expected = TxnMatchVars(
        cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="MOCK_EXTRACTOR")),
        vars=dict(foo="bar"),
    )

    outcome = match_transaction_with_vars(txn, rules, common_condition=common_cond)

    assert outcome == expected


def test_match_transaction_with_common_cond():
    txn = Transaction(extractor="MOCK_EXTRACTOR")
    rules = [
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
            vars=dict(eggs="spam"),
        ),
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="MOCK_EXTRACTOR")),
            vars=dict(foo="bar"),
        ),
    ]
    common_cond = SimpleTxnMatchRule(payee=StrExactMatch(equals="PAYEE"))
    expected = None
    outcome = match_transaction_with_vars(txn, rules, common_condition=common_cond)
    assert outcome == expected


def test_match_transaction_with_vars_common():
    txn = Transaction(extractor="MOCK_EXTRACTOR", payee="PAYEE")
    rules = [
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
            vars=dict(eggs="spam"),
        ),
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="MOCK_EXTRACTOR")),
            vars=dict(foo="bar"),
        ),
    ]

    common_cond = SimpleTxnMatchRule(payee=StrExactMatch(equals="PAYEE"))
    expected = TxnMatchVars(
        cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="MOCK_EXTRACTOR")),
        vars=dict(foo="bar"),
    )
    outcome = match_transaction_with_vars(txn, rules, common_condition=common_cond)
    assert outcome == expected


def test_match_transaction_with_vars():
    txn = Transaction(extractor="MOCK_EXTRACTOR")
    rules = [
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="OTHER")),
            vars=dict(eggs="spam"),
        ),
        TxnMatchVars(
            cond=SimpleTxnMatchRule(extractor=StrExactMatch(equals="NOPE")),
            vars=dict(foo="bar"),
        ),
    ]
    common_cond = None
    expected = None
    outcome = match_transaction_with_vars(txn, rules, common_condition=common_cond)

    assert outcome == expected
