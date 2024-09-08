import pathlib
import typing

from beancount_importer_rules.data_types import InputConfig
from beancount_importer_rules.extractor import ExtractorBase, create_extractor_factory
from beancount_importer_rules.processor.matchers import match_file
from beancount_importer_rules.processor.walk_dir import walk_dir_files


class ExtractorInstance(pathlib.Path):
    directive: InputConfig
    extractor: ExtractorBase
    matched_paths: typing.List[pathlib.Path]


type ExtractorInstanceHash = typing.Dict[str, ExtractorInstance]


def match_directive(
    input_directives: typing.List[InputConfig], matched_path: pathlib.Path
) -> InputConfig | None:
    """
    Given a path, return an ExtractorInstance if the path matches an input directive

    It should only match one directive.
    """

    for input_directive in input_directives:
        # continue to next directive if path doesn't match
        if not match_file(input_directive.match, matched_path):
            continue

        return input_directive

    return None


def get_matched_input_files(
    input_directives: typing.List[InputConfig], pwd: pathlib.Path
) -> ExtractorInstanceHash:
    """
    Given a list if ImportDoc.inputs directives, return a list of files that match the directives.
    """
    output: ExtractorInstanceHash = {}

    extractor_factory = create_extractor_factory(working_dir=pwd)

    def build_instance(
        input_directive: InputConfig, matched_path: pathlib.Path
    ) -> ExtractorInstance | None:
        # instantiate the extractor
        extractor = input_directive.config.extractor

        if extractor is None:
            raise ValueError(f"Extractor not specified for {matched_path}")

        instance = ExtractorInstance(matched_path)
        instance.directive = input_directive
        instance.matched_paths = [matched_path]

        ExtractorKlass = extractor_factory(extractor)
        instance.extractor = ExtractorKlass(
            name=input_directive.config.extractor.as_name,
            date_format=input_directive.config.extractor.date_format,
            datetime_format=input_directive.config.extractor.datetime_format,
            date_field=input_directive.config.extractor.date_field,
        )

        # if we get this far, return the instance
        # so we don't continue to the next directive
        return instance

    for matched_path in walk_dir_files(pwd):
        directive = match_directive(input_directives, matched_path)

        # path didn't match any directive, ignore it
        if not directive:
            continue

        # do we already have an instance for this directive?
        existing_instance = output.get(str(directive.match))
        if existing_instance is not None:
            existing_instance.matched_paths.append(matched_path)
            continue

        instance = build_instance(directive, matched_path)
        if instance is None:
            raise ValueError(f"Could not build instance for {matched_path}")

        output[str(directive.match)] = instance

        continue

    return output
