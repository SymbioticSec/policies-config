"""Generates the complete configuration in YAML format."""

from dataclasses import dataclass
from pathlib import Path

from scripts.generate_config.common import IConfigGenerator, ToJSONMixin
from scripts.generate_config.rules_config_generator import (
    RulesConfig,
    RulesConfigGenerator,
)
from scripts.generate_config.scanner_config_generator import (
    ScannerConfigGenerator,
    ScannersConfig,
)
from scripts.utils.constants import RULES_FOLDER, SCANNER_CONFIG_FILENAME


@dataclass
class Config(ToJSONMixin):
    """Complete configuration."""

    scanners: ScannersConfig
    rules: RulesConfig


class ConfigGenerator(IConfigGenerator):
    """Generates the complete configuration."""

    def __init__(self, directory_path: Path):
        self.directory_path = directory_path

    def generate(self) -> Config:
        """Generates the complete configuration in YAML format."""

        scanner_config = ScannerConfigGenerator(
            self.directory_path / SCANNER_CONFIG_FILENAME
        ).generate()
        rules_config = RulesConfigGenerator(
            self.directory_path / RULES_FOLDER
        ).generate()
        return Config(scanners=scanner_config, rules=rules_config)
