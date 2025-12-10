"""CSV document loader for large datasets."""
import csv
import io
from pathlib import Path
from typing import Any, BinaryIO, Optional

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument


class CSVLoader(DocumentLoader):
    """
    Loader for CSV (Comma-Separated Values) documents.
    
    Features:
    - Automatic delimiter detection (comma, semicolon, tab, pipe)
    - Encoding detection and handling (UTF-8, Latin-1, CP1252)
    - Large file support with row sampling
    - Header detection and column metadata
    - Statistical summary of numeric columns
    - Markdown table conversion for LLM readability
    
    Optimized for Kaggle employment datasets:
    - Canada Employment Trend Cycle (120MB, 17 columns)
    - Unemployment in Canada by Province (4.5MB, 13 columns)
    
    Example:
        >>> loader = CSVLoader(sample_rows=1000)
        >>> with open("employment_data.csv", "rb") as f:
        ...     doc = loader.load_from_stream(f)
        >>> print(doc.text)  # Markdown table
        >>> print(doc.metadata["column_count"])  # 17
    """
    
    def __init__(
        self,
        sample_rows: Optional[int] = None,
        max_preview_rows: int = 50,
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None,
    ):
        """
        Initialize CSV loader.
        
        Args:
            sample_rows: Max rows to include in text (None = all rows)
            max_preview_rows: Max rows to show in markdown preview
            encoding: Force specific encoding (None = auto-detect)
            delimiter: Force specific delimiter (None = auto-detect)
        """
        self.sample_rows = sample_rows
        self.max_preview_rows = max_preview_rows
        self.encoding = encoding
        self.delimiter = delimiter
    
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Load and extract text from CSV document.
        
        Args:
            file: Binary file object
            filename: Original filename
            
        Returns:
            Extracted document with text and metadata
        """
        return self.load_from_stream(file)
    
    def load_from_stream(self, stream: BinaryIO) -> ExtractedDocument:
        """
        Load CSV document from stream.
        
        Args:
            stream: Binary stream of CSV file
            
        Returns:
            Extracted document with text and metadata
        """
        content = stream.read()
        
        # Detect encoding
        encoding = self._detect_encoding(content)
        
        try:
            text_content = content.decode(encoding)
        except Exception as e:
            return ExtractedDocument(
                text="",
                page_count=0,
                metadata={
                    "error": f"Encoding error: {str(e)}",
                    "loader": "CSVLoader"
                }
            )
        
        # Detect delimiter
        delimiter = self._detect_delimiter(text_content)
        
        # Parse CSV
        reader = csv.DictReader(io.StringIO(text_content), delimiter=delimiter)
        
        try:
            rows = list(reader)
        except csv.Error as e:
            return ExtractedDocument(
                text="",
                page_count=0,
                metadata={
                    "error": f"CSV parse error: {str(e)}",
                    "loader": "CSVLoader"
                }
            )
        
        if not rows:
            return ExtractedDocument(
                text="",
                page_count=0,
                metadata={
                    "error": "Empty CSV file",
                    "loader": "CSVLoader"
                }
            )
        
        # Extract metadata
        columns = list(rows[0].keys())
        total_rows = len(rows)
        
        # Sample rows if needed
        sampled_rows = rows
        if self.sample_rows and total_rows > self.sample_rows:
            # Take first, middle, and last rows for representative sample
            step = total_rows // self.sample_rows
            sampled_rows = rows[::step][:self.sample_rows]
        
        # Generate markdown table
        text = self._generate_markdown(
            columns,
            sampled_rows[:self.max_preview_rows],
            total_rows,
            sampled=len(sampled_rows) < total_rows
        )
        
        # Calculate statistics
        stats = self._calculate_statistics(sampled_rows, columns)
        
        metadata = {
            "loader": "CSVLoader",
            "encoding": encoding,
            "delimiter": delimiter,
            "column_count": len(columns),
            "row_count": total_rows,
            "sampled_rows": len(sampled_rows),
            "columns": columns,
            "statistics": stats,
        }
        
        return ExtractedDocument(
            text=text,
            page_count=1,
            metadata=metadata
        )
    
    def _detect_encoding(self, content: bytes) -> str:
        """
        Detect file encoding.
        
        Args:
            content: Raw bytes
            
        Returns:
            Detected encoding name
        """
        if self.encoding:
            return self.encoding
        
        # Try common encodings
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]:
            try:
                content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        
        # Fallback
        return "utf-8"
    
    def _detect_delimiter(self, text: str) -> str:
        """
        Detect CSV delimiter.
        
        Args:
            text: CSV text content
            
        Returns:
            Detected delimiter
        """
        if self.delimiter:
            return self.delimiter
        
        # Use csv.Sniffer for detection
        try:
            sniffer = csv.Sniffer()
            sample = text[:10000]  # First 10KB
            delimiter = sniffer.sniff(sample).delimiter
            return delimiter
        except:
            # Fallback to comma
            return ","
    
    def _generate_markdown(
        self,
        columns: list[str],
        rows: list[dict],
        total_rows: int,
        sampled: bool
    ) -> str:
        """
        Generate markdown table from CSV data.
        
        Args:
            columns: Column names
            rows: Data rows
            total_rows: Total number of rows
            sampled: Whether data is sampled
            
        Returns:
            Markdown formatted table
        """
        lines = []
        
        # Header
        lines.append("# CSV Data\n")
        
        if sampled:
            lines.append(f"**Note:** Showing {len(rows)} of {total_rows:,} total rows (sampled)\n")
        else:
            lines.append(f"**Total Rows:** {total_rows:,}\n")
        
        lines.append(f"**Columns:** {len(columns)}\n")
        
        # Column list
        lines.append("\n## Columns\n")
        for i, col in enumerate(columns, 1):
            lines.append(f"{i}. `{col}`")
        
        # Data table
        lines.append("\n## Data Preview\n")
        
        # Table header
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"
        lines.append(header)
        lines.append(separator)
        
        # Table rows
        for row in rows:
            values = [str(row.get(col, "")).replace("|", "\\|") for col in columns]
            # Truncate long values
            values = [v[:50] + "..." if len(v) > 50 else v for v in values]
            line = "| " + " | ".join(values) + " |"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _calculate_statistics(
        self,
        rows: list[dict],
        columns: list[str]
    ) -> dict[str, Any]:
        """
        Calculate basic statistics for numeric columns.
        
        Args:
            rows: Data rows
            columns: Column names
            
        Returns:
            Statistics dictionary
        """
        stats: dict[str, Any] = {}
        
        for col in columns:
            values = [row.get(col) for row in rows if row.get(col)]
            
            # Try to detect numeric columns
            numeric_values = []
            for val in values:
                try:
                    numeric_values.append(float(val))
                except (ValueError, TypeError):
                    break
            
            if len(numeric_values) >= len(values) * 0.8:  # 80% numeric
                stats[col] = {
                    "type": "numeric",
                    "min": min(numeric_values) if numeric_values else None,
                    "max": max(numeric_values) if numeric_values else None,
                    "mean": sum(numeric_values) / len(numeric_values) if numeric_values else None,
                }
            else:
                # Categorical column
                unique_values = set(values)
                stats[col] = {
                    "type": "categorical",
                    "unique_count": len(unique_values),
                    "sample_values": list(unique_values)[:5],
                }
        
        return stats
