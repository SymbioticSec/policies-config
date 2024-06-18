"""Scripts entrypoint."""

from pathlib import Path
import sys

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
    """Calls the correct script based on the first argument."""

    if len(sys.argv) > 1:
        root_path = Path(__file__).parent.parent.resolve()

        if sys.argv[1] == "generate-config":
            generate_and_print(ConfigGenerator, root_path)
        elif sys.argv[1] == "generate-scanner-config":
            generate_and_print(
                ScannerConfigGenerator, root_path / SCANNER_CONFIG_FILENAME
            )
        elif sys.argv[1] == "generate-rules-config":
            generate_and_print(RulesConfigGenerator, root_path / RULES_FOLDER)
        else:
            print("Unknown command")
    else:
        print("No command given")


if __name__ == "__main__":
    main()
