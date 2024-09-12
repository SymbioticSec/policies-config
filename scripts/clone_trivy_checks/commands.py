"""Commands for cloning trivy-checks repository."""

import argparse

from scripts.clone_trivy_checks.clone_trivy_checks import TrivyChecksCloner
from scripts.command.command import ICommand
from scripts.utils.constants import ROOT_PATH, SCANNER_CONFIG_FILENAME


class CloneTrivyChecksCommand(ICommand):
    """Clone trivy-checks-repository."""

    help_msg = "Clone trivy-checks-repository."

    def execute(self, args: argparse.Namespace) -> None:
        TrivyChecksCloner(ROOT_PATH / SCANNER_CONFIG_FILENAME).clone()
