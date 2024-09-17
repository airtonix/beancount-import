# an extract is a class that returns a callable
# the callable accepts a file and returns a list of transactions
import csv
import datetime
import hashlib
import os
import pathlib
import sys
import typing
from importlib import import_module
from pathlib import Path

import arrow

from beancount_importer_rules.data_types import (
    ExractorInputConfig,
    Fingerprint,
    Transaction,
)

type ExtractorFactory = typing.Callable[[ExractorInputConfig], type[ExtractorBase]]


class ExtractorError(Exception):
    def __init__(self, module: str, klass_name: str):
        self.module = module
        self.klass_name = klass_name


class ExtractorImportError(ExtractorError):
    def __str__(self):
        return f"Could not import module {self.module}"


class ExtractorClassNotFoundError(ExtractorError):
    def __str__(self):
        return f"Could not find class {self.klass_name} in module {self.module}"


class ExtractorClassNotSubclassError(ExtractorError):
    def __str__(self):
        return f"Class {self.klass_name} in module {self.module} is not a subclass of ExtractorBase"


class ExtractorClassInvalidInputFileError(ExtractorError):
    def __str__(self):
        return f"Class {self.klass_name} in module {self.module} does not accept input_file=None"


class ExtractorClassInvalidInputMissingFileNameError(ExtractorError):
    def __str__(self):
        return (
            f"Class {self.klass_name} in module {self.module} does not have a filename"
        )


class ExtractorClassIncorrectlyCraftedError(ExtractorError):
    def __str__(self):
        return f"Class {self.klass_name} in module {self.module} is incorrectly crafted"


def create_extractor_factory(
    class_name: typing.Optional[str] = None,
    working_dir: Path = Path.cwd(),
) -> ExtractorFactory:
    """
    Manages importing the defined extractor module and returning the extractor
    """

    class_name = class_name or "Importer"
    working_dir = working_dir
    sys.path.append(str(working_dir))

    def get_extractor(extractor: ExractorInputConfig) -> type[ExtractorBase]:
        # set the import path to the working directory
        bits = extractor.import_path.split(":")
        module_import = bits[0]
        module_class = bits[1] if len(bits) > 1 else class_name

        try:
            module = import_module(module_import)
        except ImportError:
            raise ExtractorImportError(
                module=module_import,
                klass_name=module_class,
            )

        try:
            klass = getattr(module, module_class)
        except AttributeError:
            raise ExtractorClassNotFoundError(
                module=module_import,
                klass_name=module_class,
            )

        if not issubclass(klass, ExtractorBase):
            raise ExtractorClassNotSubclassError(
                module=module_import,
                klass_name=module_class,
            )

        return klass

    return get_extractor


DEFAULT_IMPORT_ID_TEMPLATE: str = "{{ file | as_posix_path }}:{{ reversed_lineno }}"


class ExtractorBase:
    """
    Base class for extractors

    Examples

    ```python
    class MyExtractor(ExtractorBase):
        def detect(self):
            return True

        def process(self):
            yield Transaction(
                date=datetime.date.today(),
                narration="Test transaction",
                amount=Decimal("10.00"),
                currency="USD",
            )
    ```
    """

    name: str = "extractor"
    date_field: str = "Date"
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        name: str | None = None,
        date_field: str | None = None,
        date_format: str | None = None,
        datetime_format: str | None = None,
    ):
        self.name = name or self.name
        self.date_field = date_field or self.date_field
        self.date_format = date_format or self.date_format
        self.datetime_format = datetime_format or self.datetime_format

    def get_import_id_template(self) -> str:
        return DEFAULT_IMPORT_ID_TEMPLATE

    def detect(self, file_path: pathlib.Path) -> bool:
        raise NotImplementedError()

    def fingerprint(self, file_path: pathlib.Path) -> Fingerprint | None:
        raise NotImplementedError()

    def parse_date(self, date_str: str) -> datetime.date:
        raise NotImplementedError()

    def parse_datetime(self, date_str: str) -> datetime.datetime:
        raise NotImplementedError()

    def process(
        self, file_path: pathlib.Path
    ) -> typing.Generator[Transaction, None, None]:
        raise NotImplementedError()


class ExtractorCsvBase(ExtractorBase):
    """
    Base class for CSV extractors

    Create a file called `extractors/csv.py` by
    subclassing [`ExtractorCsvBase`][beancount_importer_rules.extractor.ExtractorCsvBase]:

    ```python
    class MyCsvExtractor(ExtractorCsvBase):

        fields = ["Date", "Description", "Amount", "Currency"]

        def process_line(self, lineno, line):
            return Transaction(
                date=self.parse_date(line["Date"]),
                narration=line["Description"],
                amount=Decimal(line["Amount"]),
                currency=line["Currency"],
            )
    ```
    """

    fields: typing.List[str]
    """The fields in the CSV file"""
    delimiter: str = ","
    """The delimiter used in the CSV file"""

    def parse_date(self, date_str: str) -> datetime.date:
        """
        Parse a date string using the self.format
        """
        return arrow.get(date_str, self.date_format).date()

    def parse_datetime(self, date_str: str) -> datetime.datetime:
        """
        Parse a date string using the self.format
        """
        return arrow.get(date_str, self.datetime_format).datetime

    def get_linecount(self, file_path: pathlib.Path) -> int:
        """
        Get the number of lines in a file
        """
        return sum(1 for i in open(file_path, "rb"))

    def fingerprint(self, file_path: pathlib.Path) -> Fingerprint | None:
        """
        Generate a fingerprint for the CSV file
        """
        with open(file_path, "r") as file_contents:
            file_contents.seek(0, os.SEEK_SET)  # noqa: F821

            reader = csv.DictReader(file_contents)
            if reader.fieldnames is None:
                return

            row = None
            for row in reader:
                pass

            if row is None:
                return

            hash = hashlib.sha256()
            for field in reader.fieldnames:
                hash.update(row[field].encode("utf8"))

            date = self.parse_date(row[self.date_field])
            return Fingerprint(
                starting_date=date,
                first_row_hash=hash.hexdigest(),
            )

    def detect(self, file_path: pathlib.Path) -> bool:
        """
        Check if the input file is a CSV file with the expected
        fields. Should this extractor be used to process the file?
        """
        if self.fields is None:
            raise ExtractorClassIncorrectlyCraftedError(
                module=self.__module__,
                klass_name=self.__class__.__name__,
            )

        with open(file_path, "r") as file_contents:
            file_contents.seek(0, os.SEEK_SET)  # noqa: F821
            reader = csv.DictReader(file_contents)
            try:
                return reader.fieldnames == self.fields
            except Exception:
                return False

    def detect_has_header(self, file_path: pathlib.Path) -> bool:
        """
        Check if the supplied csv file has a header row.

        It will if the fieldnames attribute is not None and they match the
        values of the first row of the file.

        We do this to detect if we need to skip the first row; it seems that
        the DictReader class does not automatically detect if the file has a
        header row or not and will return the first row as data if the
        fieldnames attribute is not set.
        """
        if self.fields is None:
            raise ExtractorClassIncorrectlyCraftedError(
                module=self.__module__,
                klass_name=self.__class__.__name__,
            )

        with open(file_path, "r") as file_contents:
            file_contents.seek(0, os.SEEK_SET)  # noqa: F821
            reader = csv.DictReader(file_contents)
            file_contents.seek(0, os.SEEK_SET)  # noqa: F821

            try:
                outcome = reader.fieldnames == self.fields
                return outcome
            except Exception:
                return False

    def process_line(
        self, lineno: int, line: dict, file_path: pathlib.Path, line_count: int
    ) -> Transaction:
        """
        Process a line in the CSV file and return a transaction.

        This method should be implemented by subclasses to return a [`Transaction`][beancount_importer_rules.data_types.Transaction].
        """
        raise NotImplementedError()

    def process(
        self, file_path: pathlib.Path
    ) -> typing.Generator[Transaction, None, None]:
        """
        Process the CSV file and yield transactions.

        Loops over the rows in the CSV file and yields a transaction for each row by calling
        [`process_line`](beancount_importer_rules.extractor.ExtractorCsvBase.process_line).
        """
        has_header = self.detect_has_header(file_path)
        line_count = self.get_linecount(file_path)

        with open(file_path, "r") as file_contents:
            if has_header:
                reader = csv.DictReader(file_contents, delimiter=self.delimiter)
            else:
                reader = csv.DictReader(
                    file_contents, fieldnames=self.fields, delimiter=self.delimiter
                )

            for lineno, line in enumerate(reader, start=has_header and 1 or 0):
                txn = self.process_line(
                    lineno=lineno, line=line, file_path=file_path, line_count=line_count
                )

                yield txn
