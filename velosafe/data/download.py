import hashlib
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen

from tqdm import tqdm


@dataclass
class RemoteFile:
    url: str
    filename: str | Path
    md5sum: str | None = None

    def download(self, dest_dir: str | Path, show_progress: bool = True, chunk_size: int = 1024 * 1024) -> Path:
        """
        Download the file located at url to dest_file.

        Will follow redirects.
        :param dest_dir: The file destination directory.
        :param show_progress: Print a progress bar to stdout if set to True.
        :param chunk_size: Number of bits to download before saving stream to file.

        :return: The file the dataset was downloaded to.
        """
        if self.filename:
            dest_file = Path(dest_dir).expanduser() / self.filename
        if dest_file.exists() and self.md5sum is not None and self.checksum(dest_file) == self.md5sum:
            return dest_file
        # Ensure the directory we'll put the downloaded file in actually exists
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(self.url) as response:
            file_size = response.headers["Content-Length"]
            if file_size is not None:
                file_size = int(file_size)
            else:
                show_progress = False
            with open(dest_file, "wb") as db_file:
                with tqdm(total=file_size, unit="B", unit_scale=True, disable=not show_progress) as progress_bar:
                    while chunk := response.read(chunk_size):
                        db_file.write(chunk)
                        progress_bar.update(chunk_size)
            if self.md5sum is not None and self.checksum(dest_file) != self.md5sum:
                dest_file.unlink()
                raise ValueError("File was corrupted during download. Please try again.")
            return dest_file

    @classmethod
    def checksum(self, file: Path) -> str:
        """
        Compute the md5 checksum of a file.
        """
        hasher = hashlib.md5()
        with open(file, "rb") as f:
            while chunk := f.read(128 * hasher.block_size):
                hasher.update(chunk)
        return hasher.hexdigest()
