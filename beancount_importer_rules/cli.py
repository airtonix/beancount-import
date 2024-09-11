import os
import pathlib

import click

from beancount_importer_rules.engine import ImportRuleEngine
from beancount_importer_rules.environment import (
    LOG_LEVEL_MAP,
)


@click.group()
def cli():
    pass


@cli.command(name="import")
@click.option(
    "-w",
    "--workdir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    default=str(pathlib.Path.cwd()),
    help="The beanhub project path to work on",
)
@click.option(
    "-b",
    "--beanfile",
    type=click.Path(),
    default="main.bean",
    help="The path to main entry beancount file",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(),
    default=".beancount_imports.yaml",
    help="The path to import config file",
)
@click.option(
    "--remove-dangling",
    is_flag=True,
    help="Remove dangling transactions (existing imported transactions in Beancount files without corresponding generated transactions)",
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(
        list(map(lambda key: key.value, LOG_LEVEL_MAP.keys())), case_sensitive=False
    ),
    default=lambda: os.environ.get("LOG_LEVEL", "INFO"),
)
def import_cmd(
    config: str,
    workdir: str,
    beanfile: str,
    remove_dangling: bool,
    log_level: str,
):
    """
    Import transactions from external sources to Beancount files.

    Assuming the following directory structure:

    ```shell
    > tree .
    workspace/
        ├── extractors/
        │   ╰── my_extractor.py
        │
        ├── sources/
        │       ├── 2024-01-01.csv
        │       ├── 2024-01-02.csv
        │       ╰── 2024-01-03.csv
        │
        ├── imported/
        │   ├── 2024-01-01.bean
        │   ├── 2024-01-02.bean
        │   ╰── 2024-01-03.bean
        │
        ├── main.bean
        ├── options.bean
        ├── imported.bean
        ├── accounts.bean
        ├── data.bean
        ╰── importer_config.yaml
    ```

    The `import_cmd` command will import matching transactions
    found in matching files the `sources` directory to the
    `imported` directory.

    ```sh
    > beancount-import import \\
        -w workspace \\
        -b data.bean \\
        -c importer_config.yaml
    ```

    Note:
          We recommend having separate beanfiles for options and data.

            - `main.bean`
                - `data.bean`
                    - `accounts.bean`
                    - `imported.bean`
                - `options.bean`

          Your `main.bean` should import `data.bean`, `options.bean`.

          Your `data.bean` should import `accounts.bean`, `imported.bean`.

          This way, you can keep your data and options separate from your main beanfile.

          But more importantly, we recommend this because beancount-importer-rules doesn't
          understand some of the syntax used for options.

    """
    engine = ImportRuleEngine(
        workdir=workdir,
        config_path=config,
        beanfile_path=beanfile,
        remove_dangling=remove_dangling,
        log_level=log_level,
    )

    engine.run()
