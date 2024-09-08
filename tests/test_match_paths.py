import typing

from beancount_importer_rules.data_types import (
    InputConfig,
)
from beancount_importer_rules.engine import load_config
from beancount_importer_rules.processor.match_paths import get_matched_input_files
from tests.conftest import FIXTURE_FOLDER


def find_input_by_match(inputs: typing.List[InputConfig], match: str):
    for input in inputs:
        if input.match == match:
            return input
    return None


def test_extractor_dateformat():
    folder_path = FIXTURE_FOLDER / "processor" / "simple"
    config_path = folder_path / "import.yaml"
    doc = load_config(config_path, workdir_path=FIXTURE_FOLDER)

    extractor_hash = get_matched_input_files(doc.inputs, folder_path)

    for [fingerprint, manager] in extractor_hash.items():
        matching_input = find_input_by_match(doc.inputs, fingerprint)
        assert matching_input is not None
        assert matching_input.config.extractor is not None

        if matching_input.config.extractor.date_format is None:
            assert (
                matching_input.config.extractor.date_format
                == manager.extractor.date_format
            )
        if matching_input.config.extractor.datetime_format is None:
            assert (
                matching_input.config.extractor.datetime_format
                == manager.extractor.datetime_format
            )
        if matching_input.config.extractor.as_name is None:
            assert matching_input.config.extractor.as_name == manager.extractor.name
