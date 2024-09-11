import datetime
import decimal
import pathlib

import pytest
import pytz

from beancount_importer_rules.data_types import (
    Amount,
    GeneratedPosting,
    GeneratedTransaction,
    MetadataItem,
    Transaction,
    UnprocessedTransaction,
)
from beancount_importer_rules.engine import load_config
from beancount_importer_rules.processor.match_paths import get_matched_input_files
from beancount_importer_rules.processor.process_imports import (
    process_imports,
)


@pytest.mark.parametrize(
    "folder, expected",
    [
        (
            "simple",
            [
                UnprocessedTransaction(
                    txn=Transaction(
                        extractor="mercury",
                        file="mercury.csv",
                        lineno=1,
                        reversed_lineno=-4,
                        date=datetime.date(2024, 4, 17),
                        post_date=None,
                        timestamp=datetime.datetime(
                            2024, 4, 17, 21, 30, 40, tzinfo=pytz.UTC
                        ),
                        timezone="UTC",
                        desc="GUSTO",
                        bank_desc="GUSTO; FEE 111111; Launch Platform LLC",
                        amount=decimal.Decimal("-46.00"),
                        currency="",
                        category="",
                        status="Sent",
                        source_account="Mercury Checking xx12",
                        note="",
                        reference="",
                        gl_code="",
                        name_on_card="",
                        last_four_digits="",
                        extra=None,
                    ),
                    import_id="mercury.csv:-4",
                    prepending_postings=[
                        GeneratedPosting(
                            account="Assets:Bank:US:Mercury",
                            amount=Amount(number="-46.00", currency="USD"),
                            price=None,
                            cost=None,
                        ),
                    ],
                ),
                GeneratedTransaction(
                    file="output.bean",
                    sources=["mercury.csv"],
                    id="mercury.csv:-3",
                    date="2024-04-16",
                    flag="*",
                    narration="Amazon Web Services",
                    payee=None,
                    tags=["MyTag"],
                    links=["MyLink"],
                    metadata=[MetadataItem(name="meta-name", value="meta-value")],
                    postings=[
                        GeneratedPosting(
                            account="Assets:Bank:US:Mercury",
                            amount=Amount(
                                number="-353.63",
                                currency="USD",
                            ),
                        ),
                        GeneratedPosting(
                            account="Expenses:FooBar",
                            amount=Amount(number="353.63", currency="USD"),
                        ),
                    ],
                ),
                UnprocessedTransaction(
                    txn=Transaction(
                        extractor="mercury",
                        file="mercury.csv",
                        lineno=3,
                        reversed_lineno=-2,
                        date=datetime.date(2024, 4, 16),
                        post_date=None,
                        timestamp=datetime.datetime(
                            2024, 4, 16, 3, 24, 57, tzinfo=pytz.UTC
                        ),
                        timezone="UTC",
                        desc="Adobe",
                        bank_desc="ADOBE  *ADOBE",
                        amount=decimal.Decimal("-54.99"),
                        currency="USD",
                        category="Software",
                        status="Sent",
                        type=None,
                        source_account="Mercury Credit",
                        dest_account=None,
                        note="",
                        reference="",
                        payee=None,
                        gl_code="",
                        name_on_card="Fang-Pen Lin",
                        last_four_digits="5678",
                        extra=None,
                    ),
                    import_id="mercury.csv:-2",
                    prepending_postings=[
                        GeneratedPosting(
                            account="Assets:Bank:US:Mercury",
                            amount=Amount(number="-54.99", currency="USD"),
                            price=None,
                            cost=None,
                        ),
                    ],
                ),
                UnprocessedTransaction(
                    txn=Transaction(
                        extractor="mercury",
                        file="mercury.csv",
                        lineno=4,
                        reversed_lineno=-1,
                        date=datetime.date(2024, 4, 15),
                        timestamp=datetime.datetime(
                            2024, 4, 15, 14, 35, 37, tzinfo=pytz.UTC
                        ),
                        timezone="UTC",
                        desc="Jane Doe",
                        bank_desc="Send Money transaction initiated on Mercury",
                        amount=decimal.Decimal("-1500.00"),
                        currency="",
                        category="",
                        status="Sent",
                        source_account="Mercury Checking xx1234",
                        note="",
                        reference="Profit distribution",
                        gl_code="",
                        name_on_card="",
                        last_four_digits="",
                        extra=None,
                    ),
                    prepending_postings=[
                        GeneratedPosting(
                            account="Assets:Bank:US:Mercury",
                            amount=Amount(number="-1500.00", currency="USD"),
                            price=None,
                            cost=None,
                        ),
                    ],
                    import_id="mercury.csv:-1",
                ),
            ],
        )
    ],
)
def test_process_imports(
    fixtures_folder: pathlib.Path, folder: str, expected: list[GeneratedTransaction]
):
    folder_path = fixtures_folder / "processor" / folder
    config_path = folder_path / "import.yaml"
    doc = load_config(config_path, workdir_path=fixtures_folder)

    extractor_hash = get_matched_input_files(
        [directive for directive in doc.inputs], folder_path
    )
    processed = []

    for fingerprint, manager in extractor_hash.items():
        imported = list(
            process_imports(
                fingerprint=fingerprint,
                manager=manager,
                context=doc.context,
                imports=doc.imports,
                input_dir=folder_path,
            )
        )
        processed.extend(imported)

    assert len(processed) == len(expected)
