"""Commands for downloading scanners."""

import argparse
from scripts.command.command import ICommand
from scripts.download_scanners.download_scanners import ScannerDownloader
from scripts.generate_config.scanner_config_generator import ScannerConfigGenerator
from scripts.utils.constants import ROOT_PATH, SCANNER_CONFIG_FILENAME


class DownloadScannersCommand(ICommand):
    """Downloads and extracts scanners."""

    help_msg = "Download and extract scanners"

    def execute(self, args: argparse.Namespace) -> None:
        ScannerDownloader.clear_outputs()
        version = ScannerConfigGenerator(
            ROOT_PATH / SCANNER_CONFIG_FILENAME
        ).get_scanner_version()
        scanners_path = ScannerDownloader(version).extract_all_scanners()
        print(f"Scanners downloaded and extracted to: {scanners_path}")


class ClearScannersCommand(ICommand):
    """Deletes all downloaded scanners and archives."""

    help_msg = "Delete all downloaded scanners and archives"

    def execute(self, args: argparse.Namespace) -> None:
        ScannerDownloader.clear_outputs()
        print("Scanners cleared")
