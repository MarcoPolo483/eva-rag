"""HTML document loader with advanced table extraction."""
from io import BytesIO
from typing import BinaryIO

from bs4 import BeautifulSoup, NavigableString, Tag

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument


class HTMLLoader(DocumentLoader):
    """Load and extract text from HTML files with structured table preservation."""
    
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Extract text and tables from HTML file.
        
        Args:
            file: Binary HTML file object
            filename: Original filename
            
        Returns:
            Extracted document with text and structured tables
            
        Raises:
            ValueError: If HTML is invalid or empty
        """
        try:
            # Read HTML
            html_bytes = file.read()
            html_content = html_bytes.decode('utf-8', errors='ignore')
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title from <title> or <h1>
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            
            # Extract meta description BEFORE removing meta tags
            metadata = {}
            if title:
                metadata["title"] = title
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                metadata["description"] = meta_desc['content']
            
            # NOW remove script, style and meta elements
            for element in soup(['script', 'style', 'meta', 'link']):
                element.decompose()
            
            # Extract main content with special table handling
            content_parts: list[str] = []
            
            # Process body or entire document
            main_content = soup.find('body') or soup
            
            # Extract structured content
            for element in main_content.descendants:
                if isinstance(element, NavigableString):
                    continue
                    
                if not isinstance(element, Tag):
                    continue
                
                # Handle headings
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(element.name[1])
                    heading_text = element.get_text(strip=True)
                    if heading_text:
                        content_parts.append(f"\n{'#' * level} {heading_text}\n")
                
                # Handle paragraphs
                elif element.name == 'p':
                    para_text = element.get_text(strip=True)
                    if para_text:
                        content_parts.append(f"{para_text}\n")
                
                # Handle lists
                elif element.name in ['ul', 'ol']:
                    list_items = element.find_all('li', recursive=False)
                    for item in list_items:
                        item_text = item.get_text(strip=True)
                        if item_text:
                            prefix = "•" if element.name == 'ul' else f"{list_items.index(item) + 1}."
                            content_parts.append(f"  {prefix} {item_text}\n")
                
                # Handle tables with structured format
                elif element.name == 'table':
                    table_md = self._extract_table_markdown(element)
                    if table_md:
                        content_parts.append(f"\n{table_md}\n")
            
            full_text = "".join(content_parts).strip()
            
            if not full_text:
                raise ValueError(f"HTML file '{filename}' contains no extractable text")
            
            return ExtractedDocument(
                text=full_text,
                page_count=1,  # HTML is single-page by nature
                metadata=metadata,
            )
            
        except Exception as e:
            raise ValueError(f"Failed to load HTML '{filename}': {str(e)}") from e
    
    def _extract_table_markdown(self, table: Tag) -> str:
        """
        Extract table data in markdown format for better readability.
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            Markdown-formatted table string
        """
        rows: list[list[str]] = []
        
        # Find all rows (handle both direct <tr> and nested in <thead>/<tbody>)
        all_rows = table.find_all('tr')
        
        for row in all_rows:
            cells: list[str] = []
            
            # Get all cells (both <th> and <td>)
            for cell in row.find_all(['th', 'td']):
                cell_text = cell.get_text(strip=True)
                
                # Handle colspan
                colspan = int(cell.get('colspan', 1))
                cells.append(cell_text)
                
                # Add empty cells for colspan > 1
                for _ in range(colspan - 1):
                    cells.append("")
            
            if cells:
                rows.append(cells)
        
        if not rows:
            return ""
        
        # Build markdown table
        md_lines: list[str] = []
        
        # Assume first row is header
        if len(rows) > 0:
            header = rows[0]
            max_cols = max(len(row) for row in rows)
            
            # Pad header to max columns
            while len(header) < max_cols:
                header.append("")
            
            # Header row
            md_lines.append("| " + " | ".join(header) + " |")
            
            # Separator row
            md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
            
            # Data rows
            for row in rows[1:]:
                # Pad row to match header length
                while len(row) < len(header):
                    row.append("")
                
                md_lines.append("| " + " | ".join(row) + " |")
        
        return "\n".join(md_lines)
