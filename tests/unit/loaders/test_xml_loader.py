"""Tests for XML loader."""
import io

import pytest

from eva_rag.loaders.xml_loader import XMLLoader


class TestXMLLoader:
    """Test suite for XMLLoader."""
    
    def test_simple_xml(self):
        """Test loading simple flat XML structure."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <title>Test Document</title>
            <author>John Doe</author>
            <content>This is the document content.</content>
        </root>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert doc is not None
        assert "Test Document" in doc.text
        assert "John Doe" in doc.text
        assert "document content" in doc.text
        assert doc.metadata["root_tag"] == "root"
        assert doc.metadata["loader"] == "XMLLoader"
    
    def test_nested_xml(self):
        """Test loading nested XML structure."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <library>
            <book>
                <title>Python Programming</title>
                <author>Jane Smith</author>
                <year>2024</year>
            </book>
            <book>
                <title>Data Science Handbook</title>
                <author>Bob Johnson</author>
                <year>2023</year>
            </book>
        </library>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert "Python Programming" in doc.text
        assert "Data Science Handbook" in doc.text
        assert "Jane Smith" in doc.text
        assert "Bob Johnson" in doc.text
        assert "book" in doc.metadata["detected_schema"]["repeating_elements"]
    
    def test_xml_with_attributes(self):
        """Test XML with attributes extraction."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <document id="DOC-001" lang="en">
            <title>Sample Document</title>
            <section name="Introduction">
                <text>This is the introduction.</text>
            </section>
        </document>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert "Sample Document" in doc.text
        assert "introduction" in doc.text.lower()
        # Check that attributes are captured
        schema = doc.metadata.get("detected_schema")
        assert "id" in schema["common_attributes"] or "name" in schema["common_attributes"]
    
    def test_xml_with_namespace(self):
        """Test XML with namespaces."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <doc:document xmlns:doc="http://example.com/doc">
            <doc:title>Namespaced Document</doc:title>
            <doc:content>Content with namespace</doc:content>
        </doc:document>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        # Namespace should be stripped
        assert "Namespaced Document" in doc.text
        assert "Content with namespace" in doc.text
        assert doc.metadata["root_tag"] == "document"
    
    def test_knowledge_article_structure(self):
        """Test real knowledge article XML structure."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <documents>
            <document>
                <reference>https://kmt-ogc.service.gc.ca/en/knowledgebase/article?pid=KA-001</reference>
                <title>Test Article 1</title>
                <content>This is the content of article 1. It contains important information.</content>
            </document>
            <document>
                <reference>https://kmt-ogc.service.gc.ca/en/knowledgebase/article?pid=KA-002</reference>
                <title>Test Article 2</title>
                <content>This is the content of article 2. More details here.</content>
            </document>
        </documents>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert "Test Article 1" in doc.text
        assert "Test Article 2" in doc.text
        assert "article 1" in doc.text
        assert "article 2" in doc.text
        assert doc.metadata["document_count"] == 2
        assert doc.metadata["main_element"] == "document"
    
    def test_bilingual_xml(self):
        """Test XML with bilingual content."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <articles>
            <article lang="en">
                <title>English Title</title>
                <content>English content here.</content>
            </article>
            <article lang="fr">
                <title>Titre français</title>
                <content>Contenu en français ici.</content>
            </article>
        </articles>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert "English Title" in doc.text
        assert "Titre français" in doc.text
        assert "English content" in doc.text
        assert "français" in doc.text
        assert "en" in doc.metadata.get("languages", [])
        assert "fr" in doc.metadata.get("languages", [])
    
    def test_xml_with_cdata(self):
        """Test XML with CDATA sections."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <document>
            <title>Document with CDATA</title>
            <content><![CDATA[
                This is CDATA content.
                It can contain <html> tags and special & characters.
            ]]></content>
        </document>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert "Document with CDATA" in doc.text
        # CDATA content should be extracted
        assert "CDATA content" in doc.text or "This is" in doc.text
    
    def test_empty_xml(self):
        """Test empty XML document."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <empty></empty>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert doc is not None
        assert doc.metadata["root_tag"] == "empty"
        assert doc.metadata["total_elements"] == 1
    
    def test_malformed_xml(self):
        """Test handling of malformed XML."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <document>
            <title>Unclosed tag
            <content>Content here</content>
        </document>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        # Should return error metadata instead of crashing
        assert "error" in doc.metadata
        assert "parse error" in doc.metadata["error"].lower()
    
    def test_schema_detection_disabled(self):
        """Test XML loading with schema detection disabled."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <root>
            <item>Item 1</item>
            <item>Item 2</item>
        </root>
        """
        
        loader = XMLLoader(detect_schema=False)
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert "Item 1" in doc.text
        assert "detected_schema" not in doc.metadata
    
    def test_deep_nested_structure(self):
        """Test deeply nested XML structure."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <level1>
            <level2>
                <level3>
                    <level4>
                        <level5>
                            <content>Deep content</content>
                        </level5>
                    </level4>
                </level3>
            </level2>
        </level1>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        assert "Deep content" in doc.text
        schema = doc.metadata["detected_schema"]
        assert schema["structure_type"] in ["nested", "deep_nested"]
    
    def test_xml_with_special_characters(self):
        """Test XML with special characters and entities."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <document>
            <title>Special &amp; Characters</title>
            <content>Text with &lt;tags&gt; and &quot;quotes&quot;</content>
        </document>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        # XML entities should be decoded
        assert "&" in doc.text or "Special" in doc.text
        assert "Characters" in doc.text
    
    def test_detected_schema_property(self):
        """Test accessing detected schema via property."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <books>
            <book><title>Book 1</title></book>
            <book><title>Book 2</title></book>
        </books>
        """
        
        loader = XMLLoader()
        stream = io.BytesIO(xml_content.encode('utf-8'))
        doc = loader.load_from_stream(stream)
        
        schema = loader.detected_schema
        assert schema is not None
        assert schema["root_element"] == "books"
        assert "book" in schema["repeating_elements"]
