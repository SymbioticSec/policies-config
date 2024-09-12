"""Scripts entrypoint."""

import argparse

from scripts.clone_trivy_checks.commands import CloneTrivyChecksCommand
from scripts.command.command_registry import CommandRegistry
from scripts.download_scanners.commands import (
    ClearScannersCommand,
    DownloadScannersCommand,
)
from scripts.generate_config.commands import (
    GenerateConfigCommand,
    GenerateRulesConfigCommand,
    GenerateScannerConfigCommand,
)
from scripts.generate_static_data.commands import (
    ClearStaticDataCommand,
    GenerateStaticDataCommand,
)


def main():
    """Main entry point for script execution."""
    registry = CommandRegistry()

    registry.register("generate-config", GenerateConfigCommand)
    registry.register("generate-scanner-config", GenerateScannerConfigCommand)
    registry.register("generate-rules-config", GenerateRulesConfigCommand)
    registry.register("download-scanners", DownloadScannersCommand)
    registry.register("clear-scanners", ClearScannersCommand)
    registry.register("generate-static-data", GenerateStaticDataCommand)
    registry.register("clear-static-data", ClearStaticDataCommand)
    registry.register("clone-trivy-checks", CloneTrivyChecksCommand)

    parser = argparse.ArgumentParser(description="Generate and print configurations.")
    registry.add_to_parser(parser)
    args = parser.parse_args()
    registry.execute(args)


if __name__ == "__main__":
    main()
