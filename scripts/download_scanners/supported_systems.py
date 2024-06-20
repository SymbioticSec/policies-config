"""Supported systems for scanners."""

from dataclasses import dataclass
from enum import Enum

BASE_TRIVY_RELEASE_URL = "https://github.com/aquasecurity/trivy/releases/download"


class SupportedSystem(Enum):
    """Supported systems for Trivy scanners."""

    WINDOWS = "windows"
    DARWIN_AMD64 = "darwin_amd64"
    DARWIN_ARM64 = "darwin_arm64"
    LINUX_AMD64 = "linux_amd64"
    LINUX_ARM64 = "linux_arm64"


@dataclass
class TrivyRelease:
    """Information about a Trivy scanner release for a system."""

    system: SupportedSystem
    system_label: str
    ext: str
    binary_name: str

    def get_release_url(self, version: str):
        """Returns the Trivy release URL for the given system and version."""

        return (
            f"{BASE_TRIVY_RELEASE_URL}/v{version}/"
            f"trivy_{version}_{self.system_label}.{self.ext}"
        )


TRIVY_RELEASES = {
    SupportedSystem.WINDOWS: TrivyRelease(
        SupportedSystem.WINDOWS, "windows-64bit", "zip", "trivy.exe"
    ),
    SupportedSystem.DARWIN_AMD64: TrivyRelease(
        SupportedSystem.DARWIN_AMD64, "macOS-64bit", "tar.gz", "trivy"
    ),
    SupportedSystem.DARWIN_ARM64: TrivyRelease(
        SupportedSystem.DARWIN_ARM64, "macOS-ARM64", "tar.gz", "trivy"
    ),
    SupportedSystem.LINUX_AMD64: TrivyRelease(
        SupportedSystem.LINUX_AMD64, "Linux-64bit", "tar.gz", "trivy"
    ),
    SupportedSystem.LINUX_ARM64: TrivyRelease(
        SupportedSystem.LINUX_ARM64, "Linux-ARM64", "tar.gz", "trivy"
    ),
}
