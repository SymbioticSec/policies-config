"""Classes to extract files from different archive types."""

from abc import ABC, abstractmethod
from pathlib import Path
import tarfile
import zipfile


class IArchiveExtractor(ABC):
    """Extracts a file from an archive."""

    extension: str

    @abstractmethod
    def extract(
        self,
        archive_path: Path,
        filename: str,
        dest_dir: Path,
        new_filename: str | None = None,
    ) -> Path:
        """Extracts the archive at the given path to the destination directory."""

        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)


class ZipExtractor(IArchiveExtractor):
    """Extracts a file from a ZIP archive."""

    extension = ".zip"

    def extract(
        self,
        archive_path: Path,
        filename: str,
        dest_dir: Path,
        new_filename: str | None = None,
    ) -> Path:
        super().extract(archive_path, filename, dest_dir)

        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extract(filename, dest_dir)
        if new_filename is not None:
            (dest_dir / filename).rename(dest_dir / new_filename)
        return dest_dir / filename


class TarGzExtractor(IArchiveExtractor):
    """Extracts a file from a tar.gz archive."""

    extension = ".tar.gz"

    def extract(
        self,
        archive_path: Path,
        filename: str,
        dest_dir: Path,
        new_filename: str | None = None,
    ) -> Path:
        super().extract(archive_path, filename, dest_dir)
        if new_filename is None:
            new_filename = filename

        with tarfile.open(archive_path, "r:gz") as archive:
            file = archive.extractfile(filename)
            with open(dest_dir / new_filename, "wb") as dest_file:
                dest_file.write(file.read())
        return dest_dir / filename


def get_extractor_from_extension(archive_ext: str) -> IArchiveExtractor:
    """Returns an extractor for the given archive suffixes (.zip, .tar.gz, ...)."""

    try:
        subcls = next(
            (
                child
                for child in IArchiveExtractor.__subclasses__()
                if child.extension == archive_ext
            )
        )
        return subcls()
    except StopIteration as exc:
        raise ValueError(f"Unsupported archive type: {archive_ext}") from exc
