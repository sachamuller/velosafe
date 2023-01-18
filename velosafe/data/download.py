import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from urllib.request import urlopen

import py7zr
from tqdm import tqdm


@dataclass
class RemoteFile:
    url: str
    filename: str | Path
    md5sum: str | None = None

    def download(
        self, dest_dir: str | Path = "data", show_progress: bool = True, chunk_size: int = 1024 * 1024
    ) -> Path:
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

    def was_already_downloaded(self, parent_folder):
        return os.path.exists(os.path.join(parent_folder, self.filename))


class ZipRemoteFile(RemoteFile):
    def __init__(
        self,
        url: str,
        filename: str,
        md5sum: str | None = None,
        foldername_after_unzipping: str = "",
        foldername: str = "",
        path_files_to_keep: Dict[str, str] = {},
    ):
        super().__init__(url, filename, md5sum)
        self.foldername_after_unzipping = foldername_after_unzipping
        self.foldername = foldername
        self.path_files_to_keep = path_files_to_keep

    def was_already_downloaded(self, parent_folder):
        for file_to_keep in self.path_files_to_keep.values():
            if not os.path.exists(os.path.join(parent_folder, file_to_keep)):
                return False
        return True

    def unzip_7zip_file(self, parent_folder="data"):
        with py7zr.SevenZipFile(os.path.join(parent_folder, self.filename), "r") as zip_ref:
            zip_ref.extractall(parent_folder)
        os.remove(os.path.join(parent_folder, self.filename))

    def keep_only_necessary_files(self, parent_folder="data"):
        for old_name, new_name in self.path_files_to_keep.items():
            shutil.copy(os.path.join(parent_folder, old_name), os.path.join(parent_folder, new_name))
        shutil.rmtree(os.path.join(parent_folder, self.foldername_after_unzipping))
