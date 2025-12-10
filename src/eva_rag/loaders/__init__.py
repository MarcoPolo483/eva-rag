"""Document loaders for PDF, DOCX, HTML, TXT, and web crawling."""
from eva_rag.loaders.base import DocumentLoader, ExtractedDocument
from eva_rag.loaders.docx_loader import DOCXLoader
from eva_rag.loaders.factory import LoaderFactory
from eva_rag.loaders.html_loader import HTMLLoader
from eva_rag.loaders.pdf_loader import PDFLoader
from eva_rag.loaders.text_loader import TextLoader
from eva_rag.loaders.web_crawler_loader import WebCrawlerLoader

__all__ = [
    "DocumentLoader",
    "ExtractedDocument",
    "LoaderFactory",
    "PDFLoader",
    "DOCXLoader",
    "HTMLLoader",
    "TextLoader",
    "WebCrawlerLoader",
]
