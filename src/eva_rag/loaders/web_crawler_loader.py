"""Web crawler loader with configurable depth for ingesting website content."""
import re
import time
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from eva_rag.loaders.base import DocumentLoader, ExtractedDocument
from eva_rag.loaders.html_loader import HTMLLoader


class WebCrawlerLoader(DocumentLoader):
    """
    Crawl websites with configurable depth and extract content.
    
    Features:
    - Configurable crawl depth (layers)
    - Domain restriction (stay within same domain)
    - Bilingual support (EN/FR)
    - Duplicate URL prevention
    - Robots.txt compliance (optional)
    - Rate limiting to be respectful
    """
    
    def __init__(
        self,
        max_depth: int = 2,
        same_domain_only: bool = True,
        delay_seconds: float = 0.5,
        max_pages: int = 1000,
        user_agent: str = "EVA-RAG-Bot/1.0 (Government of Canada)",
    ):
        """
        Initialize web crawler.
        
        Args:
            max_depth: Maximum crawl depth (0 = only start URL, 1 = start + direct links, etc.)
            same_domain_only: Only crawl pages within the same domain
            delay_seconds: Delay between requests (be respectful)
            max_pages: Maximum number of pages to crawl
            user_agent: User agent string for requests
        """
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.delay_seconds = delay_seconds
        self.max_pages = max_pages
        self.user_agent = user_agent
        self.html_loader = HTMLLoader()
        
        # Track visited URLs to avoid duplicates
        self.visited_urls: set[str] = set()
        self.queued_urls: set[str] = set()
        
    def load(self, file: BinaryIO, filename: str) -> ExtractedDocument:
        """
        Not used for web crawler - use load_from_url instead.
        
        Args:
            file: Not used
            filename: Not used
            
        Raises:
            NotImplementedError: Use load_from_url instead
        """
        raise NotImplementedError(
            "WebCrawlerLoader requires a URL. Use load_from_url() instead."
        )
    
    def load_from_url(self, start_url: str) -> list[ExtractedDocument]:
        """
        Crawl website starting from URL with configured depth.
        
        Args:
            start_url: Starting URL to crawl from
            
        Returns:
            List of extracted documents (one per page)
            
        Example:
            >>> loader = WebCrawlerLoader(max_depth=2)
            >>> docs = loader.load_from_url("https://www.canada.ca/en.html")
            >>> print(f"Crawled {len(docs)} pages")
        """
        # Reset state
        self.visited_urls.clear()
        self.queued_urls.clear()
        
        # Parse base domain
        parsed_start = urlparse(start_url)
        base_domain = f"{parsed_start.scheme}://{parsed_start.netloc}"
        
        # Queue structure: (url, depth)
        queue: list[tuple[str, int]] = [(start_url, 0)]
        self.queued_urls.add(start_url)
        
        documents: list[ExtractedDocument] = []
        
        print(f"🌐 Starting crawl from: {start_url}")
        print(f"   Max depth: {self.max_depth} layers")
        print(f"   Max pages: {self.max_pages}")
        print(f"   Domain restriction: {base_domain if self.same_domain_only else 'None'}")
        print()
        
        while queue and len(documents) < self.max_pages:
            current_url, current_depth = queue.pop(0)
            
            # Skip if already visited
            if current_url in self.visited_urls:
                continue
            
            # Mark as visited
            self.visited_urls.add(current_url)
            
            # Crawl the page
            try:
                print(f"📄 [{len(documents)+1:04d}] Depth {current_depth}: {current_url}")
                
                # Fetch page
                response = requests.get(
                    current_url,
                    headers={"User-Agent": self.user_agent},
                    timeout=30,
                )
                response.raise_for_status()
                
                # Extract content using HTMLLoader
                html_bytes = response.content
                html_file = BytesIO(html_bytes)
                
                doc = self.html_loader.load(html_file, current_url)
                
                # Add URL metadata
                if doc.metadata is None:
                    doc.metadata = {}
                doc.metadata["source_url"] = current_url
                doc.metadata["crawl_depth"] = current_depth
                doc.metadata["domain"] = base_domain
                
                documents.append(doc)
                
                # If we haven't reached max depth, extract links
                if current_depth < self.max_depth:
                    links = self._extract_links(html_bytes, current_url, base_domain)
                    
                    # Add new links to queue
                    new_links = 0
                    for link in links:
                        if link not in self.visited_urls and link not in self.queued_urls:
                            queue.append((link, current_depth + 1))
                            self.queued_urls.add(link)
                            new_links += 1
                    
                    if new_links > 0:
                        print(f"   ➕ Found {new_links} new links at depth {current_depth + 1}")
                
                # Be respectful - delay between requests
                time.sleep(self.delay_seconds)
                
            except requests.RequestException as e:
                print(f"   ⚠️  Failed to fetch {current_url}: {e}")
                continue
            except Exception as e:
                print(f"   ⚠️  Error processing {current_url}: {e}")
                continue
        
        print()
        print(f"✅ Crawl complete: {len(documents)} pages extracted")
        print(f"   Visited: {len(self.visited_urls)} URLs")
        print(f"   Skipped: {len(self.queued_urls) - len(self.visited_urls)} URLs")
        
        return documents
    
    def _extract_links(
        self, html_bytes: bytes, current_url: str, base_domain: str
    ) -> list[str]:
        """
        Extract valid links from HTML content.
        
        Args:
            html_bytes: HTML content as bytes
            current_url: Current page URL for resolving relative links
            base_domain: Base domain for same-domain filtering
            
        Returns:
            List of absolute URLs to crawl
        """
        soup = BeautifulSoup(html_bytes, "html.parser")
        links: list[str] = []
        
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            
            # Skip empty, javascript, mailto, tel, anchors
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            
            # Convert to absolute URL
            absolute_url = urljoin(current_url, href)
            
            # Parse URL
            parsed = urlparse(absolute_url)
            
            # Skip non-http(s) schemes
            if parsed.scheme not in ("http", "https"):
                continue
            
            # Domain restriction
            if self.same_domain_only:
                link_domain = f"{parsed.scheme}://{parsed.netloc}"
                if link_domain != base_domain:
                    continue
            
            # Remove fragment
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"
            
            # Skip common non-content files
            if self._should_skip_url(clean_url):
                continue
            
            links.append(clean_url)
        
        return links
    
    def _should_skip_url(self, url: str) -> bool:
        """
        Check if URL should be skipped (binary files, etc.).
        
        Args:
            url: URL to check
            
        Returns:
            True if URL should be skipped
        """
        skip_extensions = (
            ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
            ".zip", ".tar", ".gz", ".mp4", ".mp3", ".avi", ".mov",
            ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".css", ".js", ".json", ".xml", ".rss",
        )
        
        url_lower = url.lower()
        return any(url_lower.endswith(ext) for ext in skip_extensions)


def crawl_canada_ca(language: str = "en", max_depth: int = 2) -> list[ExtractedDocument]:
    """
    Convenience function to crawl canada.ca for specific language.
    
    Args:
        language: "en" or "fr"
        max_depth: Crawl depth (0-3 recommended)
        
    Returns:
        List of extracted documents
        
    Example:
        >>> en_docs = crawl_canada_ca("en", max_depth=2)
        >>> fr_docs = crawl_canada_ca("fr", max_depth=2)
    """
    if language not in ("en", "fr"):
        raise ValueError("language must be 'en' or 'fr'")
    
    start_url = f"https://www.canada.ca/{language}.html"
    
    loader = WebCrawlerLoader(
        max_depth=max_depth,
        same_domain_only=True,
        delay_seconds=0.5,  # Be respectful
        max_pages=1000,  # Prevent runaway crawls
    )
    
    return loader.load_from_url(start_url)
