"""
Temporary until I implement a better
way to handle includes in the rules.
"""

import pathlib
import sys

import yaml
from pydantic import TypeAdapter

from beancount_importer_rules.data_types import (
    ImportList,
    ImportRule,
    IncludeRule,
)

RuleListAdapter = TypeAdapter(list[ImportRule | IncludeRule])


class NoDatesSafeLoader(yaml.SafeLoader):
    @classmethod
    def remove_implicit_resolver(cls, tag_to_remove):
        """
        Remove implicit resolvers for a particular tag

        Takes care not to modify resolvers in super classes.

        We want to load datetimes as strings, not dates, because we
        go on to serialise as json which doesn't have the advanced types
        of yaml, and leads to incompatibilities down the track.
        """
        if "yaml_implicit_resolvers" not in cls.__dict__:
            cls.yaml_implicit_resolvers = cls.yaml_implicit_resolvers.copy()

        for first_letter, mappings in cls.yaml_implicit_resolvers.items():
            cls.yaml_implicit_resolvers[first_letter] = [
                (tag, regexp) for tag, regexp in mappings if tag != tag_to_remove
            ]


NoDatesSafeLoader.remove_implicit_resolver("tag:yaml.org,2002:timestamp")


def load_includes(workdir_path: pathlib.Path, include_path: pathlib.Path) -> ImportList:
    with include_path.open("rt") as fo:
        rules = yaml.load(fo, Loader=NoDatesSafeLoader)
        try:
            imported = RuleListAdapter.validate_python(rules)
        except Exception as e:
            # pretty print the error
            print(
                f"Error loading include file: {include_path}.\n\n"
                f"{e}\n\n"
                f"Include file content:\n"
                f"{yaml.dump(rules, indent=2)}"
            )
            sys.exit(1)

        return resolve_includes(workdir_path=workdir_path, rules=imported)


def resolve_includes(
    workdir_path: pathlib.Path, rules: list[ImportRule | IncludeRule]
) -> ImportList:
    imports = ImportList(root=[])

    for rule in rules:
        if isinstance(rule, ImportRule):
            imports.root.append(rule)
        else:
            # convert to a list of strings
            paths = rule.include if isinstance(rule.include, list) else [rule.include]
            for include_path in paths:
                include_path = workdir_path / include_path
                includes = load_includes(workdir_path, include_path)
                imports.root.extend(includes.root)

    return imports
