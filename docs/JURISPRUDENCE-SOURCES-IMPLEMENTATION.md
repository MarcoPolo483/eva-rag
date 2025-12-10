# Jurisprudence Data Sources - Implementation Plan

**Date**: December 9, 2025  
**Target**: 100 cases per source (300+ total)  
**Status**: Ready to implement

---

## Data Sources (Canadian Case Law)

### 1. 🏛️ Supreme Court of Canada (SCC)
**Target**: 100 recent decisions  
**Source**: CanLII API or bulk downloads  
**URL**: https://www.canlii.org/en/ca/scc/

**Coverage**:
- Constitutional law
- Charter challenges
- Administrative law
- Criminal law
- Civil appeals

**API Details**:
- **CanLII API**: https://www.canlii.org/en/info/api.html
- **Free tier**: Available with registration
- **Format**: XML, JSON, HTML
- **Rate limit**: 1 request/second
- **Bulk download**: Available for research

**Recommended Selection**:
- Years: 2020-2024 (last 5 years)
- ~20 decisions per year
- Mix of unanimous and split decisions
- Variety of legal areas

**Metadata to Extract**:
```python
{
  "citation": "2024 SCC 1",
  "decision_date": "2024-01-15",
  "docket_number": "40123",
  "court": "Supreme Court of Canada",
  "judges": ["Wagner C.J.", "Karakatsanis J.", ...],
  "parties": {"appellant": "Smith", "respondent": "Canada (Attorney General)"},
  "topics": ["Charter s. 2(b)", "Freedom of expression", "Digital communications"],
  "statutes_considered": ["Canadian Charter of Rights and Freedoms", "Digital Communications Act"],
  "disposition": "Appeal allowed",
  "bilingual": true,
  "languages": ["en", "fr"],
  "full_text_length": 45000,
  "headnote_length": 3000
}
```

---

### 2. 📋 Federal Court of Appeal (FCA)
**Target**: 100 recent decisions  
**Source**: CanLII  
**URL**: https://www.canlii.org/en/ca/fca/

**Coverage**:
- Immigration appeals
- Tax appeals
- Employment Insurance appeals
- Federal administrative tribunal appeals
- Crown liability

**Why Include**:
- Direct relevance to federal government programs
- Employment Insurance Tribunal appeals (connects to Programs & Services)
- Immigration decisions (connects to ESDC mandate)
- Administrative law precedents

**Recommended Selection**:
- Years: 2020-2024
- Focus on: Immigration (30%), Tax (20%), Employment (20%), Administrative (30%)
- Include: Both allowed and dismissed appeals

**Metadata to Extract**:
```python
{
  "citation": "2024 FCA 45",
  "decision_date": "2024-03-08",
  "docket_number": "A-123-23",
  "court": "Federal Court of Appeal",
  "judges": ["Webb J.A.", "Laskin J.A.", "Stratas J.A."],
  "lower_court": {"court": "Federal Court", "citation": "2023 FC 456", "judge": "Southcott J."},
  "parties": {"appellant": "Jones", "respondent": "Minister of Employment"},
  "topics": ["Employment Insurance", "Standard of review", "Reasonableness"],
  "tribunal": "Employment Insurance Tribunal - Appeal Division",
  "disposition": "Appeal dismissed",
  "bilingual": true
}
```

---

### 3. 🏢 Federal Court (FC)
**Target**: 100 recent decisions  
**Source**: CanLII  
**URL**: https://www.canlii.org/en/ca/fct/

**Coverage**:
- Judicial review of federal tribunals
- Immigration and refugee matters
- Tax disputes
- Employment Insurance appeals
- Federal Crown litigation

**Why Include**:
- First level of judicial review for federal programs
- High volume of Employment Insurance cases
- Immigration decisions (large ESDC portfolio)
- Connects to Government Programs & Services use case

**Recommended Selection**:
- Years: 2022-2024 (more recent for relevance)
- Focus on: Immigration/Refugee (40%), Employment (20%), Tax (20%), Other (20%)
- Include: Both applications granted and dismissed

**Metadata to Extract**:
```python
{
  "citation": "2024 FC 234",
  "decision_date": "2024-05-15",
  "file_number": "T-456-23",
  "court": "Federal Court",
  "judge": "Manson J.",
  "parties": {"applicant": "ABC Corp.", "respondent": "Minister of National Revenue"},
  "topics": ["Judicial review", "Administrative law", "Income Tax Act"],
  "application_type": "judicial_review",
  "tribunal_decision_under_review": {"tribunal": "Tax Court of Canada", "date": "2023-08-10"},
  "disposition": "Application granted",
  "bilingual": false,
  "language": "en"
}
```

---

## Implementation Plan

### Phase 1: CanLII API Integration (Week 1)

#### Step 1: API Registration & Testing
```python
# src/eva_rag/loaders/canlii_loader.py
import requests
from typing import List, Optional
from datetime import datetime

class CanLIILoader:
    """Loader for CanLII case law API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.canlii.org/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def search_cases(
        self,
        court: str,  # "ca/scc", "ca/fca", "ca/fct"
        year_from: int,
        year_to: int,
        limit: int = 100
    ) -> List[dict]:
        """Search for cases by court and date range."""
        endpoint = f"{self.base_url}/caseBrowse/{court}"
        params = {
            "offset": 0,
            "resultCount": limit,
            "publishedBefore": f"{year_to}-12-31",
            "publishedAfter": f"{year_from}-01-01"
        }
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["cases"]
    
    def get_case_full_text(self, case_id: str, language: str = "en") -> dict:
        """Retrieve full case text and metadata."""
        endpoint = f"{self.base_url}/cases/{case_id}"
        params = {"lang": language}
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
```

#### Step 2: Metadata Extraction
```python
def extract_case_metadata(case_json: dict) -> dict:
    """Extract structured metadata from CanLII case JSON."""
    return {
        "citation": case_json.get("citation"),
        "decision_date": case_json.get("decisionDate"),
        "docket_number": case_json.get("docketNumber"),
        "court": case_json.get("court", {}).get("name"),
        "court_id": case_json.get("court", {}).get("id"),
        "judges": [j["name"] for j in case_json.get("judges", [])],
        "parties": extract_parties(case_json.get("title")),
        "keywords": case_json.get("keywords", []),
        "topics": case_json.get("topics", []),
        "cited_legislation": [
            {
                "title": leg.get("title"),
                "citation": leg.get("citation"),
                "sections": leg.get("sections", [])
            }
            for leg in case_json.get("citedLegislation", [])
        ],
        "cited_cases": [
            {
                "citation": cite.get("citation"),
                "style": cite.get("style")
            }
            for cite in case_json.get("citedCases", [])
        ],
        "language": case_json.get("language"),
        "url": case_json.get("url")
    }
```

#### Step 3: Bilingual Content Handling
```python
def ingest_case_bilingual(case_id: str, loader: CanLIILoader) -> List[ExtractedDocument]:
    """Ingest both EN and FR versions of a case."""
    documents = []
    
    for lang in ["en", "fr"]:
        try:
            case_data = loader.get_case_full_text(case_id, lang)
            
            doc = ExtractedDocument(
                text=case_data["fullText"],
                metadata={
                    **extract_case_metadata(case_data),
                    "language": lang,
                    "client": "jurisprudence",
                    "use_case": "Legal Research",
                    "document_type": "case_law",
                    "data_category": "Legal Documents",
                    "is_synthetic": False  # Real case law
                }
            )
            documents.append(doc)
        except Exception as e:
            print(f"Failed to load {lang} version: {e}")
    
    return documents
```

### Phase 2: Batch Ingestion Script (Week 1)

```python
# ingest_jurisprudence.py
"""
Ingest 100 cases from each Canadian court source.

Usage:
    python ingest_jurisprudence.py --api-key YOUR_KEY --courts scc fca fct
"""
import argparse
from pathlib import Path
from datetime import datetime
from eva_rag.loaders.canlii_loader import CanLIILoader, extract_case_metadata

def ingest_court_cases(court_id: str, loader: CanLIILoader, limit: int = 100):
    """Ingest cases from a specific court."""
    print(f"\n{'='*80}")
    print(f"INGESTING {court_id.upper()} CASES")
    print(f"{'='*80}\n")
    
    # Search for cases
    cases = loader.search_cases(
        court=f"ca/{court_id}",
        year_from=2020,
        year_to=2024,
        limit=limit
    )
    
    print(f"Found {len(cases)} cases")
    
    all_documents = []
    for i, case in enumerate(cases, 1):
        print(f"\n[{i}/{len(cases)}] {case.get('citation', 'N/A')}")
        
        try:
            # Ingest both EN and FR versions
            case_id = case["caseId"]
            docs = ingest_case_bilingual(case_id, loader)
            all_documents.extend(docs)
            
            print(f"  ✅ Ingested {len(docs)} language versions")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Save results
    output_dir = Path("data/ingested/jurisprudence")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{court_id}_cases_{timestamp}.json"
    
    save_ingestion_results(all_documents, output_file)
    
    return all_documents


def main():
    parser = argparse.ArgumentParser(description="Ingest Canadian case law")
    parser.add_argument("--api-key", required=True, help="CanLII API key")
    parser.add_argument(
        "--courts",
        nargs="+",
        choices=["scc", "fca", "fct"],
        default=["scc", "fca", "fct"],
        help="Courts to ingest from"
    )
    parser.add_argument("--limit", type=int, default=100, help="Cases per court")
    
    args = parser.parse_args()
    
    loader = CanLIILoader(args.api_key)
    
    all_documents = []
    for court in args.courts:
        court_docs = ingest_court_cases(court, loader, args.limit)
        all_documents.extend(court_docs)
    
    # Summary
    print(f"\n{'='*80}")
    print("INGESTION SUMMARY")
    print(f"{'='*80}\n")
    
    by_court = {}
    for doc in all_documents:
        court = doc.metadata.get("court_id", "unknown")
        by_court[court] = by_court.get(court, 0) + 1
    
    for court, count in sorted(by_court.items()):
        print(f"{court.upper()}: {count} documents")
    
    print(f"\nTotal: {len(all_documents)} documents")
    print(f"Total characters: {sum(len(d.text) for d in all_documents):,}")
    

if __name__ == "__main__":
    main()
```

### Phase 3: Data Validation (Week 1)

```python
# validate_jurisprudence.py
"""Validate ingested case law data quality."""

def validate_case_metadata(doc: dict) -> List[str]:
    """Check for required metadata fields."""
    issues = []
    
    required = [
        "citation",
        "decision_date",
        "court",
        "judges",
        "language",
        "is_synthetic"
    ]
    
    for field in required:
        if field not in doc.get("metadata", {}):
            issues.append(f"Missing required field: {field}")
    
    # Check is_synthetic flag
    if doc.get("metadata", {}).get("is_synthetic") != False:
        issues.append("is_synthetic must be False for real cases")
    
    # Check content length
    if len(doc.get("content_preview", "")) < 1000:
        issues.append(f"Suspiciously short content: {len(doc['content_preview'])} chars")
    
    # Check citation format
    citation = doc.get("metadata", {}).get("citation", "")
    if not re.match(r"\d{4}\s+(SCC|FCA|FC)\s+\d+", citation):
        issues.append(f"Invalid citation format: {citation}")
    
    return issues


def main():
    """Run validation on all ingested cases."""
    ingested_dir = Path("data/ingested/jurisprudence")
    
    for json_file in ingested_dir.glob("*.json"):
        print(f"\nValidating {json_file.name}...")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_issues = 0
        for i, doc in enumerate(data):
            issues = validate_case_metadata(doc)
            if issues:
                print(f"\n  Document {i+1}: {doc.get('metadata', {}).get('citation', 'N/A')}")
                for issue in issues:
                    print(f"    ❌ {issue}")
                total_issues += len(issues)
        
        if total_issues == 0:
            print(f"  ✅ All {len(data)} documents valid")
        else:
            print(f"\n  ⚠️  {total_issues} issues found across {len(data)} documents")
```

---

## Expected Dataset Summary

### Total Cases: 300+

| Court | Cases | Languages | Total Docs | Avg Length | Total Size |
|-------|-------|-----------|------------|------------|------------|
| SCC | 100 | EN + FR | 200 | 45,000 chars | 9 MB |
| FCA | 100 | EN + FR | 200 | 30,000 chars | 6 MB |
| FC | 100 | EN (mostly) | 120 | 25,000 chars | 3 MB |
| **TOTAL** | **300** | **Mixed** | **520** | **33,000** | **18 MB** |

### Coverage by Legal Area

- **Constitutional Law**: 20% (60 cases)
- **Administrative Law**: 30% (90 cases)
- **Immigration**: 25% (75 cases)
- **Employment/Labour**: 10% (30 cases)
- **Tax**: 10% (30 cases)
- **Other**: 5% (15 cases)

### Bilingual Coverage

- **Fully Bilingual**: SCC (100%), FCA (100%)
- **Primarily English**: FC (~60% bilingual, 40% English only)
- **Total Bilingual Documents**: ~460 of 520 (88%)

---

## CanLII API Registration

### Steps to Get API Key

1. **Register**:
   - Go to: https://www.canlii.org/en/info/api.html
   - Click "Request API Access"
   - Fill out form (name, email, research purpose)

2. **Justification** (for form):
   ```
   Purpose: Government of Canada RAG (Retrieval-Augmented Generation) system
   Organization: ESDC (Employment and Social Development Canada)
   Use Case: Enable natural language search of Canadian case law for:
     - Legal research by government lawyers
     - Policy analysis by government analysts
     - Public service to citizens
   Volume: ~300 cases initial load, ongoing updates
   Non-commercial: Government research and public service
   ```

3. **Wait for Approval**: Usually 1-3 business days

4. **API Key Storage**:
   ```bash
   # Store in environment variable
   export CANLII_API_KEY="your_key_here"
   
   # Or in .env file
   echo "CANLII_API_KEY=your_key_here" >> .env
   ```

---

## Alternative: Bulk Download (If API Unavailable)

### Option 1: CanLII Bulk Data

CanLII provides bulk downloads for research:
- Format: XML files
- Coverage: All courts, all years
- Size: ~50 GB compressed
- Request: Contact CanLII directly for research access

### Option 2: Manual Download + XMLLoader

Use existing XMLLoader to process CanLII XML files:

```python
# If you have XML files from CanLII bulk download
from eva_rag.loaders.xml_loader import XMLLoader

loader = XMLLoader()
doc = loader.load("path/to/2024_SCC_1.xml", "2024_SCC_1.xml")
```

---

## Next Steps (Priority Order)

### P0 (This Week)
1. ✅ Document data source specifications (this file)
2. ⏳ Register for CanLII API key
3. ⏳ Implement CanLIILoader class
4. ⏳ Test with 5 sample cases (1 SCC, 2 FCA, 2 FC)
5. ⏳ Validate metadata extraction

### P1 (Week 2)
6. ⏳ Batch ingest 100 SCC cases
7. ⏳ Batch ingest 100 FCA cases
8. ⏳ Batch ingest 100 FC cases
9. ⏳ Run validation script
10. ⏳ Fix any data quality issues

### P2 (Week 3)
11. ⏳ Update ingest_legal_documents.py to use CanLII
12. ⏳ Remove synthetic case generation code
13. ⏳ Add is_synthetic: False validation
14. ⏳ Document citation format standards
15. ⏳ Create RAG test queries for legal research

---

## Success Criteria

✅ **300+ real cases ingested** (not synthetic)  
✅ **100 cases per court** (SCC, FCA, FC)  
✅ **Bilingual coverage** (EN + FR where available)  
✅ **Complete metadata** (citation, judges, topics, disposition)  
✅ **Unique citations** (no duplicates like current synthetic data)  
✅ **Full text available** (not just headnotes)  
✅ **is_synthetic: false** flag on all documents  
✅ **Pass validation** (0 critical issues)  

---

**Document Owner**: P04-LIB (Librarian) + P06-RAG (RAG Engineer)  
**Status**: READY TO IMPLEMENT  
**Blocked By**: CanLII API key registration  
**Estimated Time**: 2-3 weeks (including API approval wait)
