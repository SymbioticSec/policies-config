"""Utils for the scripts."""

from pathlib import Path
from typing import TypeVar

import yaml

T = TypeVar("T")


def replace_hyphens(data: dict[str, T]) -> dict[str, T]:
    """Replaces all hyphens recursively in the keys of the given dictionary with underscores."""

    new_data = {}
    for key, value in data.items():
        new_key = key.replace("-", "_")
        if isinstance(value, dict):
            new_data[new_key] = replace_hyphens(value)
        else:
            new_data[new_key] = value
    return new_data


def read_content(file_path: Path) -> dict:
    """Reads and returns the content of the given file. Replaces all hyphens with underscores."""

    with open(file_path, "r", encoding="utf-8") as file:
        content = yaml.safe_load(file)
        return replace_hyphens(content)
