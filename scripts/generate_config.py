"""Generates the complete configuration in YAML format."""

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from scripts.rules_config_generator import RulesConfig, RulesConfigGenerator
from scripts.scanner_config_generator import ScannerConfigGenerator, ScannersConfig
from scripts.constants import RULES_FOLDER, SCANNER_CONFIG_FILENAME


@dataclass
class Config:
    """Complete configuration."""

    scanners: ScannersConfig
    rules: RulesConfig


def generate_config(directory_path: Path) -> Config:
    """Generates the complete configuration in YAML format."""

    scanner_config = ScannerConfigGenerator(
        directory_path / SCANNER_CONFIG_FILENAME
    ).generate()
    rules_config = RulesConfigGenerator(directory_path / RULES_FOLDER).generate()
    return Config(scanners=scanner_config, rules=rules_config)


if __name__ == "__main__":
    root_path = Path(__file__).parent.parent.resolve()
    config = generate_config(root_path)
    print(json.dumps(asdict(config)))
