# Getting Started

### 1. Install the package

[pip](https://pypi.org/project/pip/)

```sh
pip install beancount-importer-rules=={{ git.short_tag }}
```

or

```sh
pdm install beancount-importer-rules=={{ git.short_tag }}
```

or

```sh
poetry add beancount-importer-rules=={{ git.short_tag }}
```


### 2. Create extractors

::: beancount_importer_rules.extractor.ExtractorCsvBase
    options:
      show_root_toc_entry: false
      show_bases: false
      show_source: false
      members: false

### 3. Create import rules

::: beancount_importer_rules.data_types.ImportDoc
    options:
      show_root_toc_entry: false
      show_bases: false
      show_source: false
      members: false

### 4. Run the importer

::: beancount_importer_rules.cli.import_cmd
    options:
      show_root_toc_entry: false
      show_bases: false
      show_source: false


## Read More

- [Configuration](configuration.md)
- [API Reference](api.md)
