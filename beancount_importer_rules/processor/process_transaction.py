import dataclasses
import logging
import typing
import uuid

from jinja2.sandbox import SandboxedEnvironment

from beancount_importer_rules import constants
from beancount_importer_rules.data_types import (
    ActionType,
    DeletedTransaction,
    GeneratedTransaction,
    ImportList,
    IncludeRule,
    InputConfigDetails,
    MetadataItem,
    PostingTemplate,
    Transaction,
    UnprocessedTransaction,
)
from beancount_importer_rules.processor.filters import filter_first_non_none
from beancount_importer_rules.processor.generate_posting import generate_postings
from beancount_importer_rules.processor.matchers import (
    match_transaction,
    match_transaction_with_vars,
)


# TODO: split this up into smaller functions
#  1. match transactions
#  2. render transaction
def process_transaction(
    template_env: SandboxedEnvironment,
    input_config: InputConfigDetails,
    import_rules: ImportList,
    txn: Transaction,
    omit_token: str | None = None,
    default_import_id: str | None = None,
    on_transaction_processed: typing.Optional[
        typing.Callable[[Transaction], None]
    ] = None,
) -> typing.Generator[
    GeneratedTransaction | DeletedTransaction, None, UnprocessedTransaction | None
]:
    logger = logging.getLogger(__name__)
    txn_ctx = dataclasses.asdict(txn)
    if omit_token is None:
        omit_token = uuid.uuid4().hex
    txn_ctx["omit"] = omit_token
    default_txn = input_config.default_txn
    processed = False
    matched_vars: dict | None = None

    def render_str(value: str | bool | int | None) -> str | None:
        nonlocal matched_vars
        if value is None:
            return None

        template_ctx = txn_ctx
        if matched_vars is not None:
            template_ctx |= matched_vars

        result_value = template_env.from_string(str(value)).render(**template_ctx)

        if omit_token is not None and result_value == omit_token:
            return None

        return result_value

    def process_links_or_tags(
        links_or_tags: list[str] | None,
    ) -> list[str]:
        result: list[str] = []

        if links_or_tags is None:
            return result

        for item in links_or_tags:
            if item is None:
                continue
            rendered = render_str(item)
            if rendered is None:
                continue
            result.append(rendered)

        return result

    def render_txn_id(txn_id: str | None) -> str:
        rendered_txn_id = render_str(txn_id)

        if rendered_txn_id is None:
            logger.debug(
                "Omitting transaction %s:%s because of omit token",
                txn.file,
                txn.lineno,
            )
            raise ValueError(f"Transaction id is emty after rendering {txn_id}")

        return rendered_txn_id

    for import_rule in import_rules.root:
        matched_vars = None
        if isinstance(import_rule, IncludeRule):
            continue

        if isinstance(import_rule.match, list):
            matched = match_transaction_with_vars(
                txn, import_rule.match, common_condition=import_rule.common_cond
            )

            if matched is None:
                continue

            matched_vars = {
                key: template_env.from_string(value).render(**txn_ctx)
                if isinstance(value, str)
                else value
                for key, value in (matched.vars or {}).items()
            }

        elif not match_transaction(txn, import_rule.match):
            continue

        for action in import_rule.actions:
            if action.type == ActionType.ignore:
                logger.debug("Ignored transaction %s:%s", txn.file, txn.lineno)
                return None

            txn_id = filter_first_non_none(
                getattr(action.txn, "id"),
                getattr(default_txn, "id") if default_txn is not None else None,
                default_import_id,
                constants.DEFAULT_TXN_TEMPLATE["id"],
            )
            rendered_txn_id = render_txn_id(txn_id)

            if action.type == ActionType.del_txn:
                yield DeletedTransaction(id=rendered_txn_id)
                processed = True
                continue

            if action.type != ActionType.add_txn:
                # we only support add txn for now
                raise ValueError(f"Unsupported action type {action.type}")

            template_values = {
                key: filter_first_non_none(
                    getattr(action.txn, key),
                    getattr(default_txn, key) if default_txn is not None else None,
                    constants.DEFAULT_TXN_TEMPLATE.get(key),
                )
                for key in ("date", "flag", "narration", "payee")
            }
            template_values["id"] = txn_id

            posting_templates: list[PostingTemplate] = []
            if input_config.prepend_postings is not None:
                posting_templates.extend(input_config.prepend_postings)

            if action.txn.postings is not None:
                posting_templates.extend(action.txn.postings)

            elif default_txn is not None and default_txn.postings is not None:
                posting_templates.extend(default_txn.postings)

            if input_config.append_postings is not None:
                posting_templates.extend(input_config.append_postings)

            generated_tags = process_links_or_tags(action.txn.tags)
            generated_links = process_links_or_tags(action.txn.links)

            generated_metadata = []
            if action.txn.metadata is not None:
                for item in action.txn.metadata:
                    name = render_str(item.name)
                    value = render_str(item.value)
                    if not name or not value:
                        continue
                    generated_metadata.append(MetadataItem(name=name, value=value))

            if not generated_metadata:
                generated_metadata = None

            generated_postings = generate_postings(posting_templates, render_str)
            output_file = filter_first_non_none(action.file, input_config.default_file)
            if output_file is None:
                logger.error(
                    "Output file not defined when generating transaction with rule %s",
                    import_rule,
                )
                raise ValueError(
                    f"Output file not defined when generating transaction with rule {import_rule}"
                )

            processed = True
            output = render_str(output_file) or ""
            rest: typing.Dict[str, str] = {}
            for key, value in template_values.items():
                value = render_str(value)
                if value is None:
                    continue
                rest[key] = value

            sources = []

            if txn.file is not None:
                sources.append(txn.file)

            yield GeneratedTransaction(
                # We don't add line number here because sources it is going to be added as `import-src` metadata field.
                # Otherwise, the provided CSV's lineno may change every time we run import if the date order is desc and
                # there are new transactions added since then.
                sources=sources,
                file=output,
                tags=generated_tags,
                links=generated_links,
                metadata=generated_metadata,
                postings=generated_postings,
                **rest,
            )

            # TODO: make it possible to generate multiple transaction by changing rule config if there's
            #       a valid use case
        break

    logger.debug(
        "No match found for transaction %s at %s:%s", txn, txn.file, txn.lineno
    )

    if not processed:
        txn_id = filter_first_non_none(
            getattr(default_txn, "id") if default_txn is not None else None,
            default_import_id,
            constants.DEFAULT_TXN_TEMPLATE["id"],
        )

        rendered_txn_id = render_txn_id(txn_id)

        prepending_postings = None
        if input_config.prepend_postings is not None:
            prepending_postings = generate_postings(
                input_config.prepend_postings, render_str
            )
        appending_postings = None
        if input_config.append_postings is not None:
            appending_postings = generate_postings(
                input_config.prepend_postings or [], render_str
            )

        return UnprocessedTransaction(
            txn=txn,
            import_id=rendered_txn_id,
            output_file=render_str(input_config.default_file),
            prepending_postings=prepending_postings,
            appending_postings=appending_postings,
        )
