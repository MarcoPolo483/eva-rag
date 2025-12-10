"""Folder loader for recursive document ingestion."""
import logging
from pathlib import Path
from typing import Any, BinaryIO, Optional

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument
from eva_rag.loaders.factory import LoaderFactory

logger = logging.getLogger(__name__)


class FolderLoader(DocumentLoader):
    """
    Loader for recursively processing folders and subfolders.
    
    Features:
    - Recursive directory traversal
    - Automatic file type detection via LoaderFactory
    - Progress tracking (processed/total files)
    - Error handling (log failures, continue processing)
    - Filtering to skip asset folders (CSS, JS, images, fonts)
    - Support for include/exclude patterns
    
    Example:
        >>> loader = FolderLoader(
        ...     folder_path="data/jp",
        ...     recursive=True,
        ...     skip_patterns=["*_files", "*.css", "*.js"]
        ... )
        >>> documents = loader.load_all()
        >>> print(f"Loaded {len(documents)} documents")
    """
    
    # Default patterns to skip (asset files)
    DEFAULT_SKIP_PATTERNS = [
        "*_files",      # Browser-saved asset folders
        "*.css",        # Stylesheets
        "*.js",         # JavaScript
        "*.min.js",     # Minified JS
        "*.min.css",    # Minified CSS
        "*.png",        # Images
        "*.jpg",
        "*.jpeg",
        "*.gif",
        "*.svg",
        "*.ico",
        "*.woff",       # Fonts
        "*.woff2",
        "*.ttf",
        "*.eot",
        "*.map",        # Source maps
        ".git",         # Version control
        ".svn",
        "__pycache__",  # Python cache
        "node_modules", # Node.js modules
    ]
    
    def __init__(
        self,
        folder_path: Optional[str | Path] = None,
        recursive: bool = True,
        max_depth: Optional[int] = None,
        include_patterns: Optional[list[str]] = None,
        skip_patterns: Optional[list[str]] = None,
        continue_on_error: bool = True,
    ):
        """
        Initialize folder loader.
        
        Args:
            folder_path: Path to folder to process (can be set later)
            recursive: Whether to traverse subfolders
            max_depth: Maximum recursion depth (None = unlimited)
            include_patterns: File patterns to include (e.g., ["*.html", "*.xml"])
            skip_patterns: Additional patterns to skip beyond defaults
            continue_on_error: Whether to continue on file load errors
        """
        self.folder_path = Path(folder_path) if folder_path else None
        self.recursive = recursive
        self.max_depth = max_depth
        self.include_patterns = include_patterns
        self.skip_patterns = self.DEFAULT_SKIP_PATTERNS.copy()
        if skip_patterns:
            self.skip_patterns.extend(skip_patterns)
        self.continue_on_error = continue_on_error
        
        # Tracking
        self._processed_files = 0
        self._total_files = 0
        self._failed_files: list[tuple[Path, str]] = []
    
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Not implemented for folder loader.
        
        Use load_all() or load_from_folder() instead.
        """
        raise NotImplementedError(
            "FolderLoader does not support single file loading. "
            "Use load_all() or load_from_folder() instead."
        )
    
    def load_from_stream(self, stream: BinaryIO) -> ExtractedDocument:
        """
        Not implemented for folder loader.
        
        Use load_all() or load_from_folder() instead.
        """
        raise NotImplementedError(
            "FolderLoader does not support stream loading. "
            "Use load_all() or load_from_folder() instead."
        )
    
    def load_from_folder(self, folder_path: str | Path) -> list[ExtractedDocument]:
        """
        Load all documents from folder.
        
        Args:
            folder_path: Path to folder
            
        Returns:
            List of extracted documents
        """
        self.folder_path = Path(folder_path)
        return self.load_all()
    
    def load_all(self) -> list[ExtractedDocument]:
        """
        Load all documents from configured folder.
        
        Returns:
            List of extracted documents
            
        Raises:
            ValueError: If folder_path not set or doesn't exist
        """
        if not self.folder_path:
            raise ValueError("folder_path must be set before calling load_all()")
        
        if not self.folder_path.exists():
            raise ValueError(f"Folder does not exist: {self.folder_path}")
        
        if not self.folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.folder_path}")
        
        # Reset tracking
        self._processed_files = 0
        self._total_files = 0
        self._failed_files = []
        
        # Collect all files first for progress tracking
        all_files = self._collect_files()
        self._total_files = len(all_files)
        
        logger.info(f"Found {self._total_files} files to process in {self.folder_path}")
        
        # Process files
        documents: list[ExtractedDocument] = []
        
        for file_path in all_files:
            try:
                doc = self._load_file(file_path)
                if doc:
                    documents.append(doc)
                    self._processed_files += 1
                    
                    if self._processed_files % 10 == 0:
                        logger.info(
                            f"Progress: {self._processed_files}/{self._total_files} files processed"
                        )
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                self._failed_files.append((file_path, error_msg))
                logger.error(f"Failed to load {file_path}: {error_msg}")
                
                if not self.continue_on_error:
                    raise
        
        logger.info(
            f"Completed: {self._processed_files}/{self._total_files} files processed, "
            f"{len(self._failed_files)} failures"
        )
        
        return documents
    
    def _collect_files(self) -> list[Path]:
        """
        Collect all files to process based on patterns and depth.
        
        Returns:
            List of file paths to process
        """
        files: list[Path] = []
        
        if self.recursive:
            files = self._collect_recursive(self.folder_path, depth=0)
        else:
            # Only direct children
            for path in self.folder_path.iterdir():
                if path.is_file() and not self._should_skip(path):
                    if self._matches_include_patterns(path):
                        files.append(path)
        
        return sorted(files)  # Sort for consistent ordering
    
    def _collect_recursive(self, folder: Path, depth: int) -> list[Path]:
        """
        Recursively collect files from folder.
        
        Args:
            folder: Current folder
            depth: Current recursion depth
            
        Returns:
            List of file paths
        """
        files: list[Path] = []
        
        # Check depth limit
        if self.max_depth is not None and depth >= self.max_depth:
            return files
        
        try:
            for path in folder.iterdir():
                # Skip hidden files and folders
                if path.name.startswith('.'):
                    continue
                
                if path.is_dir():
                    # Skip excluded folders
                    if self._should_skip(path):
                        logger.debug(f"Skipping folder: {path}")
                        continue
                    
                    # Recurse into subfolder
                    files.extend(self._collect_recursive(path, depth + 1))
                
                elif path.is_file():
                    # Check if file should be processed
                    if not self._should_skip(path):
                        if self._matches_include_patterns(path):
                            files.append(path)
        except PermissionError:
            logger.warning(f"Permission denied accessing: {folder}")
        
        return files
    
    def _should_skip(self, path: Path) -> bool:
        """
        Check if path should be skipped based on patterns.
        
        Args:
            path: File or folder path
            
        Returns:
            True if should skip
        """
        for pattern in self.skip_patterns:
            if path.match(pattern):
                return True
        return False
    
    def _matches_include_patterns(self, path: Path) -> bool:
        """
        Check if file matches include patterns.
        
        Args:
            path: File path
            
        Returns:
            True if matches (or no patterns specified)
        """
        if not self.include_patterns:
            # No patterns = include everything
            return True
        
        for pattern in self.include_patterns:
            if path.match(pattern):
                return True
        return False
    
    def _load_file(self, file_path: Path) -> Optional[ExtractedDocument]:
        """
        Load document from file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted document or None if loader not available
        """
        try:
            # Get appropriate loader
            loader = LoaderFactory.get_loader(str(file_path))
        except ValueError as e:
            logger.debug(f"Skipping unsupported file: {file_path} ({e})")
            return None
        
        # Load document
        with open(file_path, "rb") as f:
            doc = loader.load_from_stream(f)
        
        # Add folder-specific metadata
        doc.metadata["source_file"] = str(file_path)
        doc.metadata["relative_path"] = str(file_path.relative_to(self.folder_path))
        doc.metadata["file_name"] = file_path.name
        doc.metadata["file_size"] = file_path.stat().st_size
        doc.metadata["folder_loader"] = True
        
        return doc
    
    @property
    def progress(self) -> dict[str, Any]:
        """
        Get current progress statistics.
        
        Returns:
            Progress dictionary with counts and failures
        """
        return {
            "total_files": self._total_files,
            "processed_files": self._processed_files,
            "failed_files": len(self._failed_files),
            "success_rate": (
                self._processed_files / self._total_files * 100
                if self._total_files > 0
                else 0
            ),
            "failures": [
                {"file": str(path), "error": error}
                for path, error in self._failed_files
            ],
        }
