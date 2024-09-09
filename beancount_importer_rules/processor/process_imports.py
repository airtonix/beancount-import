import logging
import pathlib
import typing
import uuid

from beancount_importer_rules.data_types import (
    DeletedTransaction,
    GeneratedTransaction,
    ImportList,
    InputConfig,
    Transaction,
    UnprocessedTransaction,
)
from beancount_importer_rules.processor.match_paths import get_matched_input_files
from beancount_importer_rules.processor.process_transaction import process_transaction
from beancount_importer_rules.templates import make_environment
from beancount_importer_rules.utils import strip_txn_base_path


def inputconfig_list_to_dict(
    input_configs: typing.List[InputConfig],
) -> dict[str, InputConfig]:
    return {str(input_config.match): input_config for input_config in input_configs}


def process_imports(
    imports: ImportList,
    context: dict | None,
    # dictionary of {[fingerprint]: InputConfig}
    inputs: dict[str, InputConfig],
    input_dir: pathlib.Path,
    on_import_processed: typing.Optional[typing.Callable[[Transaction], None]] = None,
    on_transaction_processed: typing.Optional[
        typing.Callable[[Transaction], None]
    ] = None,
) -> typing.Generator[
    UnprocessedTransaction | GeneratedTransaction | DeletedTransaction | Transaction,
    None,
    None,
]:
    logger = logging.getLogger(__name__)
    template_env = make_environment()
    omit_token = uuid.uuid4().hex

    if context is not None:
        template_env.globals.update(context)

    extractor_hash = get_matched_input_files(
        [directive for directive in inputs.values()], input_dir
    )

    for [fingerprint, manager] in extractor_hash.items():
        for matched_path in manager.matched_paths:
            logger.info(
                "Processing file %s with extractor %s",
                manager.matched_paths,
                fingerprint,
            )

            for transaction in manager.extractor.process(matched_path):
                txn = strip_txn_base_path(input_dir, transaction)
                txn_generator = process_transaction(
                    template_env=template_env,
                    input_config=manager.directive.config,
                    import_rules=imports,
                    omit_token=omit_token,
                    default_import_id=manager.extractor.get_import_id_template(),
                    txn=txn,
                    on_transaction_processed=on_transaction_processed,
                )

                unprocessed_txn = yield from txn_generator

                if unprocessed_txn is not None:
                    yield unprocessed_txn
            break
