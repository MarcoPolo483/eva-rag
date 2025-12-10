"""Tests for folder loader."""
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from eva_rag.loaders.base import ExtractedDocument
from eva_rag.loaders.folder_loader import FolderLoader


class TestFolderLoader:
    """Test suite for FolderLoader."""
    
    @pytest.fixture
    def temp_folder(self, tmp_path):
        """Create temporary folder structure for testing."""
        # Create test files
        (tmp_path / "test1.txt").write_text("Content of test1")
        (tmp_path / "test2.txt").write_text("Content of test2")
        (tmp_path / "test.html").write_text("<html><body>HTML content</body></html>")
        
        # Create subfolder
        subfolder = tmp_path / "subfolder"
        subfolder.mkdir()
        (subfolder / "nested.txt").write_text("Nested content")
        
        # Create asset folder (should be skipped)
        assets = tmp_path / "assets_files"
        assets.mkdir()
        (assets / "style.css").write_text("body { color: red; }")
        (assets / "script.js").write_text("console.log('test');")
        
        return tmp_path
    
    def test_load_single_folder(self, temp_folder):
        """Test loading files from single folder (non-recursive)."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=False
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            # Mock loader to return simple documents
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # Should only load files from root folder (not subfolder)
            assert len(docs) >= 2  # At least test1.txt and test2.txt
            assert all(doc.metadata.get("folder_loader") is True for doc in docs)
    
    def test_load_recursive(self, temp_folder):
        """Test recursive folder loading."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=True
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # Should load files from root and subfolder
            assert len(docs) >= 3  # test1.txt, test2.txt, nested.txt
            
            # Check that nested file was found
            relative_paths = [doc.metadata.get("relative_path") for doc in docs]
            assert any("subfolder" in str(path) for path in relative_paths)
    
    def test_skip_asset_folders(self, temp_folder):
        """Test that asset folders are skipped."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=True
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # Check that CSS/JS files from assets_files were skipped
            file_names = [doc.metadata.get("file_name") for doc in docs]
            assert "style.css" not in file_names
            assert "script.js" not in file_names
    
    def test_include_patterns(self, temp_folder):
        """Test filtering with include patterns."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=False,
            include_patterns=["*.txt"]  # Only .txt files
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # Should only load .txt files
            file_names = [doc.metadata.get("file_name") for doc in docs]
            assert all(name.endswith(".txt") for name in file_names if name)
            assert "test.html" not in file_names
    
    def test_max_depth(self, temp_folder):
        """Test maximum recursion depth limit."""
        # Create deeper nesting
        deep = temp_folder / "level1" / "level2" / "level3"
        deep.mkdir(parents=True)
        (deep / "deep.txt").write_text("Deep content")
        
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=True,
            max_depth=2  # Only go 2 levels deep
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # deep.txt should not be loaded (too deep)
            relative_paths = [str(doc.metadata.get("relative_path")) for doc in docs]
            assert not any("level3" in path for path in relative_paths)
    
    def test_continue_on_error(self, temp_folder):
        """Test error handling with continue_on_error=True."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=False,
            continue_on_error=True
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            # First file succeeds, second fails, third succeeds
            mock_instance = MagicMock()
            mock_instance.load_from_stream.side_effect = [
                ExtractedDocument(text="Success 1", metadata={}, page_count=1),
                Exception("Load error"),
                ExtractedDocument(text="Success 2", metadata={}, page_count=1),
            ]
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # Should have 2 successful loads despite 1 failure
            assert len(docs) >= 2
            assert len(loader.progress["failures"]) >= 1
    
    def test_stop_on_error(self, temp_folder):
        """Test error handling with continue_on_error=False."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=False,
            continue_on_error=False
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.side_effect = Exception("Load error")
            mock_loader.return_value = mock_instance
            
            # Should raise exception
            with pytest.raises(Exception, match="Load error"):
                loader.load_all()
    
    def test_progress_tracking(self, temp_folder):
        """Test progress tracking during loading."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=False
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            progress = loader.progress
            assert progress["total_files"] > 0
            assert progress["processed_files"] == len(docs)
            assert progress["success_rate"] > 0
            assert isinstance(progress["failures"], list)
    
    def test_metadata_enrichment(self, temp_folder):
        """Test that documents are enriched with folder metadata."""
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=True
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # Check metadata fields
            for doc in docs:
                assert "source_file" in doc.metadata
                assert "relative_path" in doc.metadata
                assert "file_name" in doc.metadata
                assert "file_size" in doc.metadata
                assert doc.metadata["folder_loader"] is True
    
    def test_folder_not_exists(self):
        """Test error when folder doesn't exist."""
        loader = FolderLoader(folder_path="nonexistent_folder")
        
        with pytest.raises(ValueError, match="does not exist"):
            loader.load_all()
    
    def test_path_not_directory(self, temp_folder):
        """Test error when path is not a directory."""
        file_path = temp_folder / "test1.txt"
        loader = FolderLoader(folder_path=file_path)
        
        with pytest.raises(ValueError, match="not a directory"):
            loader.load_all()
    
    def test_folder_path_not_set(self):
        """Test error when folder_path is not set."""
        loader = FolderLoader()
        
        with pytest.raises(ValueError, match="folder_path must be set"):
            loader.load_all()
    
    def test_load_from_stream_not_supported(self):
        """Test that load_from_stream raises NotImplementedError."""
        loader = FolderLoader()
        stream = io.BytesIO(b"test")
        
        with pytest.raises(NotImplementedError):
            loader.load_from_stream(stream)
    
    def test_custom_skip_patterns(self, temp_folder):
        """Test adding custom skip patterns."""
        (temp_folder / "backup.bak").write_text("Backup content")
        
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=False,
            skip_patterns=["*.bak"]  # Skip backup files
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_all()
            
            # backup.bak should be skipped
            file_names = [doc.metadata.get("file_name") for doc in docs]
            assert "backup.bak" not in file_names
    
    def test_load_from_folder_method(self, temp_folder):
        """Test convenience method load_from_folder."""
        loader = FolderLoader()
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            mock_instance = MagicMock()
            mock_instance.load_from_stream.return_value = ExtractedDocument(
                text="Test content",
                metadata={"loader": "MockLoader"},
                page_count=1
            )
            mock_loader.return_value = mock_instance
            
            docs = loader.load_from_folder(temp_folder)
            
            assert len(docs) > 0
            assert loader.folder_path == temp_folder
    
    def test_unsupported_file_types_skipped(self, temp_folder):
        """Test that unsupported file types are logged and skipped."""
        # Create unsupported file
        (temp_folder / "data.unknown").write_text("Unknown content")
        
        loader = FolderLoader(
            folder_path=temp_folder,
            recursive=False
        )
        
        with patch('eva_rag.loaders.factory.LoaderFactory.get_loader') as mock_loader:
            # Raise ValueError for unsupported extension
            mock_loader.side_effect = ValueError("Unsupported file extension")
            
            docs = loader.load_all()
            
            # Should return empty list (all files unsupported)
            assert len(docs) == 0
