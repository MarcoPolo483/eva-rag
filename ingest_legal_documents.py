"""
Ingest legal documents for multiple clients with client-specific metadata.

This script ingests legal documents (Supreme Court cases, knowledge articles)
for different clients, tagging each document with client-specific metadata
to enable multi-tenant RAG scenarios.

Clients:
1. Jurisprudence - Supreme Court case law research
2. AssistMe - Government programs and services (OAS, GIS, CPP, CPPD)

Usage:
    python ingest_legal_documents.py [--client jurisprudence|assistme|all]

Data Sources:
- AssistMe: c:/Users/marco/Documents/_AI Dev/Marco/assistme/knowledge_articles_r2r3_en 2.xml
  (104 knowledge articles, 1.24 MB, Cúram system documentation)
- Jurisprudence: data/legal/jurisprudence/cases/*.html
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List

from eva_rag.loaders.html_loader import HTMLLoader
from eva_rag.loaders.xml_loader import XMLLoader
from eva_rag.loaders.pdf_loader import PDFLoader
from eva_rag.loaders.base import ExtractedDocument


class LegalDocumentIngester:
    """Ingest legal documents with client-specific metadata tagging."""
    
    def __init__(self, client_name: str):
        """
        Initialize ingester for specific client.
        
        Args:
            client_name: Client identifier (jurisprudence, assistme)
        """
        self.client_name = client_name
        self.html_loader = HTMLLoader()
        self.xml_loader = XMLLoader()
        self.pdf_loader = PDFLoader()
        
    def ingest_directory(
        self,
        source_dir: Path,
        document_type: str = "case_law",
        jurisdiction: str = "Canada"
    ) -> List[ExtractedDocument]:
        """
        Ingest all legal documents from directory.
        
        Args:
            source_dir: Directory containing legal documents
            document_type: Type of documents (case_law, guidance, faq, policy)
            jurisdiction: Legal jurisdiction (Canada, Ontario, Quebec, etc.)
            
        Returns:
            List of extracted documents with client metadata
        """
        print(f"Ingesting from: {source_dir}")
        print(f"Client: {self.client_name}")
        print(f"Document Type: {document_type}")
        print(f"Jurisdiction: {jurisdiction}")
        print()
        
        documents = []
        
        # Process HTML files
        html_files = list(source_dir.glob("*.html")) + list(source_dir.glob("*.htm"))
        if html_files:
            print(f"Found {len(html_files)} HTML file(s)")
            for html_file in html_files:
                doc = self._ingest_file(html_file, self.html_loader)
                if doc:
                    self._enrich_metadata(doc, document_type, jurisdiction)
                    documents.append(doc)
        
        # Process XML files
        xml_files = list(source_dir.glob("*.xml"))
        if xml_files:
            print(f"Found {len(xml_files)} XML file(s)")
            for xml_file in xml_files:
                doc = self._ingest_file(xml_file, self.xml_loader)
                if doc:
                    self._enrich_metadata(doc, document_type, jurisdiction)
                    documents.append(doc)
        
        # Process PDF files
        pdf_files = list(source_dir.glob("*.pdf"))
        if pdf_files:
            print(f"Found {len(pdf_files)} PDF file(s)")
            for pdf_file in pdf_files:
                doc = self._ingest_file(pdf_file, self.pdf_loader)
                if doc:
                    self._enrich_metadata(doc, document_type, jurisdiction)
                    documents.append(doc)
        
        print(f"Total documents ingested: {len(documents)}")
        print()
        
        return documents
    
    def _ingest_file(self, file_path: Path, loader) -> ExtractedDocument:
        """Ingest single file with error handling."""
        try:
            print(f"  Processing: {file_path.name}")
            with open(file_path, 'rb') as f:
                doc = loader.load(f, file_path.name)
            print(f"    Characters: {len(doc.text):,}")
            return doc
        except Exception as e:
            print(f"    ERROR: {e}")
            return None
    
    def _enrich_metadata(
        self,
        doc: ExtractedDocument,
        document_type: str,
        jurisdiction: str
    ):
        """Add client-specific and legal metadata to document."""
        if doc.metadata is None:
            doc.metadata = {}
        
        # Client metadata (multi-tenant tagging)
        doc.metadata['client'] = self.client_name
        doc.metadata['use_case'] = 'Legal Research' if self.client_name == 'jurisprudence' else 'Programs and Services'
        
        # Legal document metadata
        doc.metadata['document_type'] = document_type
        doc.metadata['jurisdiction'] = jurisdiction
        doc.metadata['data_category'] = 'Government Programs' if self.client_name == 'assistme' else 'Legal Documents'
        
        # Client-specific tags
        if self.client_name == 'jurisprudence':
            doc.metadata['target_users'] = 'Legal researchers, Policy analysts'
            doc.metadata['content_focus'] = 'Supreme Court decisions, Case law precedents'
        elif self.client_name == 'assistme':
            doc.metadata['target_users'] = 'Service agents, Citizens, Program administrators'
            doc.metadata['content_focus'] = 'OAS, GIS, CPP, CPPD programs and services'
            doc.metadata['programs'] = 'OAS, GIS, CPP, CPPD, ALW, ALWS'
            doc.metadata['system'] = 'Cúram'


def ingest_assistme_from_xml(xml_path: Path) -> List[ExtractedDocument]:
    """
    Ingest AssistMe knowledge articles from XML file.
    
    Args:
        xml_path: Path to knowledge_articles XML file
        
    Returns:
        List of extracted documents
    """
    print("=" * 80)
    print("INGESTING ASSISTME FROM XML")
    print("=" * 80)
    print(f"Source: {xml_path}")
    print()
    
    ingester = LegalDocumentIngester("assistme")
    xml_loader = ingester.xml_loader
    
    if not xml_path.exists():
        print(f"ERROR: XML file not found: {xml_path}")
        return []
    
    print(f"Processing: {xml_path.name}")
    try:
        with open(xml_path, 'rb') as f:
            doc = xml_loader.load(f, xml_path.name)
        
        print(f"  Total characters: {len(doc.text):,}")
        
        # Enrich with AssistMe metadata
        ingester._enrich_metadata(doc, "knowledge_article", "Canada - Federal Programs")
        
        if doc.metadata:
            doc.metadata['source_file'] = str(xml_path)
            doc.metadata['format'] = 'xml'
        
        return [doc]
        
    except Exception as e:
        print(f"ERROR: Failed to load XML: {e}")
        import traceback
        traceback.print_exc()
        return []


def create_sample_legal_documents():
    """Create sample legal documents for both clients."""
    print("=" * 80)
    print("CREATING SAMPLE LEGAL DOCUMENTS")
    print("=" * 80)
    print()
    
    # Create directories
    juris_dir = Path("data/legal/jurisprudence/cases")
    juris_dir.mkdir(parents=True, exist_ok=True)
    
    assistme_dir = Path("data/legal/assistme/guidance")
    # NOTE: AssistMe data comes from XML, not these samples
    
    # Sample Jurisprudence case (HTML)
    case1_path = juris_dir / "sample_scc_case_2024_001.html"
    if not case1_path.exists():
        print(f"Creating: {case1_path.name}")
        with open(case1_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>R. v. Smith, 2024 SCC 1</title>
    <meta name="description" content="Supreme Court of Canada decision on privacy rights">
</head>
<body>
    <h1>R. v. Smith, 2024 SCC 1</h1>
    <h2>Supreme Court of Canada</h2>
    
    <h3>Case Information</h3>
    <p><strong>Citation:</strong> R. v. Smith, 2024 SCC 1</p>
    <p><strong>Date:</strong> January 15, 2024</p>
    <p><strong>Court:</strong> Supreme Court of Canada</p>
    <p><strong>Judges:</strong> Wagner C.J., Karakatsanis, Côté, Brown, Rowe, Martin, Kasirer, Jamal, O'Bonsawin JJ.</p>
    
    <h3>Summary</h3>
    <p>This case considers the scope of privacy rights under section 8 of the Canadian Charter of Rights and Freedoms 
    in the context of modern digital surveillance technologies. The Court held that individuals have a reasonable 
    expectation of privacy in their location data collected through mobile devices.</p>
    
    <h3>Issues</h3>
    <ol>
        <li>Does the collection of location data from mobile devices constitute a search under s. 8 of the Charter?</li>
        <li>If so, what is the appropriate standard for judicial authorization?</li>
    </ol>
    
    <h3>Decision</h3>
    <p>The appeal is allowed. The Court held that:</p>
    <ol>
        <li>Individuals have a reasonable expectation of privacy in their historical location data.</li>
        <li>Law enforcement must obtain a warrant based on reasonable grounds before accessing such data.</li>
        <li>The reasonableness standard applies to the manner of search execution.</li>
    </ol>
    
    <h3>Key Passages</h3>
    <p>"In the digital age, location data reveals intimate details of an individual's life. The continuous tracking
    of one's movements through mobile device data engages the highest privacy interests protected by s. 8 of the Charter."</p>
    
    <h3>Disposition</h3>
    <p>Appeal allowed. Evidence excluded under s. 24(2) of the Charter.</p>
</body>
</html>""")
    
    # Sample Jurisprudence case 2 (HTML)
    case2_path = juris_dir / "sample_scc_case_2024_002.html"
    if not case2_path.exists():
        print(f"Creating: {case2_path.name}")
        with open(case2_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>ABC Corp. v. Minister of Finance, 2024 SCC 2</title>
    <meta name="description" content="Supreme Court decision on administrative law">
</head>
<body>
    <h1>ABC Corp. v. Minister of Finance, 2024 SCC 2</h1>
    <h2>Supreme Court of Canada</h2>
    
    <h3>Case Information</h3>
    <p><strong>Citation:</strong> ABC Corp. v. Minister of Finance, 2024 SCC 2</p>
    <p><strong>Date:</strong> March 8, 2024</p>
    <p><strong>Judges:</strong> Wagner C.J., Karakatsanis, Brown, Martin, Kasirer, Jamal, O'Bonsawin JJ.</p>
    
    <h3>Summary</h3>
    <p>This appeal concerns the standard of review applicable to administrative decisions involving 
    discretionary tax assessments under the Income Tax Act. The Court clarified the application of 
    the reasonableness standard in the taxation context.</p>
    
    <h3>Decision</h3>
    <p>The appeal is dismissed. Reasonableness is the applicable standard of review for discretionary
    tax assessments. The Minister's decision was reasonable given the evidence and statutory context.</p>
</body>
</html>""")
    
    print()
    print(f"Jurisprudence samples: {len(list(juris_dir.glob('*.html')))} files")
    print()
    
    return juris_dir


def save_ingestion_results(client_name: str, documents: List[ExtractedDocument], output_dir: Path):
    """Save ingestion results to JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{client_name}_legal_docs_{timestamp}.json"
    
    data = []
    for doc in documents:
        data.append({
            "client": client_name,
            "filename": doc.metadata.get('filename', 'N/A') if doc.metadata else 'N/A',
            "document_type": doc.metadata.get('document_type', 'N/A') if doc.metadata else 'N/A',
            "content_preview": doc.text[:500] + "..." if len(doc.text) > 500 else doc.text,
            "content_length": len(doc.text),
            "metadata": doc.metadata,
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to: {output_file}")
    return output_file


def main():
    """Main ingestion workflow for both clients."""
    print("=" * 80)
    print("MULTI-CLIENT DOCUMENT INGESTION")
    print("=" * 80)
    print()
    print("Multi-Client Document Ingestion")
    print("Clients: Jurisprudence (case law) + AssistMe (programs & services)")
    print()
    
    # Create output directory
    output_dir = Path("data/ingested/legal")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for existing documents or create samples
    juris_dir = Path("data/legal/jurisprudence/cases")
    
    # Check for jurispipeline samples
    juris_external = Path("c:/Users/marco/Documents/_AI Dev/EVA Suite/eva-orchestrator/jurispipeline/data/raw-samples")
    
    if not juris_dir.exists() or len(list(juris_dir.glob("*.html"))) == 0:
        print("No local legal documents found. Creating samples...")
        print()
        juris_dir = create_sample_legal_documents()
    
    # Also copy from jurispipeline if available
    if juris_external.exists():
        print(f"Found external jurisprudence samples in: {juris_external}")
        external_files = list(juris_external.glob("*.html"))
        if external_files:
            print(f"Copying {len(external_files)} external sample(s)...")
            juris_dir.mkdir(parents=True, exist_ok=True)
            for ext_file in external_files:
                dest = juris_dir / ext_file.name
                if not dest.exists():
                    import shutil
                    shutil.copy(ext_file, dest)
                    print(f"  Copied: {ext_file.name}")
            print()
    
    # Ingest Jurisprudence client documents
    print("=" * 80)
    print("CLIENT 1: JURISPRUDENCE")
    print("=" * 80)
    print()
    
    juris_ingester = LegalDocumentIngester("jurisprudence")
    juris_docs = juris_ingester.ingest_directory(
        juris_dir,
        document_type="case_law",
        jurisdiction="Canada - Supreme Court"
    )
    
    # Ingest AssistMe client documents from XML
    print("=" * 80)
    print("CLIENT 2: ASSISTME")
    print("=" * 80)
    print()
    
    assistme_xml = Path("c:/Users/marco/Documents/_AI Dev/Marco/assistme/knowledge_articles_r2r3_en 2.xml")
    assistme_docs = ingest_assistme_from_xml(assistme_xml)
    
    # Save results
    print("=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    print()
    
    juris_output = save_ingestion_results("jurisprudence", juris_docs, output_dir)
    assistme_output = save_ingestion_results("assistme", assistme_docs, output_dir)
    
    # Summary
    print()
    print("=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print()
    
    print("CLIENT: JURISPRUDENCE")
    print(f"  Documents: {len(juris_docs)}")
    print(f"  Total Characters: {sum(len(d.text) for d in juris_docs):,}")
    print(f"  Document Type: Case Law")
    print(f"  Jurisdiction: Supreme Court of Canada")
    print()
    
    print("CLIENT: ASSISTME")
    print(f"  Documents: {len(assistme_docs)}")
    print(f"  Total Characters: {sum(len(d.text) for d in assistme_docs):,}")
    print(f"  Document Type: Government Programs Knowledge Articles")
    print(f"  Programs: OAS, GIS, CPP, CPPD, ALW, ALWS")
    print(f"  System: Cúram (Social Program Management)")
    print(f"  Jurisdiction: Canada - Federal Programs")
    print(f"  Source: XML (knowledge_articles_r2r3_en 2.xml, 104 articles)")
    print()
    
    print("TOTAL:")
    print(f"  Clients: 2")
    print(f"  Documents: {len(juris_docs) + len(assistme_docs)}")
    print(f"  Total Characters: {sum(len(d.text) for d in juris_docs + assistme_docs):,}")
    print()
    
    print("=" * 80)
    print("TASK 3 COMPLETE")
    print("=" * 80)
    print()
    print("Multi-tenant ingestion successful!")
    print("Documents are tagged with client-specific metadata.")
    print()
    print("Next Steps:")
    print("1. Review client-specific metadata in JSON files")
    print("2. Proceed to Phase 2: Chunking (preserve client tags)")
    print("3. Index in Azure AI Search with client filtering")
    print("4. Deploy client-specific RAG endpoints")
    print()


if __name__ == "__main__":
    main()
