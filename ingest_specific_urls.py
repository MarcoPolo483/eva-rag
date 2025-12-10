"""
Ingest government programs and services documents.

This script ingests:
1. Employment Equity Act - Federal employment equity program
   - HTML format (EN + FR)
   - PDF format (EN + FR)
   - XML format (EN + FR)
   - Source: laws-lois.justice.gc.ca
2. IT Collective Agreement - Federal public service employment terms
   - HTML format (EN + FR)
   - Source: Treasury Board Secretariat

Category: Programs and Services
Client: Government programs documentation

Usage:
    python ingest_specific_urls.py
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List
import requests

from eva_rag.loaders.html_loader import HTMLLoader
from eva_rag.loaders.pdf_loader import PDFLoader
from eva_rag.loaders.xml_loader import XMLLoader
from eva_rag.loaders.base import ExtractedDocument


class SpecificURLIngester:
    """Ingest specific government documents with format and language variations."""
    
    def __init__(self):
        self.html_loader = HTMLLoader()
        self.pdf_loader = PDFLoader()
        self.xml_loader = XMLLoader()
        
    def download_and_ingest(self, url: str, format_type: str, language: str) -> ExtractedDocument:
        """
        Download and ingest a specific URL.
        
        Args:
            url: URL to download
            format_type: Format (html, pdf, xml)
            language: Language (en, fr)
            
        Returns:
            ExtractedDocument or None if failed
        """
        print(f"Downloading: {url}")
        print(f"  Format: {format_type.upper()}, Language: {language.upper()}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Get filename from URL or create one
            filename = url.split('/')[-1] or f"document.{format_type}"
            if not filename.endswith(f".{format_type}"):
                filename += f".{format_type}"
            
            # Select appropriate loader
            if format_type == 'html':
                loader = self.html_loader
            elif format_type == 'pdf':
                loader = self.pdf_loader
            elif format_type == 'xml':
                loader = self.xml_loader
            else:
                print(f"  ERROR: Unsupported format {format_type}")
                return None
            
            # Load document
            from io import BytesIO
            content_bytes = BytesIO(response.content)
            doc = loader.load(content_bytes, filename)
            
            # Enrich metadata
            if doc.metadata is None:
                doc.metadata = {}
            
            doc.metadata['source_url'] = url
            doc.metadata['format'] = format_type
            doc.metadata['language'] = language
            doc.metadata['download_date'] = datetime.now().isoformat()
            
            print(f"  SUCCESS: {len(doc.text):,} characters")
            return doc
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return None


def ingest_employment_equity_act(ingester: SpecificURLIngester) -> List[ExtractedDocument]:
    """
    Ingest Employment Equity Act in all formats and languages.
    
    Base URL: https://laws-lois.justice.gc.ca/eng/acts/e-5.6/
    """
    print("=" * 80)
    print("EMPLOYMENT EQUITY ACT (S.C. 1995, c. 44)")
    print("=" * 80)
    print()
    
    documents = []
    
    # English versions
    en_urls = {
        'html': 'https://laws-lois.justice.gc.ca/eng/acts/e-5.6/page-1.html',
        'pdf': 'https://laws-lois.justice.gc.ca/PDF/E-5.6.pdf',
        'xml': 'https://laws-lois.justice.gc.ca/eng/XML/E-5.6.xml',
    }
    
    # French versions
    fr_urls = {
        'html': 'https://laws-lois.justice.gc.ca/fra/lois/e-5.6/page-1.html',
        'pdf': 'https://laws-lois.justice.gc.ca/PDF/E-5.6.pdf',  # PDFs are often bilingual
        'xml': 'https://laws-lois.justice.gc.ca/fra/XML/E-5.6.xml',
    }
    
    print("English Versions:")
    print("-" * 80)
    for format_type, url in en_urls.items():
        doc = ingester.download_and_ingest(url, format_type, 'en')
        if doc:
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata['act_name'] = 'Employment Equity Act'
            doc.metadata['act_code'] = 'S.C. 1995, c. 44'
            doc.metadata['jurisdiction'] = 'Canada - Federal'
            doc.metadata['document_type'] = 'legislation'
            doc.metadata['data_category'] = 'Government Programs'
            doc.metadata['program_area'] = 'Employment Equity'
            doc.metadata['use_case'] = 'Programs and Services'
            doc.metadata['target_users'] = 'Employers, HR professionals, Employees, Program administrators'
            documents.append(doc)
        print()
    
    print("French Versions:")
    print("-" * 80)
    for format_type, url in fr_urls.items():
        # Skip PDF for French if already downloaded (bilingual)
        if format_type == 'pdf':
            print(f"Downloading: {url}")
            print(f"  Format: PDF, Language: FR")
            print(f"  SKIPPED: PDF already ingested (bilingual)")
            print()
            continue
            
        doc = ingester.download_and_ingest(url, format_type, 'fr')
        if doc:
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata['act_name'] = 'Loi sur l\'équité en matière d\'emploi'
            doc.metadata['act_code'] = 'L.C. 1995, ch. 44'
            doc.metadata['jurisdiction'] = 'Canada - Fédéral'
            doc.metadata['document_type'] = 'legislation'
            doc.metadata['data_category'] = 'Government Programs'
            doc.metadata['program_area'] = 'Équité en matière d\'emploi'
            doc.metadata['use_case'] = 'Programmes et services'
            doc.metadata['target_users'] = 'Employeurs, Professionnels RH, Employés, Administrateurs de programmes'
            documents.append(doc)
        print()
    
    return documents


def ingest_it_collective_agreement(ingester: SpecificURLIngester) -> List[ExtractedDocument]:
    """
    Ingest IT Collective Agreement from Treasury Board Secretariat.
    
    Base URL: https://www.canada.ca/en/treasury-board-secretariat/topics/pay/collective-agreements/it.html
    """
    print("=" * 80)
    print("IT COLLECTIVE AGREEMENT (Treasury Board Secretariat)")
    print("=" * 80)
    print()
    
    documents = []
    
    # English and French URLs
    urls = {
        'en': 'https://www.canada.ca/en/treasury-board-secretariat/topics/pay/collective-agreements/it.html',
        'fr': 'https://www.canada.ca/fr/secretariat-conseil-tresor/sujets/remuneration/conventions-collectives/it.html',
    }
    
    for language, url in urls.items():
        doc = ingester.download_and_ingest(url, 'html', language)
        if doc:
            if doc.metadata is None:
                doc.metadata = {}
            
            if language == 'en':
                doc.metadata['agreement_name'] = 'Information Technology (IT) Group Collective Agreement'
                doc.metadata['bargaining_agent'] = 'Association of Canadian Financial Officers (ACFO)'
            else:
                doc.metadata['agreement_name'] = 'Convention collective du groupe Technologie de l\'information (IT)'
                doc.metadata['bargaining_agent'] = 'Association canadienne des agents financiers (ACAF)'
            
            doc.metadata['employer'] = 'Treasury Board of Canada'
            doc.metadata['document_type'] = 'collective_agreement'
            doc.metadata['data_category'] = 'Government Programs'
            doc.metadata['program_area'] = 'Public Service Employment'
            doc.metadata['use_case'] = 'Programs and Services'
            doc.metadata['jurisdiction'] = 'Canada - Federal'
            doc.metadata['target_users'] = 'IT professionals, Public servants, HR administrators, Union representatives'
            documents.append(doc)
        print()
    
    return documents


def save_ingestion_results(documents: List[ExtractedDocument], output_file: Path):
    """Save ingestion results to JSON."""
    data = []
    for doc in documents:
        data.append({
            "source_url": doc.metadata.get('source_url', 'N/A') if doc.metadata else 'N/A',
            "format": doc.metadata.get('format', 'N/A') if doc.metadata else 'N/A',
            "language": doc.metadata.get('language', 'N/A') if doc.metadata else 'N/A',
            "document_type": doc.metadata.get('document_type', 'N/A') if doc.metadata else 'N/A',
            "content_preview": doc.text[:500] + "..." if len(doc.text) > 500 else doc.text,
            "content_length": len(doc.text),
            "metadata": doc.metadata,
            "full_content": doc.text,  # Add full content for table analysis
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to: {output_file}")


def main():
    """Main ingestion workflow."""
    print("=" * 80)
    print("SPECIFIC URL INGESTION")
    print("=" * 80)
    print()
    print("Sources:")
    print("1. Employment Equity Act (laws-lois.justice.gc.ca)")
    print("2. IT Collective Agreement (Treasury Board Secretariat)")
    print()
    
    # Create output directory
    output_dir = Path("data/ingested/specific_urls")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ingester = SpecificURLIngester()
    all_documents = []
    
    # Ingest Employment Equity Act
    equity_docs = ingest_employment_equity_act(ingester)
    all_documents.extend(equity_docs)
    
    # Ingest IT Collective Agreement
    it_docs = ingest_it_collective_agreement(ingester)
    all_documents.extend(it_docs)
    
    # Save results
    print("=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    print()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"specific_urls_{timestamp}.json"
    save_ingestion_results(all_documents, output_file)
    
    # Summary
    print()
    print("=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print()
    
    # Group by document type
    equity_count = len([d for d in all_documents if d.metadata.get('document_type') == 'legislation'])
    agreement_count = len([d for d in all_documents if d.metadata.get('document_type') == 'collective_agreement'])
    
    print("EMPLOYMENT EQUITY ACT:")
    print(f"  Documents: {equity_count}")
    print(f"  Formats: HTML, PDF, XML")
    print(f"  Languages: EN, FR")
    print(f"  Category: Government Programs (Employment Equity)")
    equity_chars = sum(len(d.text) for d in all_documents if d.metadata.get('document_type') == 'legislation')
    print(f"  Total Characters: {equity_chars:,}")
    print()
    
    print("IT COLLECTIVE AGREEMENT:")
    print(f"  Documents: {agreement_count}")
    print(f"  Formats: HTML")
    print(f"  Languages: EN, FR")
    print(f"  Category: Government Programs (Public Service Employment)")
    agreement_chars = sum(len(d.text) for d in all_documents if d.metadata.get('document_type') == 'collective_agreement')
    print(f"  Total Characters: {agreement_chars:,}")
    print()
    
    print("TOTAL:")
    print(f"  Documents: {len(all_documents)}")
    print(f"  Total Characters: {sum(len(d.text) for d in all_documents):,}")
    print()
    
    # Format breakdown
    print("Format Breakdown:")
    format_counts = {}
    for doc in all_documents:
        fmt = doc.metadata.get('format', 'unknown') if doc.metadata else 'unknown'
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
    for fmt, count in sorted(format_counts.items()):
        print(f"  {fmt.upper()}: {count} documents")
    print()
    
    # Language breakdown
    print("Language Breakdown:")
    lang_counts = {}
    for doc in all_documents:
        lang = doc.metadata.get('language', 'unknown') if doc.metadata else 'unknown'
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    for lang, count in sorted(lang_counts.items()):
        print(f"  {lang.upper()}: {count} documents")
    print()
    
    print("=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Review ingestion results in JSON file")
    print("2. Combine with other ingested data sources")
    print("3. Proceed to Phase 2: Chunking & Embedding")
    print("4. Index in Azure AI Search")
    print()


if __name__ == "__main__":
    main()
