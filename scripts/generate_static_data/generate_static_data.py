"""Generates static data (description, remediation snippet) for all Trivy policies."""

from collections.abc import Generator
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
from typing import Any


@dataclass
class PolicyStaticData:
    """Static data for a single policy."""

    description: str
    remediation: str


class StaticPolicyDataGenerator:
    """Generates static data (description, remediation snippet) for policies."""

    OUTPUT_DIR = Path("output")
    STATIC_DATA_DIR = OUTPUT_DIR / "static-data"

    def __init__(self):
        pass

    def read_policy_description(self, filepath: Path) -> str:
        """
        Reads the description of a policy from a file.
        The description is the first lines of the file, until the first section header.
        """

        lines = []
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("#"):
                    break
                lines.append(line)
        return "".join(lines).strip()

    def read_policy_remediation(self, filepath: Path) -> str:
        """
        Reads the remediation snippet of a policy from a file.
        The snippet is delimited with ``` characters.
        """

        lines = []
        snippet_started = False
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith(r"```"):
                    if snippet_started:
                        # End of snippet
                        break
                    # Start of snippet
                    snippet_started = True
                elif snippet_started:
                    # Snippet content
                    lines.append(line)
        return "".join(lines).strip()

    def process_policy_directory(self, directory_path: Path) -> PolicyStaticData | None:
        """Reads contents of a directory. Returns static data for the policy."""

        remediation_path = directory_path / "Terraform.md"
        description_path = directory_path / "docs.md"
        if not remediation_path.exists() or not description_path.exists():
            return None

        remediation = self.read_policy_remediation(directory_path / "Terraform.md")
        description = self.read_policy_description(directory_path / "docs.md")
        return PolicyStaticData(description, remediation)

    def yield_policy_directories(self, root_path: Path) -> Generator[Path, Any, None]:
        """Yields all policy subdirectories."""

        for policy_dir in root_path.rglob("AVD-*"):
            if not policy_dir.is_dir():
                continue
            yield policy_dir

    def generate_file(self, policy_dir: Path) -> None:
        """Generates and saves the static data JSON file for a single policy."""

        policy_static_data = self.process_policy_directory(policy_dir)
        if policy_static_data is None:
            return
        policy_id = policy_dir.name
        output_path = self.STATIC_DATA_DIR / f"{policy_id}.json"
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(policy_static_data.__dict__, file)

    def init_output_dir(self) -> None:
        """Initializes the output directory."""

        if not self.STATIC_DATA_DIR.exists():
            self.STATIC_DATA_DIR.mkdir(parents=True)

    def generate_all_policies(self, root_path: Path) -> None:
        """Generates and saves the static data JSON files for all policies."""

        self.init_output_dir()
        for policy_dir in self.yield_policy_directories(root_path):
            self.generate_file(policy_dir)

    @classmethod
    def clear_outputs(cls):
        """Deletes all generated rules static data files."""

        if cls.STATIC_DATA_DIR.exists():
            shutil.rmtree(cls.STATIC_DATA_DIR)
        if cls.OUTPUT_DIR.exists() and not any(cls.OUTPUT_DIR.iterdir()):
            shutil.rmtree(cls.OUTPUT_DIR)
