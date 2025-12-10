# Data Ingestion Request Template

**Submitted By:** [Your Name]  
**Email:** [your.email@example.gc.ca]  
**Department/Team:** [e.g., "AICOE Knowledge Management"]  
**Date:** [YYYY-MM-DD]  
**Priority:** ☐ HIGH  ☐ MEDIUM  ☐ LOW  
**Target Completion:** [YYYY-MM-DD]

---

## 1. Project Information

**Project Name:** [e.g., "Supreme Court Decisions Ingestion"]

**Client/Stakeholder:** [e.g., "Legal Research Team"]

**Use Case:** [e.g., "Enable legal researchers to find relevant case law using natural language queries"]

**Business Objective:**  
[Describe in 2-3 sentences what business problem this solves. Example: "Currently, legal researchers spend 4-6 hours manually searching through court decisions. This ingestion will enable AI-powered search, reducing research time to 15-30 minutes per case."]

---

## 2. Data Sources

### Source 1: [Name, e.g., "Supreme Court of Canada Website"]

**URL or Location:**  
- English: https://...
- French: https://... (if applicable)

**Type:** (Check one)
- ☐ Web pages (HTML)
- ☐ PDF documents
- ☐ Excel/CSV files
- ☐ Word documents
- ☐ PowerPoint presentations
- ☐ API (provide endpoint)
- ☐ Database (provide connection details)
- ☐ Other: ____________

**Language:** (Check all that apply)
- ☐ English only
- ☐ French only
- ☐ Bilingual (both EN and FR)

**How Often Updated:**
- ☐ Daily
- ☐ Weekly
- ☐ Monthly
- ☐ Quarterly
- ☐ Annually
- ☐ One-time only (historical data)

**Estimated Volume:**  
[e.g., "20,000 historical documents", "~200 new documents per year", "5 GB of PDFs"]

**Access Requirements:**
- ☐ Public (no authentication needed)
- ☐ API Key (provide key or contact for key)
- ☐ Login credentials (provide username or contact)
- ☐ VPN required
- ☐ Database credentials
- ☐ Other: ____________

**Access Contact (if applicable):**  
[Name, email, phone of person who can provide access]

---

### Source 2: [Name] (if applicable)

[Repeat same structure as Source 1]

---

### Source 3: [Name] (if applicable)

[Repeat same structure as Source 1]

---

## 3. What Should Be Extracted

### Required Information (Must Have)

Check all that apply and add specific fields:

**Document Identification:**
- ☐ Document title/name: ____________
- ☐ Document ID/reference number: ____________
- ☐ Document type: ____________
- ☐ Date (specify which date): ____________

**Content:**
- ☐ Full text of document
- ☐ Summary/abstract
- ☐ Keywords/tags
- ☐ Section headings

**Metadata:**
- ☐ Author(s): ____________
- ☐ Organization/department: ____________
- ☐ Language: ____________
- ☐ Geographic region: ____________
- ☐ Category/classification: ____________

**Additional Fields:**
- [ ] ____________
- [ ] ____________
- [ ] ____________

### Optional Information (Nice to Have)

- [ ] ____________
- [ ] ____________
- [ ] ____________

### Content to Exclude

**What should NOT be ingested:**
- ☐ Navigation menus
- ☐ Advertisements
- ☐ Headers/footers
- ☐ Copyright notices
- ☐ Page numbers
- ☐ Images (unless needed)
- ☐ Other: ____________

---

## 4. Language Requirements

**Bilingual Handling:** (Check one)
- ☐ English only
- ☐ French only
- ☐ Both languages needed (ingest separately)
- ☐ Automatically detect language
- ☐ Link English and French versions of same document

**If bilingual:**
- ☐ Documents have parallel EN/FR versions (link them)
- ☐ Documents are mixed language (detect language per section)
- ☐ Documents are side-by-side bilingual (split them)

---

## 5. How Should Data Be Organized

### Chunking Preference

**How should long documents be split?**

- ☐ **By section** (recommended for structured documents with headings)
  - Better for: Legal documents, policy documents, reports
  - Preserves document structure
  
- ☐ **Fixed size chunks** (simpler, faster)
  - Better for: Unstructured text, web pages
  - Chunks of equal size
  
- ☐ **Intelligent/semantic chunks** (best for Q&A)
  - Better for: FAQs, guides, conversational content
  - Groups related sentences together

**Preferred chunk size:** (Check one)
- ☐ Small (200-300 words) - Better for precise answers
- ☐ Medium (500-800 words) - Balanced approach (RECOMMENDED)
- ☐ Large (1000-1500 words) - Better for context

### Special Handling

**Does your content have special elements?**

- ☐ **Tables** - Keep table structure intact
- ☐ **Citations/References** - Link to cited sources
- ☐ **Heading hierarchy** - Preserve H1, H2, H3 structure
- ☐ **Lists** - Keep lists together
- ☐ **Images** - Extract and describe images
- ☐ **Formulas/Equations** - Preserve mathematical notation
- ☐ **Code snippets** - Preserve code formatting
- ☐ **Footnotes** - Link footnotes to main text

---

## 6. Search & Retrieval Requirements

**How will users search this data?**

**Common Query Types:** (Provide 3-5 examples of questions users will ask)

1. [e.g., "What are the privacy rights under section 8 of the Charter?"]
2. [e.g., "Show me all Supreme Court decisions from 2024"]
3. [e.g., "Find cases related to taxation and administrative law"]
4. [...]
5. [...]

**Expected Filters:** (What filters will users need?)

- ☐ Date range (from YYYY-MM-DD to YYYY-MM-DD)
- ☐ Document type
- ☐ Author/Organization
- ☐ Language (EN/FR)
- ☐ Topic/Category
- ☐ Geographic region
- ☐ Other: ____________

**Expected Results:** (What should search results include?)

- ☐ Document title
- ☐ Short summary
- ☐ Date
- ☐ Link to full document
- ☐ Relevant excerpt/snippet
- ☐ Other: ____________

---

## 7. Security & Privacy

**Data Classification:** (Check one)
- ☐ Public
- ☐ Protected A
- ☐ Protected B
- ☐ Protected C
- ☐ Classified

**Privacy Concerns:**

**Does this data contain personal information?**
- ☐ No personal information
- ☐ May contain names (redact)
- ☐ May contain contact information (redact)
- ☐ May contain other PII: ____________

**Access Control:**

**Who should be able to access this data?**
- ☐ Public (anyone)
- ☐ Government of Canada employees only
- ☐ Specific department: ____________
- ☐ Specific team: ____________
- ☐ Specific individuals (provide list): ____________

**Compliance Requirements:**
- ☐ Privacy Act compliance required
- ☐ Access to Information Act compliance required
- ☐ Official Languages Act (bilingual output required)
- ☐ WCAG 2.2 AA accessibility required
- ☐ Other: ____________

---

## 8. Success Criteria

**How will we know this ingestion is successful?**

Check all that apply and specify targets:

- ☐ **Completeness:** _____% of documents successfully ingested (recommend: 95%+)
- ☐ **Accuracy:** All required metadata fields populated
- ☐ **Searchability:** Users can find relevant documents in < ___ seconds
- ☐ **Bilingual:** English and French versions correctly linked
- ☐ **Quality:** Content is clean (no HTML artifacts, navigation, etc.)
- ☐ **Other:** ____________

**Acceptance Test:**

[Describe how you will validate the results. Example: "I will search for 10 known cases and verify that all are found with correct metadata."]

---

## 9. Timeline & Resources

**Target Start Date:** [YYYY-MM-DD]

**Target Completion Date:** [YYYY-MM-DD]

**Urgency:** (Why is this timeline needed?)
[e.g., "Needed for Q2 2025 product launch", "Supporting executive decision by March 2025"]

**Recurring Ingestion:**
- ☐ No, one-time ingestion only
- ☐ Yes, recurring ingestion needed

**If recurring, how often:**
- ☐ Daily (overnight)
- ☐ Weekly (day: ______)
- ☐ Monthly (date: ______)
- ☐ Other: ____________

**Resources Available:**

- ☐ API credentials (if needed)
- ☐ Database access (if needed)
- ☐ Sample documents for testing (provide 5-10 samples)
- ☐ Subject matter expert for validation (name: ____________)
- ☐ Budget for paid APIs/services
- ☐ Other: ____________

---

## 10. Additional Notes

[Any other context, constraints, or requirements that haven't been covered above]

---

## 11. Approval & Contact

**Submitted By:**
- Name: ____________
- Title: ____________
- Department: ____________
- Email: ____________
- Phone: ____________

**Manager Approval:**
- Name: ____________
- Title: ____________
- Email: ____________
- Signature: ____________
- Date: ____________

---

## Submission Instructions

**Once completed:**

1. Save this file as: `data-sources/[project-name]/ingestion-request.md`
   - Example: `data-sources/scc-decisions/ingestion-request.md`

2. Attach 5-10 sample documents (if available)

3. Submit via ONE of the following:
   - **Slack:** Post in #eva-rag-ingestion channel
   - **Email:** Send to eva-rag-team@example.gc.ca
   - **GitHub:** Create issue in eva-rag repo with "Data Ingestion Request" label

**What happens next:**

1. **Within 2 business days:** Dev team reviews and confirms feasibility
2. **Within 1 week:** Technical specification created (requirements.json)
3. **Within 2 weeks:** Pipeline generated and tested with sample data
4. **Within 3 weeks:** Full ingestion executed and validated
5. **Go-live:** Data available for search and retrieval

**Questions?**
- Slack: #eva-rag-support
- Email: eva-rag-team@example.gc.ca
- Office Hours: Thursdays 2-3 PM ET (Teams link in Slack)

---

**Template Version:** 1.0  
**Last Updated:** December 8, 2024  
**Template Location:** `data-sources/_templates/ingestion-request.md`
