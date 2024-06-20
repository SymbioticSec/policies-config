"""Downloads and extracts scanners for all supported systems."""

from pathlib import Path
import shutil
import urllib.request

from scripts.download_scanners.archive_extractor import get_extractor_from_extension
from scripts.download_scanners.supported_systems import (
    TRIVY_RELEASES,
    SupportedSystem,
)


class ScannerDownloader:
    """Downloads and extracts Trivy scanners for all supported systems."""

    OUTPUT_DIR = Path("output")
    ARCHIVE_DIR = OUTPUT_DIR / "archives"
    SCANNER_DIR = OUTPUT_DIR / "scanners"

    scanner_version: str

    def __init__(self, scanner_version: str):
        self.scanner_version = scanner_version
        self._init_output_dirs()

    def _init_output_dirs(self):
        """Initializes the output directories."""

        if not self.ARCHIVE_DIR.exists():
            self.ARCHIVE_DIR.mkdir(parents=True)
        if not self.SCANNER_DIR.exists():
            self.SCANNER_DIR.mkdir(parents=True)

    def download_release(self, system: SupportedSystem) -> Path:
        """
        Downloads the Trivy release for the given system.
        Returns the path to the downloaded archive.
        """

        ext = TRIVY_RELEASES[system].ext
        filepath = self.ARCHIVE_DIR / f"{system.value}.{ext}"
        urllib.request.urlretrieve(
            TRIVY_RELEASES[system].get_release_url(self.scanner_version),
            filepath,
        )
        return filepath

    def extract_scanner(self, system: SupportedSystem, archive_path: Path) -> Path:
        """
        Extracts the scanner from the given archive.
        Returns the path to the extracted scanner.
        """

        exec_name = TRIVY_RELEASES[system].binary_name
        extractor = get_extractor_from_extension("".join(archive_path.suffixes))
        return extractor.extract(
            archive_path, exec_name, self.SCANNER_DIR / system.value
        )

    def extract_all_scanners(self) -> Path:
        """
        Downloads Trivy releases for all supported systems.
        Extracts the executables from the archives.
        Returns the path to the directory containing all the scanners.
        """

        for i, system in enumerate(SupportedSystem):
            print(
                f"Downloading and extracting scanner for "
                f"{system.value} ({i + 1}/{len(SupportedSystem)})"
            )
            archive_path = self.download_release(system)
            self.extract_scanner(system, archive_path)
        return self.SCANNER_DIR

    @classmethod
    def clear_outputs(cls):
        """Deletes all downloaded archives and extracted scanners."""

        if cls.OUTPUT_DIR.exists():
            shutil.rmtree(cls.OUTPUT_DIR)
