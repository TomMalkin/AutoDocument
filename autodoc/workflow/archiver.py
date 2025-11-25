"""Handle the zipping and finalisation of generated outcomes."""

import zipfile
from pathlib import Path


class Archiver:
    """Service class."""

    def zip_downloads(self, download_dir: Path):
        """
        Zip downloads into a downloadable file.

        All files found in the download dir are for this instance, so can be
        zipped together. A future update could check each filename.
        """
        files_to_zip = [f for f in download_dir.iterdir() if f.is_file()]

        if files_to_zip:
            zip_filename = download_dir.name + ".zip"
            zip_filepath = download_dir.parent / zip_filename

            with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files_to_zip:
                    zipf.write(file_path, arcname=file_path.name)
