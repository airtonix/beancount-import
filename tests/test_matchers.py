import pytest

from beancount_importer_rules.data_types import (
    StrContainsMatch,
    StrPrefixMatch,
    StrSuffixMatch,
)
from beancount_importer_rules.processor.matchers import (
    match_str,
)


@pytest.mark.parametrize(
    "pattern, value, expected",
    [
        ("^Foo([0-9]+)", "Foo0", True),
        ("^Foo([0-9]+)", "Foo", False),
        ("^Foo([0-9]+)", "foo0", False),
        ("^Foo([0-9]+)", "", False),
        ("^Foo([0-9]+)", None, False),
        (StrPrefixMatch(prefix="Foo"), "Foo", True),
        (StrPrefixMatch(prefix="Foo"), "Foobar", True),
        (StrPrefixMatch(prefix="Foo"), "FooBAR", True),
        (StrPrefixMatch(prefix="Foo"), "xFooBAR", False),
        (StrPrefixMatch(prefix="Foo"), "", False),
        (StrPrefixMatch(prefix="Foo"), None, False),
        (StrSuffixMatch(suffix="Bar"), "Bar", True),
        (StrSuffixMatch(suffix="Bar"), "fooBar", True),
        (StrSuffixMatch(suffix="Bar"), "FooBar", True),
        (StrSuffixMatch(suffix="Bar"), "Foobar", False),
        (StrSuffixMatch(suffix="Bar"), "FooBarx", False),
        (StrSuffixMatch(suffix="Bar"), "", False),
        (StrSuffixMatch(suffix="Bar"), None, False),
        (StrContainsMatch(contains="Foo"), "Foo", True),
        (StrContainsMatch(contains="Foo"), "prefix-Foo", True),
        (StrContainsMatch(contains="Foo"), "Foo-suffix", True),
        (StrContainsMatch(contains="Foo"), "prefix-Foo-suffix", True),
        (StrContainsMatch(contains="Foo"), "prefix-Fo-suffix", False),
        (StrContainsMatch(contains="Foo"), "", False),
        (StrContainsMatch(contains="Foo"), None, False),
    ],
)
def test_match_str(
    pattern: str | StrPrefixMatch | StrSuffixMatch | StrContainsMatch,
    value: str | None,
    expected: bool,
):
    assert match_str(pattern, value) == expected
