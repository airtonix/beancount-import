import decimal
import pathlib
import typing

from beancount_importer_rules.data_types import Transaction
from beancount_importer_rules.extractor import ExtractorCsvBase
from tests.conftest import FIXTURE_FOLDER


class BasicExtractor(ExtractorCsvBase):
    name: str = "basic"
    date_field: str = "Date"
    date_format: str = "YYYY-MM-DD"
    fields: typing.List[str] = [
        "Account",
        "Date",
        "ignore",
        "Description",
        "Amount",
        "Balance",
    ]

    def process_line(
        self,
        lineno: int,
        line: typing.Dict[str, str],
        file_path: pathlib.Path,
        line_count: int,
    ) -> Transaction:
        date = self.parse_date(line.pop("Date"))
        description = line.pop("Description")
        amount = decimal.Decimal(line.pop("Amount"))

        return Transaction(
            extractor=self.name,
            file=str(file_path),
            lineno=lineno + 1,
            reversed_lineno=lineno - line_count,
            extra=line,
            # The following fields are unique to this extractor
            date=date,
            amount=amount,
            desc=description,
        )


def test_withheader():
    workdir = FIXTURE_FOLDER / "extractor"

    extractor = BasicExtractor()
    txns = list(extractor.process(workdir / "with_header.csv"))
    assert len(txns) == 1


def test_withoutheader():
    workdir = FIXTURE_FOLDER / "extractor"

    extractor = BasicExtractor()
    txns = list(extractor.process(workdir / "without_header.csv"))
    assert len(txns) == 1
