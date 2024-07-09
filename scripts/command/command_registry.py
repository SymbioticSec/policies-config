"""Registry for commands."""

import argparse
from scripts.command.command import ICommand


class CommandRegistry:
    """Registry for commands."""

    def __init__(self):
        self._commands: dict[str, type[ICommand]] = {}

    def register(self, name: str, cmd_cls: type[ICommand]) -> None:
        """Registers a command."""

        self._commands[name] = cmd_cls

    def execute(self, args: argparse.Namespace) -> None:
        """Executes the command."""

        command_name = args.command
        if command_name in self._commands:
            command_class = self._commands[command_name]
            command_instance = command_class()
            command_instance.execute(args)
        else:
            raise ValueError(f"Unknown command: {command_name}")

    def add_to_parser(self, parser: argparse.ArgumentParser) -> None:
        """Adds commands to the parser."""

        subparsers = parser.add_subparsers(dest="command", required=True)
        for name, cmd_info in self._commands.items():
            subparser = subparsers.add_parser(name, help=cmd_info.help_msg)
            cmd_info.add_arguments(subparser)
