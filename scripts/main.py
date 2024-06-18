"""Scripts entrypoint."""

import argparse
from pathlib import Path

from scripts.generate_config.common import IConfigGenerator
from scripts.generate_config.generate_config import ConfigGenerator
from scripts.generate_config.rules_config_generator import RulesConfigGenerator
from scripts.generate_config.scanner_config_generator import ScannerConfigGenerator
from scripts.utils.constants import RULES_FOLDER, SCANNER_CONFIG_FILENAME


def generate_and_print(
    config_generator_cls: type[IConfigGenerator], path: Path
) -> None:
    """Generates and prints the configuration."""

    config = config_generator_cls(path).generate()
    print(config.to_json())


def main():
    """Main entry point for script execution."""
    parser = argparse.ArgumentParser(description="Generate and print configurations.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate-config", help="Generate general configuration")
    subparsers.add_parser(
        "generate-scanner-config", help="Generate scanner configuration"
    )
    subparsers.add_parser("generate-rules-config", help="Generate rules configuration")
    args = parser.parse_args()
    root_path = Path(__file__).parent.parent.resolve()
    if args.command == "generate-config":
        generate_and_print(ConfigGenerator, root_path)
    elif args.command == "generate-scanner-config":
        generate_and_print(ScannerConfigGenerator, root_path / SCANNER_CONFIG_FILENAME)
    elif args.command == "generate-rules-config":
        generate_and_print(RulesConfigGenerator, root_path / RULES_FOLDER)


if __name__ == "__main__":
    main()
