import pathlib
from datetime import date, datetime

from jinja2.sandbox import SandboxedEnvironment


def as_posix_path(path: pathlib.Path) -> str:
    return pathlib.Path(path).as_posix()


def as_datetime(value):
    return datetime.strptime(value, "%Y-%m-%d")


def as_date(value) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def datetime_format(value, format="%H:%M %d-%m-%y") -> str:
    return datetime.strftime(value, format)


def make_environment():
    env = SandboxedEnvironment()
    env.filters["as_date"] = as_date
    env.filters["as_datetime"] = as_datetime
    env.filters["datetime_format"] = datetime_format
    env.filters["as_posix_path"] = as_posix_path
    return env
