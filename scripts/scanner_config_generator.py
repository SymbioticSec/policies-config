"""Generates the scanner configuration."""

from dataclasses import asdict, dataclass
import json
import logging
from pathlib import Path
import urllib.error
import urllib.request

from scripts.constants import SCANNER_CONFIG_FILENAME
from scripts.utils import read_content


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


if __name__ == "__main__":
    root_path = Path(__file__).parent.parent.resolve()
    config = ScannerConfigGenerator(root_path / SCANNER_CONFIG_FILENAME).generate()
    print(json.dumps(asdict(config)))
