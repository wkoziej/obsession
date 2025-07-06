"""
Testy dla modułu file_structure.py
"""

from src.core.file_structure import RecordingStructure, FileStructureManager


class TestRecordingStructure:
    """Testy dla klasy RecordingStructure."""

    def test_recording_structure_creation(self, tmp_path):
        """Test tworzenia struktury nagrania."""
        recording_dir = tmp_path / "test_recording"
        video_file = recording_dir / "test.mkv"
        metadata_file = recording_dir / "metadata.json"
        extracted_dir = recording_dir / "extracted"

        structure = RecordingStructure(
            recording_dir=recording_dir,
            video_file=video_file,
            metadata_file=metadata_file,
            extracted_dir=extracted_dir,
        )

        assert structure.recording_dir == recording_dir
        assert structure.video_file == video_file
        assert structure.metadata_file == metadata_file
        assert structure.extracted_dir == extracted_dir

    def test_exists_all_present(self, tmp_path):
        """Test exists() gdy wszystkie pliki istnieją."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()

        video_file = recording_dir / "test.mkv"
        video_file.touch()

        metadata_file = recording_dir / "metadata.json"
        metadata_file.write_text('{"test": "data"}')

        extracted_dir = recording_dir / "extracted"
        extracted_dir.mkdir()

        structure = RecordingStructure(
            recording_dir=recording_dir,
            video_file=video_file,
            metadata_file=metadata_file,
            extracted_dir=extracted_dir,
        )

        assert structure.exists() is True

    def test_exists_missing_files(self, tmp_path):
        """Test exists() gdy brakuje plików."""
        recording_dir = tmp_path / "test_recording"
        video_file = recording_dir / "test.mkv"
        metadata_file = recording_dir / "metadata.json"
        extracted_dir = recording_dir / "extracted"

        structure = RecordingStructure(
            recording_dir=recording_dir,
            video_file=video_file,
            metadata_file=metadata_file,
            extracted_dir=extracted_dir,
        )

        assert structure.exists() is False

    def test_is_valid_correct_structure(self, tmp_path):
        """Test is_valid() dla poprawnej struktury."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()

        video_file = recording_dir / "test.mkv"
        video_file.touch()

        metadata_file = recording_dir / "metadata.json"
        metadata_file.write_text('{"test": "data"}')

        extracted_dir = recording_dir / "extracted"
        extracted_dir.mkdir()

        structure = RecordingStructure(
            recording_dir=recording_dir,
            video_file=video_file,
            metadata_file=metadata_file,
            extracted_dir=extracted_dir,
        )

        assert structure.is_valid() is True

    def test_is_valid_invalid_json(self, tmp_path):
        """Test is_valid() dla niepoprawnego JSON."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()

        video_file = recording_dir / "test.mkv"
        video_file.touch()

        metadata_file = recording_dir / "metadata.json"
        metadata_file.write_text("invalid json")

        extracted_dir = recording_dir / "extracted"
        extracted_dir.mkdir()

        structure = RecordingStructure(
            recording_dir=recording_dir,
            video_file=video_file,
            metadata_file=metadata_file,
            extracted_dir=extracted_dir,
        )

        assert structure.is_valid() is False

    def test_is_valid_missing_files(self, tmp_path):
        """Test is_valid() dla brakujących plików."""
        recording_dir = tmp_path / "test_recording"
        video_file = recording_dir / "test.mkv"
        metadata_file = recording_dir / "metadata.json"
        extracted_dir = recording_dir / "extracted"

        structure = RecordingStructure(
            recording_dir=recording_dir,
            video_file=video_file,
            metadata_file=metadata_file,
            extracted_dir=extracted_dir,
        )

        assert structure.is_valid() is False


class TestFileStructureManager:
    """Testy dla klasy FileStructureManager."""

    def test_get_structure(self, tmp_path):
        """Test get_structure()."""
        recording_dir = tmp_path / "test_recording"
        video_file = recording_dir / "test.mkv"

        structure = FileStructureManager.get_structure(video_file)

        assert structure.recording_dir == recording_dir
        assert structure.video_file == video_file
        assert structure.metadata_file == recording_dir / "metadata.json"
        assert structure.extracted_dir == recording_dir / "extracted"

    def test_create_structure(self, tmp_path):
        """Test create_structure()."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()
        video_file = recording_dir / "test.mkv"

        structure = FileStructureManager.create_structure(video_file)

        assert structure.extracted_dir.exists()
        assert structure.extracted_dir.is_dir()

    def test_get_extracted_dir(self, tmp_path):
        """Test get_extracted_dir()."""
        recording_dir = tmp_path / "test_recording"
        video_file = recording_dir / "test.mkv"

        extracted_dir = FileStructureManager.get_extracted_dir(video_file)

        assert extracted_dir == recording_dir / "extracted"

    def test_get_metadata_file(self, tmp_path):
        """Test get_metadata_file()."""
        recording_dir = tmp_path / "test_recording"
        video_file = recording_dir / "test.mkv"

        metadata_file = FileStructureManager.get_metadata_file(video_file)

        assert metadata_file == recording_dir / "metadata.json"

    def test_create_recording_directory_name(self, tmp_path):
        """Test create_recording_directory_name()."""
        video_file = tmp_path / "test_recording.mkv"

        dir_name = FileStructureManager.create_recording_directory_name(video_file)

        assert dir_name == "test_recording"

    def test_find_recording_structure_found(self, tmp_path):
        """Test find_recording_structure() - struktura znaleziona."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()

        video_file = recording_dir / "test.mkv"
        video_file.touch()

        metadata_file = recording_dir / "metadata.json"
        metadata_file.write_text('{"test": "data"}')

        extracted_dir = recording_dir / "extracted"
        extracted_dir.mkdir()

        structure = FileStructureManager.find_recording_structure(recording_dir)

        assert structure is not None
        assert structure.recording_dir == recording_dir
        assert structure.video_file == video_file
        assert structure.metadata_file == metadata_file
        assert structure.extracted_dir == extracted_dir

    def test_find_recording_structure_no_metadata(self, tmp_path):
        """Test find_recording_structure() - brak metadata.json."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()

        video_file = recording_dir / "test.mkv"
        video_file.touch()

        structure = FileStructureManager.find_recording_structure(recording_dir)

        assert structure is None

    def test_find_recording_structure_no_video(self, tmp_path):
        """Test find_recording_structure() - brak pliku wideo."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()

        metadata_file = recording_dir / "metadata.json"
        metadata_file.write_text('{"test": "data"}')

        structure = FileStructureManager.find_recording_structure(recording_dir)

        assert structure is None

    def test_find_recording_structure_nonexistent_dir(self, tmp_path):
        """Test find_recording_structure() - katalog nie istnieje."""
        nonexistent_dir = tmp_path / "nonexistent"

        structure = FileStructureManager.find_recording_structure(nonexistent_dir)

        assert structure is None

    def test_find_recording_structure_multiple_video_files(self, tmp_path):
        """Test find_recording_structure() - wiele plików wideo."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()

        video_file1 = recording_dir / "test1.mkv"
        video_file1.touch()

        video_file2 = recording_dir / "test2.mp4"
        video_file2.touch()

        metadata_file = recording_dir / "metadata.json"
        metadata_file.write_text('{"test": "data"}')

        extracted_dir = recording_dir / "extracted"
        extracted_dir.mkdir()

        structure = FileStructureManager.find_recording_structure(recording_dir)

        assert structure is not None
        # Powinien znaleźć jeden z plików wideo
        assert structure.video_file in [video_file1, video_file2]

    def test_ensure_extracted_dir(self, tmp_path):
        """Test ensure_extracted_dir()."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()
        video_file = recording_dir / "test.mkv"

        extracted_dir = FileStructureManager.ensure_extracted_dir(video_file)

        assert extracted_dir.exists()
        assert extracted_dir.is_dir()
        assert extracted_dir == recording_dir / "extracted"

    def test_ensure_extracted_dir_already_exists(self, tmp_path):
        """Test ensure_extracted_dir() gdy katalog już istnieje."""
        recording_dir = tmp_path / "test_recording"
        recording_dir.mkdir()
        video_file = recording_dir / "test.mkv"

        # Utwórz katalog extracted
        existing_extracted = recording_dir / "extracted"
        existing_extracted.mkdir()

        extracted_dir = FileStructureManager.ensure_extracted_dir(video_file)

        assert extracted_dir.exists()
        assert extracted_dir.is_dir()
        assert extracted_dir == existing_extracted
