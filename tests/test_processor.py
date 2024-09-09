import datetime
import decimal
import pathlib
import typing

import pytest
from jinja2.sandbox import SandboxedEnvironment

from beancount_importer_rules.data_types import (
    ActionAddTxn,
    ActionDelTxn,
    ActionIgnore,
    ActionType,
    Amount,
    AmountTemplate,
    DeletedTransaction,
    DeleteTransactionTemplate,
    ExractorInputConfig,
    GeneratedPosting,
    GeneratedTransaction,
    ImportList,
    ImportRule,
    InputConfigDetails,
    MetadataItem,
    MetadataItemTemplate,
    PostingTemplate,
    SimpleTxnMatchRule,
    StrExactMatch,
    Transaction,
    TransactionTemplate,
    TxnMatchVars,
    UnprocessedTransaction,
)
from beancount_importer_rules.processor.process_transaction import (
    process_transaction,
)
from beancount_importer_rules.processor.walk_dir import walk_dir_files
from beancount_importer_rules.templates import make_environment


@pytest.fixture
def template_env() -> SandboxedEnvironment:
    return make_environment()


@pytest.mark.parametrize(
    "files, expected",
    [
        (
            {
                "a": {
                    "b": {
                        "1": "hey",
                        "2": {},
                    },
                    "c": "hi there",
                },
            },
            [
                "a/b/1",
                "a/c",
            ],
        )
    ],
)
def test_walk_dir_files(
    tmp_path: pathlib.Path,
    construct_files: typing.Callable,
    files: dict,
    expected: list[pathlib.Path],
):
    construct_files(tmp_path, files)
    assert frozenset(
        p.relative_to(tmp_path) for p in walk_dir_files(tmp_path)
    ) == frozenset(map(pathlib.Path, expected))


@pytest.mark.parametrize(
    "txn, input_config, import_rules, expected, expected_result",
    [
        pytest.param(
            Transaction(
                extractor="MOCK_EXTRACTOR",
                file="mock.csv",
                lineno=123,
                desc="MOCK_DESC",
                source_account="Foobar",
                date=datetime.date(2024, 5, 5),
                currency="BTC",
                amount=decimal.Decimal("123.45"),
            ),
            InputConfigDetails(
                extractor=ExractorInputConfig(
                    import_path="mock.extractor:SomeClassName",
                    as_name="extractor",
                    date_format="YYYY-MM-DD",
                    datetime_format="YYYY-MM-DD HH:mm:ss",
                ),
                prepend_postings=[
                    PostingTemplate(
                        account="Expenses:Food",
                        amount=AmountTemplate(
                            number="{{ -(amount - 5) }}",
                            currency="{{ currency }}",
                        ),
                    ),
                ],
                append_postings=[
                    PostingTemplate(
                        account="Expenses:Fees",
                        amount=AmountTemplate(
                            number="-5",
                            currency="{{ currency }}",
                        ),
                    ),
                ],
            ),
            ImportList(
                root=[
                    ImportRule(
                        common_cond=SimpleTxnMatchRule(
                            source_account=StrExactMatch(equals="Foobar")
                        ),
                        match=[
                            TxnMatchVars(
                                cond=SimpleTxnMatchRule(
                                    extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                                ),
                                vars=dict(foo="bar{{ 123 }}"),
                            )
                        ],
                        actions=[
                            ActionAddTxn(
                                type=ActionType.add_txn,
                                file="{{ extractor }}.bean",
                                txn=TransactionTemplate(
                                    metadata=[
                                        MetadataItemTemplate(
                                            name="var_value", value="{{ foo }}"
                                        )
                                    ],
                                    postings=[
                                        PostingTemplate(
                                            account="Assets:Bank:{{ source_account }}",
                                            amount=AmountTemplate(
                                                number="{{ amount }}",
                                                currency="{{ currency }}",
                                            ),
                                        ),
                                    ],
                                ),
                            )
                        ],
                    )
                ]
            ),
            [
                GeneratedTransaction(
                    id="mock.csv:123",
                    sources=["mock.csv"],
                    date="2024-05-05",
                    file="MOCK_EXTRACTOR.bean",
                    flag="*",
                    narration="MOCK_DESC",
                    links=[],
                    tags=[],
                    metadata=[
                        MetadataItem(name="var_value", value="bar123"),
                    ],
                    postings=[
                        GeneratedPosting(
                            account="Expenses:Food",
                            amount=Amount(
                                number="-118.45",
                                currency="BTC",
                            ),
                        ),
                        GeneratedPosting(
                            account="Assets:Bank:Foobar",
                            amount=Amount(
                                number="123.45",
                                currency="BTC",
                            ),
                        ),
                        GeneratedPosting(
                            account="Expenses:Fees",
                            amount=Amount(
                                number="-5",
                                currency="BTC",
                            ),
                        ),
                    ],
                )
            ],
            None,
            id="match-with-vars",
        ),
        pytest.param(
            Transaction(
                extractor="MOCK_EXTRACTOR",
                file="mock.csv",
                lineno=123,
                desc="MOCK_DESC",
                source_account="Foobar",
                date=datetime.date(2024, 5, 5),
                currency="BTC",
                amount=decimal.Decimal("123.45"),
            ),
            InputConfigDetails(
                extractor=ExractorInputConfig(
                    import_path="mock.extractor:SomeClassName",
                    as_name="extractor",
                    date_format="YYYY-MM-DD",
                    datetime_format="YYYY-MM-DD HH:mm:ss",
                ),
                default_txn=TransactionTemplate(
                    id="my-{{ file }}:{{ lineno }}",
                    date="2024-01-01",
                    flag="!",
                    narration="my-{{ desc }}",
                    postings=[
                        PostingTemplate(
                            account="Assets:Bank:{{ source_account }}",
                            amount=AmountTemplate(
                                number="{{ amount }}",
                                currency="{{ currency }}",
                            ),
                        ),
                    ],
                ),
            ),
            ImportList(
                root=[
                    ImportRule(
                        match=SimpleTxnMatchRule(
                            extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                        ),
                        actions=[
                            ActionAddTxn(
                                type=ActionType.add_txn,
                                file="{{ extractor }}.bean",
                                txn=TransactionTemplate(),
                            )
                        ],
                    )
                ]
            ),
            [
                GeneratedTransaction(
                    id="my-mock.csv:123",
                    sources=["mock.csv"],
                    date="2024-01-01",
                    file="MOCK_EXTRACTOR.bean",
                    flag="!",
                    narration="my-MOCK_DESC",
                    links=[],
                    tags=[],
                    postings=[
                        GeneratedPosting(
                            account="Assets:Bank:Foobar",
                            amount=Amount(
                                number="123.45",
                                currency="BTC",
                            ),
                        ),
                    ],
                )
            ],
            None,
            id="default-values",
        ),
        pytest.param(
            Transaction(
                extractor="MOCK_EXTRACTOR",
                file="mock.csv",
                lineno=123,
                desc="MOCK_DESC",
                source_account="Foobar",
                date=datetime.date(2024, 5, 5),
                currency="BTC",
                amount=decimal.Decimal("123.45"),
            ),
            InputConfigDetails(
                extractor=ExractorInputConfig(
                    import_path="mock.extractor:SomeClassName",
                    as_name="extractor",
                    date_format="YYYY-MM-DD",
                    datetime_format="YYYY-MM-DD HH:mm:ss",
                ),
            ),
            ImportList(
                root=[
                    ImportRule(
                        match=SimpleTxnMatchRule(
                            extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                        ),
                        actions=[
                            ActionAddTxn(
                                type=ActionType.add_txn,
                                file="{{ extractor }}.bean",
                                txn=TransactionTemplate(
                                    payee="{{ omit }}",
                                    postings=[
                                        PostingTemplate(
                                            account="Assets:Bank:Foobar",
                                            amount=AmountTemplate(
                                                number="{{ amount }}",
                                                currency="{{ currency }}",
                                            ),
                                        ),
                                    ],
                                ),
                            )
                        ],
                    )
                ]
            ),
            [
                GeneratedTransaction(
                    id="mock.csv:123",
                    sources=["mock.csv"],
                    date="2024-05-05",
                    file="MOCK_EXTRACTOR.bean",
                    flag="*",
                    links=[],
                    tags=[],
                    narration="MOCK_DESC",
                    postings=[
                        GeneratedPosting(
                            account="Assets:Bank:Foobar",
                            amount=Amount(
                                number="123.45",
                                currency="BTC",
                            ),
                        ),
                    ],
                )
            ],
            None,
            id="omit-token",
        ),
        pytest.param(
            Transaction(
                extractor="MOCK_EXTRACTOR",
                file="mock.csv",
                lineno=123,
                desc="MOCK_DESC",
                source_account="Foobar",
                date=datetime.date(2024, 5, 5),
                currency="BTC",
                amount=decimal.Decimal("123.45"),
            ),
            InputConfigDetails(
                extractor=ExractorInputConfig(
                    import_path="mock.extractor:SomeClassName",
                    as_name="extractor",
                    date_format="YYYY-MM-DD",
                    datetime_format="YYYY-MM-DD HH:mm:ss",
                ),
                prepend_postings=[
                    PostingTemplate(
                        account="Expenses:Food",
                        amount=AmountTemplate(
                            number="{{ -(amount - 5) }}",
                            currency="{{ currency }}",
                        ),
                    ),
                ],
                append_postings=[
                    PostingTemplate(
                        account="Expenses:Fees",
                        amount=AmountTemplate(
                            number="-5",
                            currency="{{ currency }}",
                        ),
                    ),
                ],
            ),
            ImportList(
                root=[
                    ImportRule(
                        match=SimpleTxnMatchRule(
                            extractor=StrExactMatch(equals="OTHER_MOCK_EXTRACTOR")
                        ),
                        actions=[],
                    )
                ]
            ),
            [],
            UnprocessedTransaction(
                txn=Transaction(
                    extractor="MOCK_EXTRACTOR",
                    file="mock.csv",
                    lineno=123,
                    desc="MOCK_DESC",
                    source_account="Foobar",
                    date=datetime.date(2024, 5, 5),
                    currency="BTC",
                    amount=decimal.Decimal("123.45"),
                ),
                import_id="mock.csv:123",
                prepending_postings=[
                    GeneratedPosting(
                        account="Expenses:Food",
                        amount=Amount(number="-118.45", currency="BTC"),
                        price=None,
                        cost=None,
                    ),
                ],
                appending_postings=[
                    GeneratedPosting(
                        account="Expenses:Food",
                        amount=Amount(number="-118.45", currency="BTC"),
                        price=None,
                        cost=None,
                    ),
                ],
            ),
            id="no-match",
        ),
        pytest.param(
            Transaction(
                extractor="MOCK_EXTRACTOR",
                file="mock.csv",
                lineno=123,
                desc="MOCK_DESC",
                source_account="Foobar",
                date=datetime.date(2024, 5, 5),
                currency="BTC",
                amount=decimal.Decimal("123.45"),
            ),
            InputConfigDetails(
                extractor=ExractorInputConfig(
                    import_path="mock.extractor:SomeClassName",
                    as_name="extractor",
                    date_format="YYYY-MM-DD",
                    datetime_format="YYYY-MM-DD HH:mm:ss",
                ),
            ),
            ImportList(
                root=[
                    ImportRule(
                        match=SimpleTxnMatchRule(
                            extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                        ),
                        actions=[
                            ActionDelTxn(
                                type=ActionType.del_txn,
                                txn=DeleteTransactionTemplate(
                                    id="id-{{ file }}:{{ lineno }}"
                                ),
                            )
                        ],
                    )
                ]
            ),
            [
                DeletedTransaction(id="id-mock.csv:123"),
            ],
            None,
            id="delete",
        ),
        pytest.param(
            Transaction(
                extractor="MOCK_EXTRACTOR",
                file="mock.csv",
                lineno=123,
                desc="MOCK_DESC",
                source_account="Foobar",
                date=datetime.date(2024, 5, 5),
                currency="BTC",
                amount=decimal.Decimal("123.45"),
            ),
            InputConfigDetails(
                extractor=ExractorInputConfig(
                    import_path="mock.extractor:SomeClassName",
                    as_name="extractor",
                    date_format="YYYY-MM-DD",
                    datetime_format="YYYY-MM-DD HH:mm:ss",
                ),
            ),
            ImportList(
                root=[
                    ImportRule(
                        match=SimpleTxnMatchRule(
                            extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                        ),
                        actions=[
                            ActionIgnore(
                                type=ActionType.ignore,
                            )
                        ],
                    )
                ]
            ),
            [],
            None,
            id="ignore",
        ),
    ],
)
def test_process_transaction(
    template_env: SandboxedEnvironment,
    input_config: InputConfigDetails,
    import_rules: ImportList,
    txn: Transaction,
    expected: list[GeneratedTransaction],
    expected_result: UnprocessedTransaction | None,
):
    result = None

    def get_result():
        nonlocal result
        result = yield from process_transaction(
            template_env=template_env,
            input_config=input_config,
            import_rules=import_rules,
            txn=txn,
        )

    assert list(get_result()) == expected
    assert result == expected_result


def test_process_transaction_generic(template_env: SandboxedEnvironment):
    """
    Test a generic transaction with no specific rules.

    Pulled this test out of the above test in order to debug it.

    Turned out that changes I made to how type safety was enforced in the
    GeneratedTransaction meant that empty link and tags resulted in
    empty lists(new behaviour) instead of None (previous behaviour).

    """
    txn = Transaction(
        extractor="MOCK_EXTRACTOR",
        file="mock.csv",
        lineno=123,
        desc="MOCK_DESC",
        source_account="Foobar",
        date=datetime.date(2024, 5, 5),
        currency="BTC",
        amount=decimal.Decimal("123.45"),
    )
    input_config = InputConfigDetails(
        extractor=ExractorInputConfig(
            import_path="mock.extractor:SomeClassName",
            as_name="extractor",
            date_format="YYYY-MM-DD",
            datetime_format="YYYY-MM-DD HH:mm:ss",
        ),
        prepend_postings=[
            PostingTemplate(
                account="Expenses:Food",
                amount=AmountTemplate(
                    number="{{ -(amount - 5) }}",
                    currency="{{ currency }}",
                ),
            ),
        ],
        append_postings=[
            PostingTemplate(
                account="Expenses:Fees",
                amount=AmountTemplate(
                    number="-5",
                    currency="{{ currency }}",
                ),
            ),
        ],
    )
    import_rules = ImportList(
        root=[
            ImportRule(
                match=SimpleTxnMatchRule(
                    extractor=StrExactMatch(equals="MOCK_EXTRACTOR")
                ),
                actions=[
                    ActionAddTxn(
                        type=ActionType.add_txn,
                        file="{{ extractor }}.bean",
                        txn=TransactionTemplate(
                            postings=[
                                PostingTemplate(
                                    account="Assets:Bank:{{ source_account }}",
                                    amount=AmountTemplate(
                                        number="{{ amount }}",
                                        currency="{{ currency }}",
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
            )
        ]
    )
    expected = [
        GeneratedTransaction(
            id="mock.csv:123",
            sources=["mock.csv"],
            date="2024-05-05",
            file="MOCK_EXTRACTOR.bean",
            flag="*",
            narration="MOCK_DESC",
            links=[],
            tags=[],
            postings=[
                GeneratedPosting(
                    account="Expenses:Food",
                    amount=Amount(
                        number="-118.45",
                        currency="BTC",
                    ),
                ),
                GeneratedPosting(
                    account="Assets:Bank:Foobar",
                    amount=Amount(
                        number="123.45",
                        currency="BTC",
                    ),
                ),
                GeneratedPosting(
                    account="Expenses:Fees",
                    amount=Amount(
                        number="-5",
                        currency="BTC",
                    ),
                ),
            ],
        )
    ]

    result = [
        item
        for item in process_transaction(
            template_env=template_env,
            input_config=input_config,
            import_rules=import_rules,
            txn=txn,
        )
    ]

    assert result[0].__dict__ == expected[0].__dict__
