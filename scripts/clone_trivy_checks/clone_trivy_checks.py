import os
import subprocess
from pathlib import Path

from scripts.utils.utils import read_content


class TrivyChecksCloner:
    REPOSITORY_URL = "https://github.com/aquasecurity/trivy-checks.git"

    def __init__(self, scanner_config_path: Path) -> None:
        self.scanner_config_path = scanner_config_path

    def clone(self):
        trivy_tag = self.get_trivy_checks_version()
        repo_dir = "trivy-checks"

        if not os.path.exists(repo_dir):
            print(f"Cloning repository with tag {trivy_tag}...")
            subprocess.run(
                ["git", "clone", "--branch", trivy_tag, self.REPOSITORY_URL], check=True
            )
        else:
            print(f"Repository already cloned in {repo_dir}.")

    def get_trivy_checks_version(self) -> str:
        return read_content(self.scanner_config_path)["iac"]["trivy_checks_version"]
