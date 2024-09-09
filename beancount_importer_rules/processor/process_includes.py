import pathlib
import typing

import yaml

from beancount_importer_rules.data_types import (
    ImportRule,
)


# TODO: remove this and use pyyaml-include instead
def process_includes(
    includerule: str | typing.List[str], input_dir: pathlib.Path
) -> typing.List[ImportRule]:
    imports: typing.List[ImportRule] = []

    includes = includerule if isinstance(includerule, list) else [includerule]

    for include in includes:
        include_doc = yaml.safe_load(include)
        imports.append(include_doc.imports)

    return imports
