"""Generates the complete configuration in YAML format."""

from dataclasses import dataclass, asdict
import inspect
import json
import logging
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request
import yaml

SCANNER_CONFIG_FILENAME = "scanner_config.yml"
RULES_FOLDER = "rules-config"


@dataclass
class ScannerConfig:
    """Single scanner configuration."""

    scanner_version: str
    scanner_dl_links: dict[str, str]
    rules_version: str | None = None


@dataclass
class ScannersConfig:
    """All scanners configurations."""

    iac: ScannerConfig


@dataclass()
class RuleConfig:
    """Single rule configuration."""

    severity: str | None = None

    @classmethod
    def from_dict(cls, values: dict[str, Any]):
        """Creates a RuleConfig instance from a dictionary, ignoring extra keys."""
        return cls(
            **{
                k: v
                for k, v in values.items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass
class RuleConfigWithDisabled(RuleConfig):
    """Single rule configuration with disabled flag."""

    disabled: bool | None = None


@dataclass
class CategoryRuleConfig:
    """Rules configuration for a single category."""

    rules_disabled: list[str]
    rules: dict[str, RuleConfig]
    minimum_severity: str | None = None


@dataclass
class RulesConfig:
    """All rules configurations."""

    iac: CategoryRuleConfig


@dataclass
class Config:
    """Complete configuration."""

    scanners: ScannersConfig
    rules: RulesConfig


def replace_hyphens(data: dict[str, Any]) -> dict[str, Any]:
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


class ScannerConfigGenerator:
    """Generates all scanner-related configurations."""

    BASE_TRIVY_RELEASE_URL = "https://github.com/aquasecurity/trivy/releases/download"

    def __init__(self, scanner_config_path: Path):
        self.scanner_config_path = scanner_config_path

    def _is_url_valid(self, url: str) -> bool:
        """Checks if the given URL is accessible."""

        try:
            req = urllib.request.Request(url, method="HEAD")
            resp = urllib.request.urlopen(req)
            return resp.status == 200
        except (urllib.error.HTTPError, urllib.error.URLError):
            return False
        except Exception as e:  # pylint: disable=broad-except
            logging.error("Unexpected error while checking URL %s: %s", url, e)
            return False

    def _get_trivy_download_links(self, version: str) -> dict[str, str]:
        """Returns the Trivy executable download links for the given version, for all systems."""

        systems = (
            ("windows", "windows-64bit", "zip"),
            ("darwin_amd64", "macOS-64bit", "tar.gz"),
            ("darwin_arm64", "macOS-ARM64", "tar.gz"),
            ("linux_amd64", "Linux-64bit", "tar.gz"),
            ("linux_arm64", "Linux-ARM64", "tar.gz"),
        )
        links = {
            label: f"{self.BASE_TRIVY_RELEASE_URL}/v{version}/trivy_{version}_{system}.{ext}"
            for label, system, ext in systems
        }
        for system, url in links.items():
            if not self._is_url_valid(url):
                raise ValueError(f"Invalid url for system {system}: {url}")
        return links

    def generate(self) -> ScannersConfig:
        """Reads, processes and returns the scanner configuration."""

        base_scanner_config = read_content(self.scanner_config_path)
        dl_links = self._get_trivy_download_links(
            base_scanner_config["iac"]["scanner_version"]
        )
        base_scanner_config["iac"].update({"scanner_dl_links": dl_links})
        return ScannersConfig(**base_scanner_config)


class RulesConfigGenerator:
    """Generates all rules-related configurations."""

    def __init__(self, rules_config_path: Path):
        self.rules_config_path = rules_config_path

    def _get_rules_files(self) -> dict[str, RuleConfigWithDisabled]:
        """Returns all specific rules configs by ID."""

        files = self.rules_config_path.rglob("*-AVD-*.yml")
        return {
            file.stem: RuleConfigWithDisabled(**read_content(file)) for file in files
        }

    def _partition_rules_disabled(
        self, rules: dict[str, RuleConfigWithDisabled]
    ) -> tuple[dict[str, RuleConfig], list[str]]:
        """
        Partitions the rules into a list of disabled rules,
        and a dict of enabled rules and their config.
        Removes the "disabled" key from the enabled rules config.
        """

        disabled_rules: list[str] = []
        enabled_rules: dict[str, RuleConfig] = {}

        for rule_id, rule_config in rules.items():
            if rule_config.disabled:
                disabled_rules.append(rule_id)
            else:
                enabled_rules[rule_id] = RuleConfig.from_dict(rule_config.__dict__)

        return enabled_rules, disabled_rules

    def generate(self) -> RulesConfig:
        """Reads, processes and returns the rules configuration from each rule file ."""

        defaults = read_content(self.rules_config_path / "iac" / "defaults.yml")
        rules_configs = self._get_rules_files()
        enabled_rules, disabled_rules = self._partition_rules_disabled(rules_configs)
        defaults.update({"rules_disabled": disabled_rules, "rules": enabled_rules})
        return RulesConfig(iac=CategoryRuleConfig(**defaults))


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
