# eva-rag

RAG (Retrieval-Augmented Generation) module for document ingestion, chunking, embedding, and retrieval.

## Quick Start: PDF Text Extraction

When specialized PDF processing tools are not available, you can use Python's `pypdf` library as a lightweight fallback:

### Prerequisites
```bash
pip install pypdf
```

### Extract PDF Text (One-liner)
```bash
python -c "import pypdf; reader = pypdf.PdfReader('document.pdf'); [print(f'\n--- Page {i+1} ---\n{page.extract_text()}') for i, page in enumerate(reader.pages)]"
```

### Extract to File
```python
import pypdf

def extract_pdf_text(pdf_path, output_path=None):
    """Extract text from PDF file."""
    reader = pypdf.PdfReader(pdf_path)

    text_content = []
    for i, page in enumerate(reader.pages):
        text_content.append(f"--- Page {i+1} ---\n{page.extract_text()}\n")

    full_text = "\n".join(text_content)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

    return full_text

# Usage
text = extract_pdf_text('input.pdf', 'output.txt')
print(f"Extracted {len(text)} characters")
```

### Use Cases
- Quick document preview for analysis
- Text extraction when Azure Document Intelligence is unavailable
- Local development without cloud dependencies
- Proof-of-concept RAG ingestion pipelines

### Limitations
- No layout preservation
- No table extraction
- No image/OCR processing
- Best for text-based PDFs

For production RAG pipelines, use:
- **Azure Document Intelligence** (formerly Form Recognizer) - Layout + OCR
- **LangChain DocumentLoaders** - Multi-format support
- **Unstructured.io** - Advanced document parsing

## Architecture

(To be implemented: ingestion pipeline, chunking strategy, vector storage, hybrid search)
