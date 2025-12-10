# EVA-RAG Ingestion Continuation Guide

**Created:** December 9, 2025  
**For:** Next work session on chunking phase  
**Status:** Ingestion complete, ready to proceed

---

## Quick Start (Resume Work)

### What Was Completed

✅ **All data ingested**: 15.2 MB across 1,372 documents  
✅ **All tests passed**: 3/3 data sources validated (100%)  
✅ **Architecture documented**: Complete loader framework analysis  
✅ **Issues identified**: 2 critical blockers before chunking

### Where You Left Off

You completed comprehensive data source testing and validation. All ingestion scripts working perfectly. Ready to move to chunking phase BUT two critical issues must be addressed first:

1. **IT Collective Agreement salary tables** require special chunking algorithm
2. **Jurisprudence synthetic data** needs `is_synthetic: true` flag

---

## Critical Path (What to Do Next)

### Phase 1: Pre-Chunking Fixes (Week 1) - START HERE

#### Task 1: Implement Table-Aware Chunking 🔴 CRITICAL

**Priority**: P0 - Must complete before any chunking  
**Estimated Time**: 4-6 hours  
**Complexity**: Medium

**What You Need to Know**:
- IT Collective Agreement contains **25 markdown salary tables**
- Tables have 8 steps × 9 rows each
- Standard chunking would **destroy table structure** (unusable for RAG)
- Partial tables enable **LLM hallucination** (inventing salary values)

**Where to Start**:
1. Read: `docs/IT-COLLECTIVE-AGREEMENT-TABLE-ANALYSIS.md` (400+ lines, Option 1 recommended)
2. Review: `analyze_tables.py` (shows current table detection logic)
3. Access data: `data/ingested/specific_urls/specific_urls_20251209_013238.json`

**Implementation Steps**:

**Step 1: Create table extraction function**
```python
# File: src/eva_rag/chunking/table_extractor.py

import re
from typing import List, Tuple

def extract_markdown_tables(content: str) -> List[Tuple[int, int, str]]:
    """
    Extract all markdown tables with their positions.
    
    Returns:
        List of (start_pos, end_pos, table_text) tuples
    """
    # Regex pattern for markdown tables with Step columns
    pattern = r'\|[^\n]*Step[^\n]*\|[^\n]*\n\|[-\s|]+\|[^\n]*\n(?:\|[^\n]+\|[^\n]*\n)+'
    
    tables = []
    for match in re.finditer(pattern, content):
        start_pos = match.start()
        end_pos = match.end()
        table_text = match.group()
        tables.append((start_pos, end_pos, table_text))
    
    return tables

def extract_table_classification(table_text: str) -> str:
    """Extract IT classification (IT-01 to IT-05) from table."""
    classifications = ['IT-01', 'IT-02', 'IT-03', 'IT-04', 'IT-05']
    for classification in classifications:
        if classification in table_text:
            return classification
    return 'unknown'
```

**Step 2: Create table-aware chunker**
```python
# File: src/eva_rag/chunking/table_aware_chunker.py

from typing import List
from dataclasses import dataclass

@dataclass
class Chunk:
    text: str
    metadata: dict
    start_pos: int
    end_pos: int

def chunk_with_table_awareness(
    content: str,
    chunk_size: int = 500,  # tokens
    overlap: int = 100,
    context_chars: int = 200
) -> List[Chunk]:
    """
    Chunk document while preserving table integrity.
    
    Algorithm:
    1. Extract all tables and positions
    2. Mark table regions as "do not split"
    3. Chunk non-table content normally
    4. Add context before/after each table
    5. Tag table chunks with metadata
    """
    from eva_rag.chunking.table_extractor import extract_markdown_tables, extract_table_classification
    
    chunks = []
    
    # Step 1: Extract all tables
    tables = extract_markdown_tables(content)
    table_regions = [(start, end) for start, end, _ in tables]
    
    # Step 2: Create "do not split" regions
    # Each table gets 200 chars context before/after
    protected_regions = []
    for start, end, table_text in tables:
        context_start = max(0, start - context_chars)
        context_end = min(len(content), end + context_chars)
        protected_regions.append((context_start, context_end, table_text, start, end))
    
    # Step 3: Chunk non-table content
    current_pos = 0
    
    for context_start, context_end, table_text, table_start, table_end in protected_regions:
        # Chunk content before this table
        if current_pos < context_start:
            non_table_text = content[current_pos:context_start]
            # Use standard semantic chunking on non_table_text
            # (implement or call existing chunker here)
            # For now, simple sentence-based chunking:
            sentences = non_table_text.split('. ')
            for sentence in sentences:
                if len(sentence.strip()) > 0:
                    chunks.append(Chunk(
                        text=sentence.strip() + '.',
                        metadata={'is_table': False},
                        start_pos=current_pos,
                        end_pos=current_pos + len(sentence)
                    ))
                    current_pos += len(sentence)
        
        # Step 4: Add table chunk with context
        table_with_context = content[context_start:context_end]
        classification = extract_table_classification(table_text)
        
        chunks.append(Chunk(
            text=table_with_context,
            metadata={
                'is_table': True,
                'classification': classification,
                'table_type': 'salary_table',
                'columns': 8,  # Steps 1-8
                'rows': 9,     # Effective dates 2020-2024
            },
            start_pos=context_start,
            end_pos=context_end
        ))
        
        current_pos = context_end
    
    # Step 5: Chunk remaining content after last table
    if current_pos < len(content):
        remaining_text = content[current_pos:]
        # Use standard semantic chunking on remaining_text
        sentences = remaining_text.split('. ')
        for sentence in sentences:
            if len(sentence.strip()) > 0:
                chunks.append(Chunk(
                    text=sentence.strip() + '.',
                    metadata={'is_table': False},
                    start_pos=current_pos,
                    end_pos=current_pos + len(sentence)
                ))
                current_pos += len(sentence)
    
    return chunks
```

**Step 3: Test on IT Collective Agreement**
```python
# File: test_table_chunking.py

import json
from pathlib import Path
from eva_rag.chunking.table_aware_chunker import chunk_with_table_awareness

def test_it_agreement_chunking():
    """Test table-aware chunking on IT Collective Agreement."""
    
    # Load ingested data
    data_file = Path("data/ingested/specific_urls/specific_urls_20251209_013238.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    
    # Find IT Collective Agreement documents
    it_docs = [d for d in docs if 'IT' in d.get('metadata', {}).get('agreement_name', '')]
    
    print(f"Found {len(it_docs)} IT Collective Agreement documents")
    
    for doc in it_docs:
        language = doc.get('language', 'unknown')
        content = doc.get('full_content', '')
        
        print(f"\nProcessing: {language.upper()}")
        print(f"Content length: {len(content):,} chars")
        
        # Chunk with table awareness
        chunks = chunk_with_table_awareness(content)
        
        # Count table chunks
        table_chunks = [c for c in chunks if c.metadata.get('is_table')]
        text_chunks = [c for c in chunks if not c.metadata.get('is_table')]
        
        print(f"Total chunks: {len(chunks)}")
        print(f"  Table chunks: {len(table_chunks)}")
        print(f"  Text chunks: {len(text_chunks)}")
        
        # Validate: No tables split
        print("\nTable Validation:")
        for i, chunk in enumerate(table_chunks, 1):
            classification = chunk.metadata.get('classification', 'unknown')
            print(f"  Table {i}: {classification} - {len(chunk.text):,} chars")
            
            # Check if table is complete (has header + all rows)
            if '| Step 1 |' in chunk.text and '| Step 8 |' in chunk.text:
                print(f"    ✅ Table structure intact (8 steps)")
            else:
                print(f"    ❌ TABLE SPLIT DETECTED - CRITICAL ERROR")
        
        # Show sample chunks
        print("\nSample Table Chunk:")
        if table_chunks:
            sample = table_chunks[0]
            print(f"  Classification: {sample.metadata.get('classification')}")
            print(f"  Text (first 300 chars):")
            print(f"    {sample.text[:300]}...")

if __name__ == "__main__":
    test_it_agreement_chunking()
```

**Expected Output**:
```
Found 2 IT Collective Agreement documents

Processing: EN
Content length: 346,203 chars
Total chunks: 175
  Table chunks: 25
  Text chunks: 150

Table Validation:
  Table 1: IT-01 - 2,450 chars
    ✅ Table structure intact (8 steps)
  Table 2: IT-02 - 2,450 chars
    ✅ Table structure intact (8 steps)
  ...
  Table 25: IT-05 - 2,450 chars
    ✅ Table structure intact (8 steps)

Processing: FR
Content length: 400,047 chars
Total chunks: 180
  Table chunks: 25
  Text chunks: 155

Table Validation:
  Table 1: IT-01 - 2,550 chars
    ✅ Table structure intact (8 steps)
  ...
```

**Success Criteria**:
- ✅ All 25 tables detected (EN)
- ✅ All 25 tables detected (FR) - or investigate if 0 found
- ✅ Zero tables split across chunks
- ✅ All table chunks tagged with `is_table: true`
- ✅ All table chunks have `classification` metadata

**Files to Create**:
- `src/eva_rag/chunking/table_extractor.py`
- `src/eva_rag/chunking/table_aware_chunker.py`
- `test_table_chunking.py`

**Documentation Reference**:
- `docs/IT-COLLECTIVE-AGREEMENT-TABLE-ANALYSIS.md` (full analysis, 400+ lines)

---

#### Task 2: Add Synthetic Data Flag 🔴 CRITICAL

**Priority**: P0 - Must complete before RAG deployment  
**Estimated Time**: 1 hour  
**Complexity**: Low

**What You Need to Know**:
- Jurisprudence dataset has 4 fake Supreme Court cases
- Currently NOT flagged as synthetic (HIGH legal misinformation risk)
- Must add `is_synthetic: true` to all jurisprudence chunks

**Where to Start**:
1. Read: `docs/JURISPRUDENCE-DATA-STATUS.md` (synthetic data analysis)
2. Access data: `data/ingested/legal/jurisprudence_legal_docs_20251208_115158.json`

**Implementation Steps**:

**Step 1: Add flag to existing JSON**
```python
# File: scripts/add_synthetic_flag.py

import json
from pathlib import Path

def add_synthetic_flag_to_jurisprudence():
    """Add is_synthetic flag to all jurisprudence documents."""
    
    # Load ingested data
    data_file = Path("data/ingested/legal/jurisprudence_legal_docs_20251208_115158.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    
    # Find jurisprudence documents (skip AssistMe)
    juris_docs = [d for d in docs if d.get('metadata', {}).get('client') == 'jurisprudence']
    
    print(f"Found {len(juris_docs)} jurisprudence documents")
    
    # Add synthetic flag
    modified_count = 0
    for doc in juris_docs:
        if doc.get('metadata'):
            doc['metadata']['is_synthetic'] = True
            doc['metadata']['data_quality'] = 'demo_only'
            doc['metadata']['warning'] = 'This is synthetic demo data, not real case law'
            modified_count += 1
    
    print(f"Modified {modified_count} documents")
    
    # Save back
    output_file = data_file.parent / f"{data_file.stem}_with_synthetic_flag.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to: {output_file}")
    
    # Validation
    print("\nValidation:")
    for doc in juris_docs:
        citation = doc.get('metadata', {}).get('citation', 'N/A')
        is_synthetic = doc.get('metadata', {}).get('is_synthetic', False)
        print(f"  {citation}: is_synthetic = {is_synthetic}")

if __name__ == "__main__":
    add_synthetic_flag_to_jurisprudence()
```

**Step 2: Update chunker to preserve flag**
```python
# Ensure chunker preserves is_synthetic flag in metadata
# When chunking jurisprudence documents, copy flag to all chunks:

def chunk_jurisprudence_document(doc):
    chunks = standard_chunking(doc)
    
    # Preserve synthetic flag in all chunks
    if doc.metadata.get('is_synthetic'):
        for chunk in chunks:
            chunk.metadata['is_synthetic'] = True
            chunk.metadata['warning'] = 'Synthetic demo data, not real case law'
    
    return chunks
```

**Step 3: Add disclaimer to RAG responses**
```python
# File: src/eva_rag/services/response_formatter.py

def format_rag_response(answer: str, sources: List[dict]) -> dict:
    """Format RAG response with synthetic data disclaimer."""
    
    # Check if any sources are synthetic
    has_synthetic = any(s.get('metadata', {}).get('is_synthetic') for s in sources)
    
    response = {
        'answer': answer,
        'sources': sources,
    }
    
    if has_synthetic:
        response['disclaimer'] = (
            "⚠️ WARNING: This response includes synthetic demo data, "
            "not real case law. Do not use for legal research or decision-making."
        )
    
    return response
```

**Expected Output**:
```
Found 4 jurisprudence documents
Modified 4 documents
Saved to: data/ingested/legal/jurisprudence_legal_docs_20251208_115158_with_synthetic_flag.json

Validation:
  2024 SCC 1: is_synthetic = True
  2024 SCC 2: is_synthetic = True
  2024 SCC 1: is_synthetic = True
  2024 SCC 2: is_synthetic = True
```

**Success Criteria**:
- ✅ All 4 jurisprudence documents flagged
- ✅ Flag preserved during chunking
- ✅ Disclaimer shown in RAG responses
- ✅ No synthetic data presented as authoritative

**Files to Create**:
- `scripts/add_synthetic_flag.py`

**Documentation Reference**:
- `docs/JURISPRUDENCE-DATA-STATUS.md` (synthetic data analysis)

---

#### Task 3: Investigate French Table Detection 🟡 HIGH

**Priority**: P1 - Should complete during table-aware implementation  
**Estimated Time**: 1 hour  
**Complexity**: Low

**What You Need to Know**:
- English IT Agreement: ~205 table markers found (`"| Step"`)
- French IT Agreement: ~0 table markers found
- Need to verify if tables exist and update detection regex

**Investigation Steps**:

**Step 1: Check French content**
```python
# File: scripts/investigate_french_tables.py

import json
from pathlib import Path

def investigate_french_tables():
    """Check if French IT Agreement has tables."""
    
    # Load ingested data
    data_file = Path("data/ingested/specific_urls/specific_urls_20251209_013238.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    
    # Find French IT Agreement
    french_it = None
    for doc in docs:
        if doc.get('language') == 'fr' and 'IT' in doc.get('metadata', {}).get('agreement_name', ''):
            french_it = doc
            break
    
    if not french_it:
        print("French IT Agreement not found")
        return
    
    content = french_it.get('full_content', '')
    print(f"French IT Agreement: {len(content):,} chars")
    
    # Check for various table patterns
    patterns = {
        'Step (EN)': '| Step ',
        'Étape (FR)': '| Étape ',
        'Échelon (FR alt)': '| Échelon ',
        'Generic pipe': '|',
        'Table markers': '---',
    }
    
    print("\nPattern Detection:")
    for name, pattern in patterns.items():
        count = content.count(pattern)
        print(f"  {name}: {count} occurrences")
    
    # Show sample table (if exists)
    if '| Étape ' in content or '| Échelon ' in content:
        print("\nSample Table Found:")
        # Find first table occurrence
        start = content.find('| Étape ') if '| Étape ' in content else content.find('| Échelon ')
        sample = content[start:start+500]
        print(sample)
    else:
        print("\nNo French table markers found. Showing sample content:")
        # Show 1000 chars from middle of document
        mid = len(content) // 2
        print(content[mid:mid+1000])

if __name__ == "__main__":
    investigate_french_tables()
```

**Step 2: Update table detection regex**
```python
# Update extract_markdown_tables() to support bilingual detection

def extract_markdown_tables(content: str, language: str = 'en') -> List[Tuple[int, int, str]]:
    """Extract markdown tables with bilingual support."""
    
    # Language-specific patterns
    if language == 'en':
        step_pattern = 'Step'
    elif language == 'fr':
        # Try both common French terms
        step_pattern = '(?:Étape|Échelon)'
    else:
        step_pattern = '(?:Step|Étape|Échelon)'
    
    pattern = f r'\|[^\n]*{step_pattern}[^\n]*\|[^\n]*\n\|[-\s|]+\|[^\n]*\n(?:\|[^\n]+\|[^\n]*\n)+'
    
    tables = []
    for match in re.finditer(pattern, content):
        start_pos = match.start()
        end_pos = match.end()
        table_text = match.group()
        tables.append((start_pos, end_pos, table_text))
    
    return tables
```

**Expected Outcomes**:
- **Scenario A**: Tables exist with "| Étape " → Update regex, re-test
- **Scenario B**: Tables exist with different structure → Adapt detection logic
- **Scenario C**: No tables in French version → Document finding, English-only table chunking

**Success Criteria**:
- ✅ French table detection working (if tables exist)
- ✅ Bilingual regex pattern implemented
- ✅ Both EN and FR tables detected correctly

**Files to Create**:
- `scripts/investigate_french_tables.py`

---

### Phase 2: Standard Chunking (Week 1-2)

After completing Phase 1, proceed to standard chunking for non-table content.

#### Task 4: Chunk AssistMe XML

**Command**:
```powershell
cd "c:\Users\marco\Documents\_AI Dev\EVA Suite\eva-rag"
python scripts/chunk_assistme.py
```

**Expected Output**:
- Input: 104 articles (1,243,742 chars)
- Output: ~248 chunks (~500 tokens each, 100 overlap)
- File: `data/chunked/assistme_chunks_YYYYMMDD_HHMMSS.json`

**Metadata to Preserve**:
- `client`: assistme
- `use_case`: Programs and Services
- `document_type`: knowledge_article
- `programs`: OAS, GIS, CPP, CPPD, ALW, ALWS
- `system`: Cúram

---

#### Task 5: Chunk Employment Equity Act

**Command**:
```powershell
python scripts/chunk_employment_equity.py
```

**Expected Output**:
- Input: 5 documents (1,922,290 chars usable - HTML/PDF only)
- Output: ~470 chunks
- File: `data/chunked/employment_equity_chunks_YYYYMMDD_HHMMSS.json`

**Note**: Skip XML format (extraction failed, only 221 chars)

---

#### Task 6: Chunk IT Collective Agreement

**Command**:
```powershell
python scripts/chunk_it_agreement.py  # Uses table-aware chunker
```

**Expected Output**:
- Input: 2 documents (746,250 chars)
- Output: ~175 chunks (25 table chunks + 150 text chunks)
- File: `data/chunked/it_agreement_chunks_YYYYMMDD_HHMMSS.json`

**CRITICAL**: Use table-aware chunker from Phase 1

---

#### Task 7: Chunk Canada.ca

**Command**:
```powershell
python scripts/chunk_canada_ca.py
```

**Expected Output**:
- Input: 1,257 pages (11,296,905 chars)
- Output: ~2,800 chunks
- File: `data/chunked/canada_ca_chunks_YYYYMMDD_HHMMSS.json`

---

### Phase 3: Embedding & Indexing (Week 2-3)

#### Task 8: Generate Embeddings

**Command**:
```powershell
python scripts/generate_embeddings.py
```

**Configuration**:
- Model: Azure OpenAI `text-embedding-3-small`
- Dimensions: 1536
- Batch size: 100 chunks per request
- Estimated cost: ~$2-3 for 3,500 chunks

**Expected Output**:
- File: `data/embeddings/embeddings_YYYYMMDD_HHMMSS.json`
- Format: `[{"chunk_id": "...", "embedding": [0.123, ...], "metadata": {...}}]`

---

#### Task 9: Index in Azure AI Search

**Command**:
```powershell
python scripts/index_to_azure_search.py
```

**Index Configuration**:
```json
{
  "name": "eva-rag-index-v1",
  "fields": [
    {"name": "chunk_id", "type": "Edm.String", "key": true},
    {"name": "content", "type": "Edm.String", "searchable": true},
    {"name": "content_vector", "type": "Collection(Edm.Single)", "dimensions": 1536, "searchable": true},
    {"name": "client", "type": "Edm.String", "filterable": true},
    {"name": "language", "type": "Edm.String", "filterable": true},
    {"name": "document_type", "type": "Edm.String", "filterable": true},
    {"name": "is_table", "type": "Edm.Boolean", "filterable": true},
    {"name": "is_synthetic", "type": "Edm.Boolean", "filterable": true},
    {"name": "classification", "type": "Edm.String", "filterable": true}
  ]
}
```

---

### Phase 4: Testing & Validation (Week 3)

#### Task 10: Test RAG Queries

**Test Script**:
```powershell
python scripts/test_rag_queries.py
```

**Sample Queries**:
```python
test_queries = [
    # AssistMe
    "How do I verify person evidence in Cúram?",
    "What are the ALW eligibility requirements?",
    
    # IT Agreement
    "What's the salary for IT-03 Step 5 in 2024?",
    "What are the working hours for IT professionals?",
    
    # Employment Equity
    "What employers are covered by the Employment Equity Act?",
    "What are employment equity reporting requirements?",
    
    # Canada.ca
    "How do I apply for OAS benefits?",
    "What documents do I need for citizenship application?",
]
```

**Success Criteria**:
- ✅ Relevance @top-5: 90%+
- ✅ Correct metadata filtering
- ✅ Synthetic data disclaimer shown (jurisprudence)
- ✅ Table chunks retrieved for salary queries
- ✅ Bilingual retrieval working (EN ↔ FR)

---

## File Locations Quick Reference

### Ingested Data (Current)
```
data/ingested/
├── legal/
│   └── jurisprudence_legal_docs_20251208_115158.json  (AssistMe + Jurisprudence)
├── specific_urls/
│   └── specific_urls_20251209_013238.json              (Employment Equity + IT Agreement)
└── canada_ca/
    ├── canada_ca_en_20251208_115223.json               (632 pages EN)
    └── canada_ca_fr_20251208_115223.json               (625 pages FR)
```

### Documentation (Read These)
```
docs/
├── IT-COLLECTIVE-AGREEMENT-TABLE-ANALYSIS.md           (400+ lines, table chunking strategy)
├── JURISPRUDENCE-DATA-STATUS.md                        (synthetic data warning)
├── EMPLOYMENT-EQUITY-ACT-INGESTION-STATUS.md           (XML extraction failure)
├── JURISPRUDENCE-SOURCES-IMPLEMENTATION.md             (CanLII replacement plan)
├── DATA-SOURCE-TESTING-RESULTS.md                      (validation test results)
├── INGESTION-ARCHITECTURE.md                           (loader framework, 13 loaders)
└── INGESTION-STATUS-REPORT.md                          (comprehensive status)
```

### Scripts (Current)
```
eva-rag/
├── ingest_legal_documents.py       (AssistMe + Jurisprudence)
├── ingest_specific_urls.py         (Employment Equity + IT Agreement)
├── ingest_canada_ca.py             (Web crawl EN + FR)
├── ingest_canadalife.py            (Canada Life booklets - needs re-run)
├── test_data_sources.py            (Validation: 3/3 passed)
└── analyze_tables.py               (Table detection)
```

### Scripts to Create (Chunking Phase)
```
scripts/
├── add_synthetic_flag.py           (P0 - Add flag to jurisprudence)
├── investigate_french_tables.py    (P1 - Check French table structure)
├── chunk_assistme.py               (P1 - Chunk 104 articles)
├── chunk_employment_equity.py      (P1 - Chunk legislation)
├── chunk_it_agreement.py           (P0 - Table-aware chunking)
├── chunk_canada_ca.py              (P1 - Chunk 1,257 pages)
├── generate_embeddings.py          (P1 - Azure OpenAI embeddings)
├── index_to_azure_search.py        (P1 - Hybrid search index)
└── test_rag_queries.py             (P2 - Validate retrieval)
```

### New Modules to Create (Table Chunking)
```
src/eva_rag/chunking/
├── __init__.py
├── table_extractor.py              (P0 - Extract tables and positions)
├── table_aware_chunker.py          (P0 - Preserve table integrity)
└── semantic_chunker.py             (P1 - Standard chunking)
```

---

## Commands Quick Reference

### Resume Work
```powershell
# Navigate to repo
cd "c:\Users\marco\Documents\_AI Dev\EVA Suite\eva-rag"

# Activate Poetry environment (if needed)
poetry shell

# Run tests to verify data integrity
python test_data_sources.py
# Expected: 3/3 PASSED

# Read critical documentation
code docs/IT-COLLECTIVE-AGREEMENT-TABLE-ANALYSIS.md
code docs/JURISPRUDENCE-DATA-STATUS.md
```

### Start Phase 1 (Pre-Chunking Fixes)
```powershell
# 1. Implement table-aware chunking
code src/eva_rag/chunking/table_extractor.py
code src/eva_rag/chunking/table_aware_chunker.py
code test_table_chunking.py

# 2. Add synthetic flag
python scripts/add_synthetic_flag.py

# 3. Investigate French tables
python scripts/investigate_french_tables.py
```

### Validate Phase 1 Complete
```powershell
# Test table chunking
python test_table_chunking.py
# Expected: All 25 tables intact (EN + FR)

# Verify synthetic flag
cat data/ingested/legal/jurisprudence_legal_docs_20251208_115158_with_synthetic_flag.json | Select-String "is_synthetic"
# Expected: 4 occurrences (all true)
```

---

## Success Criteria Checklist

### Phase 1 (Before Moving to Phase 2)
- [ ] Table-aware chunking implemented
- [ ] Test script passes: Zero tables split
- [ ] All 25 EN tables detected and preserved
- [ ] All 25 FR tables detected (or investigation complete)
- [ ] Synthetic flag added to all 4 jurisprudence documents
- [ ] Flag preserved during chunking
- [ ] Disclaimer logic implemented for RAG responses

### Phase 2 (Chunking Complete)
- [ ] AssistMe: 104 articles → ~248 chunks
- [ ] Employment Equity: 5 docs → ~470 chunks
- [ ] IT Agreement: 2 docs → ~175 chunks (25 tables + 150 text)
- [ ] Canada.ca: 1,257 pages → ~2,800 chunks
- [ ] Total: ~3,693 chunks created
- [ ] All metadata preserved in chunks

### Phase 3 (RAG Ready)
- [ ] All chunks embedded (1536 dimensions)
- [ ] Azure AI Search index created
- [ ] Hybrid search operational (vector + keyword)
- [ ] Metadata filters working
- [ ] Test queries: 90%+ relevance @top-5

---

## Troubleshooting

### Issue: Table Detection Not Working

**Symptom**: `extract_markdown_tables()` returns 0 tables

**Fixes**:
1. Check regex pattern matches content structure
2. Try raw string: `r'pattern'` instead of `'pattern'`
3. Verify content has `full_content` field (not just `content_preview`)
4. Print first 2000 chars of content to inspect structure

---

### Issue: French Tables Not Detected

**Symptom**: 0 table markers in French version

**Investigation**:
1. Run `python scripts/investigate_french_tables.py`
2. Check for `"| Étape "` or `"| Échelon "`
3. If no markers, check if French version has different structure
4. May need to adapt regex or document as English-only feature

---

### Issue: Chunking Too Slow

**Symptom**: Processing takes >1 hour

**Fixes**:
1. Reduce chunk size: 500 → 300 tokens
2. Batch processing: Process 100 docs at a time
3. Use multiprocessing for large datasets (Canada.ca)
4. Profile with `python -m cProfile script.py`

---

### Issue: Azure OpenAI Rate Limits

**Symptom**: 429 errors during embedding generation

**Fixes**:
1. Reduce batch size: 100 → 20 chunks per request
2. Add retry logic with exponential backoff
3. Add sleep between requests: `time.sleep(0.5)`
4. Check quota in Azure portal

---

## Contact & Support

**Owner**: Marco Presta  
**Agent**: GitHub Copilot (P06-RAG)  
**POD**: POD-F  
**Repo**: eva-rag

**Key Documents**:
- Agile Framework: `../eva-orchestrator/docs/standards/AGENTIC-FRAMEWORK-OFFICIAL.md`
- DUA Format: `../eva-orchestrator/docs/standards/DUA-FORMAT-SPECIFICATION.md`
- Copilot Instructions: `.github/copilot-instructions.md`

---

**Document Status**: ✅ COMPLETE  
**Ready to Resume**: ✅ YES  
**Next Action**: Implement table-aware chunking (Task 1)  
**Updated**: December 9, 2025
