"""Commands for generating static data."""

import argparse
from pathlib import Path
from scripts.command.command import ICommand
from scripts.generate_static_data.generate_static_data import StaticPolicyDataGenerator


class GenerateStaticDataCommand(ICommand):
    """Generates static data for all policies."""

    help_msg = "Generate static data"

    def execute(self, args: argparse.Namespace) -> None:
        StaticPolicyDataGenerator().generate_all_policies(Path(args.path))
        print("Static data generated")

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("path", type=str, help="Path to the AVD docs")


class ClearStaticDataCommand(ICommand):
    """Deletes all generated static data files."""

    help_msg = "Delete all generated static data files"

    def execute(self, args: argparse.Namespace) -> None:
        StaticPolicyDataGenerator.clear_outputs()
        print("Static data cleared")
