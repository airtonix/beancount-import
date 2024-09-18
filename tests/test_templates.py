from beancount_importer_rules.templates import make_environment


def test_make_environment():
    env = make_environment()
    assert env
    assert env.filters["as_date"]
    assert env.filters["as_datetime"]
    assert env.filters["datetime_format"]
    assert env.filters["as_posix_path"]


def test_format_datetime():
    env = make_environment()
    template = "{{ date | as_date | datetime_format('%Y') }}"
    result = env.from_string(template).render({"date": "2022-01-01"})

    assert result == "2022"
