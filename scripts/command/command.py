"""Base class for commands."""

from abc import ABC, abstractmethod
import argparse


class ICommand(ABC):
    """Base class for commands."""

    @property
    @abstractmethod
    def help_msg(self) -> str:
        """Returns the help message for the command."""

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> None:
        """Executes the command."""

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """Adds arguments to the parser."""
