"""Validate Employment Insurance jurisprudence ingestion results."""
import json
from pathlib import Path
from collections import Counter

def validate_ei_cases(json_file: Path):
    """Validate the EI case distribution."""
    print("=" * 80)
    print("VALIDATION: EMPLOYMENT INSURANCE JURISPRUDENCE")
    print("=" * 80)
    print()
    
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total documents: {len(data)}")
    print()
    
    # By source
    sources = Counter(d['metadata']['source'] for d in data)
    print("By Source:")
    for source, count in sorted(sources.items()):
        en_count = len([d for d in data if d['metadata']['source'] == source and d['language'] == 'en'])
        fr_count = len([d for d in data if d['metadata']['source'] == source and d['language'] == 'fr'])
        print(f"  {source}: {count} total ({en_count} EN + {fr_count} FR)")
    print()
    
    # By language
    languages = Counter(d['language'] for d in data)
    print("By Language:")
    for lang, count in sorted(languages.items()):
        print(f"  {lang}: {count}")
    print()
    
    # Use cases (should all be Employment Insurance)
    use_cases = set(d['metadata']['use_case'] for d in data)
    print(f"Use Cases: {use_cases}")
    print()
    
    # Case types
    case_types = Counter(d['case_type'] for d in data)
    print("By EI Case Type:")
    for case_type, count in sorted(case_types.items()):
        print(f"  {case_type}: {count}")
    print()
    
    # Sample cases
    print("Sample Cases (first 3):")
    for i, doc in enumerate(data[:3], 1):
        print(f"\n{i}. Citation: {doc['citation']}")
        print(f"   Court: {doc['court']}")
        print(f"   Source: {doc['metadata']['source']}")
        print(f"   Language: {doc['language']}")
        print(f"   Type: {doc['case_type']}")
        print(f"   Topics: {doc['topics']}")
        print(f"   Length: {doc['content_length']:,} chars")
    print()
    
    # Validation checks
    print("=" * 80)
    print("VALIDATION CHECKS")
    print("=" * 80)
    print()
    
    checks = []
    
    # Check total count
    if len(data) == 800:
        checks.append("✅ Total count: 800 (PASS)")
    else:
        checks.append(f"❌ Total count: {len(data)} (FAIL - expected 800)")
    
    # Check language distribution
    if languages.get('en', 0) == 400 and languages.get('fr', 0) == 400:
        checks.append("✅ Language distribution: 400 EN + 400 FR (PASS)")
    else:
        checks.append(f"❌ Language distribution: {languages.get('en', 0)} EN + {languages.get('fr', 0)} FR (FAIL)")
    
    # Check source distribution
    source_check = all(count == 200 for count in sources.values()) and len(sources) == 4
    if source_check:
        checks.append("✅ Source distribution: 200 per source × 4 sources (PASS)")
    else:
        checks.append(f"❌ Source distribution: {dict(sources)} (FAIL)")
    
    # Check use case
    if use_cases == {'Employment Insurance'}:
        checks.append("✅ Use case: All Employment Insurance (PASS)")
    else:
        checks.append(f"❌ Use case: {use_cases} (FAIL)")
    
    # Check EI case types
    ei_types = ['ei_voluntary_leaving', 'ei_misconduct', 'ei_availability', 
                'ei_job_search', 'ei_allocation', 'ei_false_declaration']
    if all(ct.startswith('ei_') for ct in case_types.keys()):
        checks.append("✅ Case types: All EI-specific (PASS)")
    else:
        checks.append(f"❌ Case types: Non-EI types found (FAIL)")
    
    # Check synthetic flag
    all_synthetic = all(d['metadata'].get('is_synthetic') == True for d in data)
    if all_synthetic:
        checks.append("✅ Synthetic flag: All cases marked synthetic (PASS)")
    else:
        checks.append(f"❌ Synthetic flag: Some cases not marked (FAIL)")
    
    for check in checks:
        print(check)
    
    print()
    print("=" * 80)
    
    # Summary
    passed = sum(1 for c in checks if c.startswith('✅'))
    total = len(checks)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
    else:
        print(f"⚠️  SOME CHECKS FAILED ({passed}/{total} passed)")
    
    print("=" * 80)
    print()


if __name__ == "__main__":
    json_file = Path("data/ingested/jurisprudence/jurisprudence_ei_4sources_20251209_053450.json")
    validate_ei_cases(json_file)
