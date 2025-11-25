"""Test the Archiver class."""

import zipfile
from pathlib import Path

from autodoc.workflow.archiver import Archiver


def test_zip_downloads_creates_zip_file(tmp_path: Path):
    """Test that downloads creates a zipfile."""
    # Setup: Create dummy files in a temporary download directory
    download_dir = tmp_path / "downloads"
    download_dir.mkdir()
    (download_dir / "file1.txt").write_text("content 1")
    (download_dir / "file2.txt").write_text("content 2")
    (download_dir / "subdir").mkdir()  # Should be ignored

    archiver = Archiver()
    archiver.zip_downloads(download_dir)

    # Assertions: Check if the zip file was created and contains the correct files
    zip_filepath = tmp_path / "downloads.zip"
    assert zip_filepath.exists()

    with zipfile.ZipFile(zip_filepath, "r") as zipf:
        namelist = zipf.namelist()
        assert len(namelist) == 2
        assert "file1.txt" in namelist
        assert "file2.txt" in namelist
        assert zipf.read("file1.txt").decode() == "content 1"
        assert zipf.read("file2.txt").decode() == "content 2"


def test_zip_downloads_no_files_in_dir(tmp_path: Path):
    """Test that no files means no zipfile."""
    # Setup: Create an empty download directory
    download_dir = tmp_path / "empty_downloads"
    download_dir.mkdir()

    archiver = Archiver()
    archiver.zip_downloads(download_dir)

    # Assertions: No zip file should be created if there are no files
    zip_filepath = tmp_path / "empty_downloads.zip"
    assert not zip_filepath.exists()


def test_zip_downloads_single_file_in_dir(tmp_path: Path):
    """Test that a single still creates a zipfile."""
    # Setup: Create a single file in the temporary download directory
    download_dir = tmp_path / "single_file_dir"
    download_dir.mkdir()
    (download_dir / "single.pdf").write_text("pdf content")

    archiver = Archiver()
    archiver.zip_downloads(download_dir)

    # Assertions: Check if the zip file was created and contains the single file
    zip_filepath = tmp_path / "single_file_dir.zip"
    assert zip_filepath.exists()

    with zipfile.ZipFile(zip_filepath, "r") as zipf:
        namelist = zipf.namelist()
        assert len(namelist) == 1
        assert "single.pdf" in namelist
        assert zipf.read("single.pdf").decode() == "pdf content"
