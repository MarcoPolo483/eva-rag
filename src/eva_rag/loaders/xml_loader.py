"""XML document loader with automatic schema detection."""
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, BinaryIO, Optional

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument


class XMLLoader(DocumentLoader):
    """
    Loader for XML documents with automatic schema detection.
    
    Features:
    - Automatic schema detection by analyzing document structure
    - Namespace-aware parsing
    - Handles nested elements and attributes
    - Extracts text content from CDATA sections
    - Bilingual content support (EN/FR)
    - Generates schema for reference
    
    Example:
        >>> loader = XMLLoader()
        >>> with open("knowledge_articles.xml", "rb") as f:
        ...     doc = loader.load_from_stream(f)
        >>> print(doc.text)
        >>> print(doc.metadata["detected_schema"])
    """
    
    def __init__(self, detect_schema: bool = True):
        """
        Initialize XML loader.
        
        Args:
            detect_schema: Whether to auto-detect schema structure
        """
        self.detect_schema = detect_schema
        self._schema: Optional[dict[str, Any]] = None
    
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Load and extract text from XML document.
        
        Args:
            file: Binary file object
            filename: Original filename
            
        Returns:
            Extracted document with text and metadata
        """
        return self.load_from_stream(file)
    
    def load_from_stream(self, stream: BinaryIO) -> ExtractedDocument:
        """
        Load XML document from stream.
        
        Args:
            stream: Binary stream of XML file
            
        Returns:
            Extracted document with text and metadata
        """
        content = stream.read()
        
        try:
            # Parse XML with namespace awareness
            root = ET.fromstring(content)
        except ET.ParseError as e:
            return ExtractedDocument(
                text="",
                page_count=0,
                metadata={
                    "error": f"XML parse error: {str(e)}",
                    "loader": "XMLLoader"
                }
            )
        
        # Detect schema if enabled
        if self.detect_schema:
            self._schema = self._detect_schema(root)
        
        # Extract text and metadata
        text = self._extract_text(root)
        metadata = self._extract_metadata(root)
        
        if self._schema:
            metadata["detected_schema"] = self._schema
        
        metadata["loader"] = "XMLLoader"
        metadata["root_tag"] = self._strip_namespace(root.tag)
        
        return ExtractedDocument(
            text=text,
            page_count=1,  # XML documents don't have pages
            metadata=metadata
        )
    
    def _detect_schema(self, root: ET.Element) -> dict[str, Any]:
        """
        Auto-detect XML schema by analyzing structure.
        
        Args:
            root: Root XML element
            
        Returns:
            Schema dictionary with element frequency and structure
        """
        schema = {
            "root_element": self._strip_namespace(root.tag),
            "child_elements": {},
            "repeating_elements": [],
            "common_attributes": [],
            "structure_type": "flat",  # flat, nested, or mixed
        }
        
        # Analyze all elements in document
        element_counts: Counter = Counter()
        all_attributes: Counter = Counter()
        depth_map: dict[str, int] = {}
        
        for elem in root.iter():
            tag = self._strip_namespace(elem.tag)
            element_counts[tag] += 1
            
            # Track attributes
            for attr in elem.attrib.keys():
                all_attributes[self._strip_namespace(attr)] += 1
            
            # Track depth
            depth = self._get_element_depth(root, elem)
            depth_map[tag] = max(depth_map.get(tag, 0), depth)
        
        # Identify repeating elements (appearing more than once)
        schema["repeating_elements"] = [
            tag for tag, count in element_counts.items() if count > 1
        ]
        
        # Identify common attributes (appearing in multiple elements)
        schema["common_attributes"] = [
            attr for attr, count in all_attributes.most_common(10)
        ]
        
        # Determine structure type
        max_depth = max(depth_map.values()) if depth_map else 0
        if max_depth <= 2:
            schema["structure_type"] = "flat"
        elif max_depth <= 4:
            schema["structure_type"] = "nested"
        else:
            schema["structure_type"] = "deep_nested"
        
        # Build child element map
        for child in root:
            child_tag = self._strip_namespace(child.tag)
            if child_tag not in schema["child_elements"]:
                schema["child_elements"][child_tag] = {
                    "count": 0,
                    "has_attributes": False,
                    "has_text": False,
                    "has_children": False,
                }
            
            schema["child_elements"][child_tag]["count"] += 1
            schema["child_elements"][child_tag]["has_attributes"] = bool(child.attrib)
            schema["child_elements"][child_tag]["has_text"] = bool(child.text and child.text.strip())
            schema["child_elements"][child_tag]["has_children"] = len(list(child)) > 0
        
        return schema
    
    def _extract_text(self, root: ET.Element) -> str:
        """
        Extract all text content from XML tree.
        
        Args:
            root: Root XML element
            
        Returns:
            Concatenated text content
        """
        sections = []
        
        # Check if this is a structured document with repeating elements
        if self._schema and self._schema["repeating_elements"]:
            # Process structured documents (e.g., knowledge articles)
            main_element = self._schema["repeating_elements"][0] if self._schema["repeating_elements"] else None
            
            if main_element:
                for elem in root.iter(main_element):
                    section = self._extract_element_text(elem)
                    if section.strip():
                        sections.append(section)
            else:
                # Fallback to root extraction
                sections.append(self._extract_element_text(root))
        else:
            # Simple extraction for unstructured XML
            sections.append(self._extract_element_text(root))
        
        return "\n\n".join(sections)
    
    def _extract_element_text(self, element: ET.Element) -> str:
        """
        Extract text from a single element and its children.
        
        Args:
            element: XML element
            
        Returns:
            Formatted text content
        """
        parts = []
        
        # Add element tag as heading if it looks like a document section
        tag = self._strip_namespace(element.tag)
        if tag in ["document", "article", "section", "record"]:
            parts.append(f"## {tag.title()}\n")
        
        # Extract attributes as metadata fields
        if element.attrib:
            for key, value in element.attrib.items():
                clean_key = self._strip_namespace(key).replace("_", " ").title()
                parts.append(f"**{clean_key}:** {value}")
        
        # Extract direct text
        if element.text and element.text.strip():
            parts.append(element.text.strip())
        
        # Extract text from children
        for child in element:
            child_tag = self._strip_namespace(child.tag)
            child_text = child.text.strip() if child.text else ""
            
            # Format based on child structure
            if len(list(child)) > 0:
                # Child has nested children - recurse
                parts.append(self._extract_element_text(child))
            elif child_text:
                # Child has text - format as field
                clean_tag = child_tag.replace("_", " ").title()
                
                # Long text fields (likely content)
                if len(child_text) > 200 or child_tag.lower() in ["content", "description", "text", "body"]:
                    parts.append(f"\n### {clean_tag}\n")
                    parts.append(child_text)
                else:
                    # Short fields (likely metadata)
                    parts.append(f"**{clean_tag}:** {child_text}")
            
            # Extract tail text (text after closing tag)
            if child.tail and child.tail.strip():
                parts.append(child.tail.strip())
        
        return "\n".join(parts)
    
    def _extract_metadata(self, root: ET.Element) -> dict[str, Any]:
        """
        Extract metadata from XML document.
        
        Args:
            root: Root XML element
            
        Returns:
            Metadata dictionary
        """
        metadata: dict[str, Any] = {}
        
        # Extract root attributes
        for key, value in root.attrib.items():
            clean_key = self._strip_namespace(key)
            metadata[f"root_{clean_key}"] = value
        
        # Count document sections
        if self._schema and self._schema["repeating_elements"]:
            main_element = self._schema["repeating_elements"][0]
            count = sum(1 for _ in root.iter(main_element))
            metadata["document_count"] = count
            metadata["main_element"] = main_element
        
        # Detect languages (simple heuristic)
        languages = set()
        for elem in root.iter():
            if "lang" in elem.attrib:
                languages.add(elem.attrib["lang"])
            # Check for FR/EN indicators in tags or attributes
            tag = self._strip_namespace(elem.tag).lower()
            if "fr" in tag or "_fr" in tag:
                languages.add("fr")
            elif "en" in tag or "_en" in tag:
                languages.add("en")
        
        if languages:
            metadata["languages"] = sorted(languages)
        
        # Document statistics
        total_elements = sum(1 for _ in root.iter())
        metadata["total_elements"] = total_elements
        
        return metadata
    
    def _strip_namespace(self, tag: str) -> str:
        """
        Remove XML namespace from tag name.
        
        Args:
            tag: Tag name potentially with namespace
            
        Returns:
            Clean tag name without namespace
        """
        # Remove namespace like {http://example.com}tag -> tag
        return re.sub(r'\{[^}]+\}', '', tag)
    
    def _get_element_depth(self, root: ET.Element, element: ET.Element) -> int:
        """
        Calculate depth of element in tree.
        
        Args:
            root: Root element
            element: Element to find depth for
            
        Returns:
            Depth level (0 for root)
        """
        if element == root:
            return 0
        
        # Build path from root to element
        def find_depth(current, target, depth=0):
            if current == target:
                return depth
            for child in current:
                result = find_depth(child, target, depth + 1)
                if result is not None:
                    return result
            return None
        
        result = find_depth(root, element)
        return result if result is not None else 0
    
    @property
    def detected_schema(self) -> Optional[dict[str, Any]]:
        """
        Get detected schema if available.
        
        Returns:
            Schema dictionary or None
        """
        return self._schema
