"""Generates the complete configuration in YAML format."""

import json
from pathlib import Path
import urllib.error
import urllib.request
import yaml

SCANNER_CONFIG_FILENAME = "scanner_config.yml"
RULES_FOLDER = "rules-config"


def read_content(file_path: Path) -> dict:
    """Reads and returns the content of the given file."""

    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


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

    def _get_trivy_download_links(self, version: str):
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

    def generate(self) -> dict:
        """Reads, processes and returns the scanner configuration."""

        base_scanner_config = read_content(self.scanner_config_path)
        dl_links = self._get_trivy_download_links(
            base_scanner_config["iac"]["scanner-version"]
        )
        base_scanner_config["iac"].update({"scanner-dl-links": dl_links})
        return base_scanner_config


class RulesConfigGenerator:
    """Generates all rules-related configurations."""

    def __init__(self, rules_config_path: Path):
        self.rules_config_path = rules_config_path

    def _get_rules_files(self) -> dict[str, dict]:
        """Returns all specific rules configs by ID."""

        files = self.rules_config_path.rglob("*-AVD-*.yml")
        return {file.stem: read_content(file) for file in files}

    def _partition_rules_disabled(
        self, rules: dict[str, dict]
    ) -> tuple[dict[str, dict], list[str]]:
        """
        Partitions the rules into a list of disabled rules,
        and a dict of enabled rules and their config.
        """

        disabled_rules = []
        enabled_rules = {}

        for rule_id, rule_config in rules.items():
            if rule_config.get("disabled", False):
                disabled_rules.append(rule_id)
            else:
                config_copy = rule_config.copy()
                del config_copy["disabled"]
                enabled_rules[rule_id] = config_copy

        return enabled_rules, disabled_rules

    def generate(self) -> dict:
        """Reads, processes and returns the rules configuration from each rule file ."""

        defaults = read_content(self.rules_config_path / "iac" / "defaults.yml")
        rules_configs = self._get_rules_files()
        enabled_rules, disabled_rules = self._partition_rules_disabled(rules_configs)
        defaults.update({"rules_disabled": disabled_rules, "rules": enabled_rules})
        return {"iac": defaults}


def generate_config(directory_path: Path):
    """Generates the complete configuration in YAML format."""

    scanner_config = ScannerConfigGenerator(
        directory_path / SCANNER_CONFIG_FILENAME
    ).generate()
    rules_config = RulesConfigGenerator(directory_path / RULES_FOLDER).generate()
    return {"scanners": scanner_config, "rules": rules_config}


if __name__ == "__main__":
    root_path = Path(__file__).parent.parent.resolve()
    config = generate_config(root_path)
    print(json.dumps(config))
