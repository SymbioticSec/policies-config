"""Common classes for generating configurations."""

from abc import ABC, abstractmethod
from dataclasses import asdict
import json


class ToJSONMixin:
    """Mixin to convert an object to a JSON string."""

    def to_json(self):
        """Returns the object as a JSON string."""

        return json.dumps(asdict(self))


class IConfigGenerator(ABC):
    """Generates a configuration."""

    @abstractmethod
    def generate(self) -> ToJSONMixin:
        """Generates the configuration."""
