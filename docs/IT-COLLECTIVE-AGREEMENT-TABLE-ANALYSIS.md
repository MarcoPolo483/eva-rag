# IT Collective Agreement - Table Structure Analysis

## Executive Summary

The IT Collective Agreement contains **25 markdown salary tables** with special structural requirements that need careful handling during chunking, embedding, and RAG retrieval.

**Key Finding**: These tables use **markdown pipe syntax** (`|`-delimited) with:
- Multi-row headers (effective dates with special symbols: `$`, `A`, `W1`, `B`, `X`, `C`, `Y`, `D`, `Z`)
- 8 salary steps (Step 1 through Step 8)
- Progressive pay increases over multiple years (2020-2024)
- Special adjustment rows (Pay Line Adjustments, Wage Adjustments)
- Dollar amounts with commas (e.g., `$60,696`)

---

## Table Structure Details

### 1. Classification Levels

Tables exist for IT classification levels:
- **IT-01** (Entry level)
- **IT-02** (Intermediate)
- **IT-03** (Senior)
- **IT-04** (Principal)
- **IT-05** (Director level - appears to have different structure)

### 2. Table Format

**Standard Table Structure** (IT-01 through IT-04):

```markdown
| Effective date | Step 1 | Step 2 | Step 3 | Step 4 | Step 5 | Step 6 | Step 7 | Step 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $) December 22, 2020 | 60,696 | 62,940 | 65,180 | 67,408 | 69,634 | 71,861 | 74,086 | 78,216 |
| A) December 22, 2021 | 61,606 | 63,884 | 66,158 | 68,419 | 70,679 | 72,939 | 75,197 | 79,389 |
| W1) December 22, 2021 – Pay Line Adjustment | 62,530 | 64,842 | 67,150 | 69,445 | 71,739 | 74,033 | 76,325 | 80,580 |
| B) December 22, 2022 | 64,719 | 67,111 | 69,500 | 71,876 | 74,250 | 76,624 | 78,996 | 83,400 |
| X) December 22, 2022 – Wage Adjustment | 65,528 | 67,950 | 70,369 | 72,774 | 75,178 | 77,582 | 79,983 | 84,443 |
| C) December 22, 2023 | 67,494 | 69,989 | 72,480 | 74,957 | 77,433 | 79,909 | 82,382 | 86,976 |
| Y) December 22, 2023 – Pay Line Adjustment | 67,831 | 70,339 | 72,842 | 75,332 | 77,820 | 80,309 | 82,794 | 87,411 |
| D) December 22, 2024 | 69,188 | 71,746 | 74,299 | 76,839 | 79,376 | 81,915 | 84,450 | 89,159 |
| Z) December 22, 2024 – Wage Adjustment | 69,361 | 71,925 | 74,485 | 77,031 | 79,574 | 82,120 | 84,661 | 89,382 |
```

**Key Features**:
- **9 data rows** per table (base + adjustments over 4 years)
- **8 salary steps** (columns 2-9)
- **Effective dates** in column 1 with special prefixes:
  - `$)` = Base rates (December 22, 2020)
  - `A)`, `B)`, `C)`, `D)` = Annual economic increases
  - `W1)`, `W2)` = Pay line adjustments (Year 1)
  - `X)` = Wage adjustment (Year 2)
  - `Y)` = Pay line adjustment (Year 3)
  - `Z)` = Wage adjustment (Year 4)

### 3. Additional Salary Tables

Beyond the 5 IT classification tables, there are **20 additional tables** covering:
- **Weekly rates** (IT-01 to IT-05)
- **Daily rates** (IT-01 to IT-05)
- **Hourly rates** (IT-01 to IT-05)
- **Different effective dates** (Appendix "A", "B", etc.)

**Total**: 25 markdown tables with salary information

---

## Special Handling Requirements

### ⚠️ **CRITICAL**: Why These Tables Need Special Treatment

1. **Markdown Preservation**
   - Tables use pipe syntax `|` which can break during:
     - Text splitting (mid-row splits destroy table structure)
     - LLM processing (markdown may be interpreted as formatting)
     - Vector embedding (table structure lost in embeddings)
   
2. **Semantic Coherence**
   - Each table represents a **single logical unit**:
     - Classification level (e.g., IT-03)
     - All salary steps for that level
     - All effective dates and adjustments
   - Splitting a table across chunks makes it unusable

3. **Contextual Dependencies**
   - Column headers (Step 1, Step 2, etc.) must stay with data
   - Row prefixes ($, A, W1, etc.) require explanation
   - Salary values are meaningless without classification level context

4. **Query Patterns**
   - Users ask: "What's the salary for IT-03 Step 5?"
   - RAG needs: Full table + classification level + current date
   - Cannot answer from partial table

---

## Recommended Chunking Strategy

### **Option 1: Table-Aware Semantic Chunking** ⭐ (RECOMMENDED)

**Implementation**:
```python
def chunk_collective_agreement(content: str, chunk_size: int = 500, overlap: int = 100):
    """
    Chunk collective agreement with table preservation.
    """
    chunks = []
    
    # Step 1: Extract all tables and their positions
    table_pattern = r'\|[^\n]*Step[^\n]*\|[^\n]*\n\|[-\s|]+\|[^\n]*\n(?:\|[^\n]+\|[^\n]*\n)+'
    tables = list(re.finditer(table_pattern, content))
    
    # Step 2: Mark table regions as "do not split"
    table_regions = [(m.start(), m.end()) for m in tables]
    
    # Step 3: Chunk non-table content normally
    position = 0
    for table_start, table_end in table_regions:
        # Chunk text before table
        if position < table_start:
            text_before = content[position:table_start]
            text_chunks = semantic_chunk(text_before, chunk_size, overlap)
            chunks.extend(text_chunks)
        
        # Add table as single chunk with context
        table_context_start = max(0, table_start - 200)  # 200 chars before
        table_context_end = min(len(content), table_end + 200)  # 200 chars after
        table_chunk = content[table_context_start:table_context_end]
        chunks.append({
            'text': table_chunk,
            'type': 'salary_table',
            'classification': extract_classification(table_chunk),  # IT-01, IT-02, etc.
            'metadata': {
                'is_table': True,
                'table_type': 'salary_rates',
                'preserve_structure': True
            }
        })
        
        position = table_end
    
    # Step 4: Chunk remaining text after last table
    if position < len(content):
        remaining = content[position:]
        text_chunks = semantic_chunk(remaining, chunk_size, overlap)
        chunks.extend(text_chunks)
    
    return chunks
```

**Advantages**:
- ✅ Preserves table structure completely
- ✅ Adds context before/after table
- ✅ Tags tables for special retrieval
- ✅ Allows normal chunking for narrative text

### **Option 2: Dual Representation**

Store both:
1. **Markdown table** (for display)
2. **Structured JSON** (for queries)

**Example JSON**:
```json
{
  "classification": "IT-03",
  "effective_date": "2024-12-22",
  "rate_type": "annual",
  "currency": "CAD",
  "steps": {
    "1": 101343,
    "2": 104833,
    "3": 108324,
    "4": 111817,
    "5": 115306,
    "6": 118791,
    "7": 122281,
    "8": 125914
  },
  "adjustment_type": "wage_adjustment",
  "adjustment_code": "Z",
  "original_markdown": "| Z) December 22, 2024 – Wage Adjustment | 101,343 | 104,833 | ..."
}
```

**Advantages**:
- ✅ Enables precise queries (filter by classification, step, date)
- ✅ Preserves original for display
- ✅ Supports both semantic and structured retrieval

### **Option 3: Table-to-Text Conversion**

Convert tables to natural language:

**Original**:
```markdown
| $) December 22, 2020 | 60,696 | 62,940 | 65,180 | ... |
```

**Converted**:
```
For IT-01 employees effective December 22, 2020 (base rates):
- Step 1: $60,696 annually
- Step 2: $62,940 annually
- Step 3: $65,180 annually
[...]
```

**Advantages**:
- ✅ Works with standard chunking
- ✅ More LLM-friendly format
- ❌ Loses visual table structure
- ❌ Harder to maintain accuracy

---

## Appendix Structure

### Appendices Containing Tables

From analysis, the following appendices contain salary tables:

| Appendix | Content Type | Tables |
|----------|-------------|--------|
| **Appendix A** | Rates of Pay (not found in initial scan) | Unknown |
| **Appendix B** | IT Group rates (weekly, daily, hourly) | 15+ tables |
| **Appendix H** | Severance pay provisions | Possibly |
| **Appendix L** | Retroactive payment calculations | Text-based |

**Note**: Initial regex search found Appendix B at position ~218,698 with explicit salary tables.

### Other Appendices (Non-Salary)

- **Appendix H**: Severance pay and termination benefits
- **Appendix I**: Workforce adjustment procedures  
- **Appendix L**: Retroactive lump sum payment formulas

---

## RAG Retrieval Strategy

### Query Types

**Type 1: Specific Salary Lookup**
- Query: "What is the salary for IT-03 Step 5 in 2024?"
- Required: Full table for IT-03, identify latest 2024 rate (row Z)
- Retrieval: Metadata filter `classification=IT-03` + `is_table=true`

**Type 2: Salary Comparison**
- Query: "How much did IT-02 salaries increase from 2020 to 2024?"
- Required: Full table for IT-02, calculate delta between $ and Z rows
- Retrieval: Same as Type 1, but LLM must compare first and last rows

**Type 3: Step Progression**
- Query: "What's the difference between Step 3 and Step 4 for IT-04?"
- Required: Any row from IT-04 table, calculate Step 4 - Step 3
- Retrieval: Table for IT-04 with step columns

**Type 4: General Policy**
- Query: "How many salary steps are there for IT positions?"
- Required: Any table (or article text explaining step system)
- Retrieval: Semantic search "salary steps" or "pay increments"

### Recommended Metadata

For each salary table chunk:

```json
{
  "chunk_id": "it-collective-agreement-salary-table-it03-annual",
  "document_type": "collective_agreement",
  "content_type": "salary_table",
  "classification": "IT-03",
  "rate_frequency": "annual",
  "currency": "CAD",
  "effective_dates": ["2020-12-22", "2021-12-22", "2022-12-22", "2023-12-22", "2024-12-22"],
  "adjustment_types": ["base", "economic", "pay_line", "wage"],
  "step_range": "1-8",
  "min_salary": 88683,
  "max_salary": 125914,
  "is_table": true,
  "preserve_markdown": true,
  "language": "en"
}
```

### Hybrid Search Approach

**Recommended**: Use Azure AI Search **hybrid search** (semantic + keyword):

1. **Keyword filters** for precise lookups:
   - `classification eq 'IT-03'`
   - `is_table eq true`
   - `effective_dates/any(d: d ge '2024-01-01')`

2. **Semantic search** for policy questions:
   - "How are salary steps determined?"
   - "What is a pay line adjustment?"

3. **Re-ranking** by relevance:
   - Exact table matches score higher
   - Context chunks (before/after table) score lower but provide explanation

---

## Test Queries

### ✅ Should Work Well

1. "What's the current salary for an IT-03 Step 5?"
   - → Retrieves IT-03 table, identifies row Z (2024-12-22), returns Step 5 value

2. "Show me the pay scale for IT-02"
   - → Retrieves full IT-02 table, displays markdown in response

3. "How much does an IT-04 make at Step 1 vs Step 8?"
   - → Retrieves IT-04 table, calculates Step 8 - Step 1

### ⚠️ May Be Challenging

1. "What was the pay increase percentage from 2020 to 2024?"
   - → Requires LLM to calculate: (Z value - $ value) / $ value × 100
   - → May need explicit calculation instructions in prompt

2. "Compare IT-01 Step 8 to IT-02 Step 1"
   - → Requires retrieving TWO different tables
   - → RAG must fetch both classifications

3. "What's the difference between economic increase and wage adjustment?"
   - → Not in tables, requires narrative policy text (Article 47 or Appendix notes)
   - → Semantic search needed, not table retrieval

---

## Implementation Checklist

### Phase 1: Chunking (P0 - Critical)

- [ ] Implement table-aware chunking algorithm
- [ ] Extract all 25 salary tables with positions
- [ ] Add 200-char context before/after each table
- [ ] Tag chunks with `is_table=true` metadata
- [ ] Extract classification level (IT-01 to IT-05) from context
- [ ] Validate: No tables split across chunks

### Phase 2: Metadata Enrichment (P1 - High)

- [ ] Extract salary ranges (min/max) from each table
- [ ] Parse effective dates from table rows
- [ ] Identify rate frequency (annual, weekly, daily, hourly)
- [ ] Add step range (1-8)
- [ ] Tag adjustment types (base, economic, pay_line, wage)

### Phase 3: Dual Storage (P1 - High)

- [ ] Store markdown table in `full_text` field
- [ ] Convert tables to structured JSON
- [ ] Store JSON in separate `structured_data` field
- [ ] Enable both semantic and structured queries

### Phase 4: RAG Configuration (P1 - High)

- [ ] Configure Azure AI Search hybrid search
- [ ] Create filterable fields: `classification`, `is_table`, `effective_dates`
- [ ] Set up semantic ranking with table content boost
- [ ] Test retrieval precision for salary queries

### Phase 5: Testing (P2 - Medium)

- [ ] Test 10 salary lookup queries (Type 1)
- [ ] Test 5 comparison queries (Type 2)
- [ ] Test 5 policy questions (Type 4)
- [ ] Validate markdown display in RAG responses
- [ ] Check for hallucinated salary values

---

## Risk Mitigation

### **Risk 1: Table Splitting**
**Impact**: HIGH - Renders tables unusable  
**Mitigation**: Implement table-aware chunking (Option 1 above)  
**Validation**: Manual inspection of all 25 tables after chunking

### **Risk 2: LLM Hallucination**
**Impact**: CRITICAL - Incorrect salary information to employees  
**Mitigation**: 
- Always cite exact table row/column in response
- Add validation prompt: "Only use values from the retrieved table"
- Consider structured extraction over LLM generation

### **Risk 3: Query Ambiguity**
**Impact**: MEDIUM - User asks "IT-03 salary" (which step? which date?)  
**Mitigation**:
- Prompt LLM to ask clarifying questions
- Default to "current effective date" and "Step 1"
- Show full table when ambiguous

### **Risk 4: Markdown Rendering**
**Impact**: LOW - Tables display poorly in UI  
**Mitigation**:
- Test markdown rendering in target UI framework
- Fallback: Convert to HTML table for display
- Option: Store both markdown and HTML

---

## Conclusion

The IT Collective Agreement salary tables require **specialized chunking, metadata, and retrieval logic** to support accurate RAG responses. 

**Recommended Approach**:
1. Use **table-aware semantic chunking** (Option 1)
2. Store **dual representation** (markdown + JSON) (Option 2)
3. Implement **hybrid search** with metadata filters
4. Add **validation checks** to prevent hallucinations

**Success Criteria**:
- ✅ 100% of tables preserved intact in chunks
- ✅ 95%+ accuracy on salary lookup queries
- ✅ Markdown tables display correctly in UI
- ✅ No hallucinated salary values in responses

**Next Steps** (Priority Order):
1. P0: Implement table-aware chunking algorithm
2. P0: Validate all 25 tables extracted correctly
3. P1: Add structured JSON representation
4. P1: Configure Azure AI Search with filters
5. P2: Test with 20 sample queries

---

**Document Status**: ANALYSIS COMPLETE  
**Date**: December 9, 2025  
**Analyzed By**: GitHub Copilot (L2 Workflow Agent)  
**Next Owner**: P06-RAG (RAG Engineer)
