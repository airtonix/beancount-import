import decimal
import pathlib
from typing import Dict, List

from beancount_importer_rules.data_types import Transaction
from beancount_importer_rules.extractor import ExtractorCsvBase


class MercuryCsvExtractor(ExtractorCsvBase):
    name: str = "mercury"
    fields: List[str] = [
        "Date (UTC)",
        "Description",
        "Amount",
        "Status",
        "Source Account",
        "Bank Description",
        "Reference",
        "Note",
        "Last Four Digits",
        "Name On Card",
        "Category",
        "GL Code",
        "Timestamp",
        "Original Currency",
    ]

    def process_line(
        self,
        lineno: int,
        line: Dict[str, str],
        file_path: pathlib.Path,
        line_count: int,
    ) -> Transaction:
        date = self.parse_date(line.pop("Date (UTC)"))
        desc = line.pop("Description")
        amount = decimal.Decimal(line.pop("Amount"))
        status = line.pop("Status")
        source_account = line.pop("Source Account")
        bank_desc = line.pop("Bank Description")
        reference = line.pop("Reference")
        note = line.pop("Note")
        category = line.pop("Category")
        currency = line.pop("Original Currency")
        name_on_card = line.pop("Name On Card")
        last_four_digits = line.pop("Last Four Digits")
        gl_code = line.pop("GL Code")
        timestamp = self.parse_datetime(line.pop("Timestamp"))

        return Transaction(
            extractor=self.name,
            file=str(file_path),
            lineno=lineno + 1,
            reversed_lineno=lineno - line_count,
            timezone="UTC",
            extra=line,
            # The following fields are unique to this extractor
            date=date,
            desc=desc,
            amount=amount,
            status=status,
            source_account=source_account,
            bank_desc=bank_desc,
            reference=reference,
            note=note,
            category=category,
            currency=currency,
            name_on_card=name_on_card,
            last_four_digits=last_four_digits,
            gl_code=gl_code,
            timestamp=timestamp,
        )
