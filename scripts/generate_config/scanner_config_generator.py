"""Generates the scanner configuration."""

from dataclasses import dataclass
from pathlib import Path

from scripts.download_scanners.supported_systems import SupportedSystem
from scripts.generate_config.common import IConfigGenerator, ToJSONMixin
from scripts.utils.utils import read_content


@dataclass
class ScannerConfig:
    """Single scanner configuration."""

    scanner_version: str
    scanner_dl_links: dict[str, str]
    rules_version: str | None = None


@dataclass
class ScannersConfig(ToJSONMixin):
    """All scanners configurations."""

    iac: ScannerConfig


class ScannerConfigGenerator(IConfigGenerator):
    """Generates all scanner-related configurations."""

    # TODO: Update the URL to the actual S3 bucket URL
    BASE_SCANNERS_URL = "https://s3.../scanners"

    def __init__(self, scanner_config_path: Path):
        self.scanner_config_path = scanner_config_path

    def _get_download_links(self) -> dict[str, str]:
        """Returns the download links for all supported systems."""

        return {
            system.value: f"{self.BASE_SCANNERS_URL}/{system.value}/trivy.exe"
            for system in SupportedSystem
        }

    def get_scanner_version(self) -> str:
        """Reads the scanner version from the configuration file."""

        return read_content(self.scanner_config_path)["iac"]["scanner_version"]

    def generate(self) -> ScannersConfig:
        """Reads, processes and returns the scanner configuration."""

        base_scanner_config = read_content(self.scanner_config_path)
        base_scanner_config["iac"].update(
            {"scanner_dl_links": self._get_download_links()}
        )
        return ScannersConfig(**base_scanner_config)
