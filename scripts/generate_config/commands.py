"""Commands for generating configurations."""

import argparse
from pathlib import Path
from scripts.command.command import ICommand
from scripts.generate_config.common import IConfigGenerator
from scripts.generate_config.generate_config import ConfigGenerator
from scripts.generate_config.rules_config_generator import RulesConfigGenerator
from scripts.generate_config.scanner_config_generator import ScannerConfigGenerator
from scripts.utils.constants import ROOT_PATH, RULES_FOLDER, SCANNER_CONFIG_FILENAME


def generate_and_print(
    config_generator_cls: type[IConfigGenerator], path: Path
) -> None:
    """Generates and prints the configuration."""

    config = config_generator_cls(path).generate()
    print(config.to_json())


class GenerateConfigCommand(ICommand):
    """Generates the full configuration."""

    help_msg = "Generate general configuration"

    def execute(self, args: argparse.Namespace) -> None:
        generate_and_print(ConfigGenerator, ROOT_PATH)


class GenerateScannerConfigCommand(ICommand):
    """Generates the scanner configuration."""

    help_msg = "Generate scanner configuration"

    def execute(self, args: argparse.Namespace) -> None:
        generate_and_print(ScannerConfigGenerator, ROOT_PATH / SCANNER_CONFIG_FILENAME)


class GenerateRulesConfigCommand(ICommand):
    """Generates the rules configuration."""

    help_msg = "Generate rules configuration"

    def execute(self, args: argparse.Namespace) -> None:
        generate_and_print(RulesConfigGenerator, ROOT_PATH / RULES_FOLDER)
