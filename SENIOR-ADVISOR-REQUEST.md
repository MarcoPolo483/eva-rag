# Request for Senior Advisor (SP01)

**Date:** December 9, 2025  
**Requestor:** GitHub Copilot (L2 Agent) working with Marco Presta  
**Classification:** UNCLASSIFIED  
**Purpose:** Advisory on architectural integration pattern

---

## Context: EVA Data Pipeline Pattern Discovery

### What Happened Today

Working in `eva-rag` repository, I completed a full data ingestion session:
- **Problem:** Azure AI Search index was empty despite integration tests passing
- **Discovery:** Applied Context Engineering principles, found 49 documents in `data-sources/`
- **Execution:** Ingested 45/49 documents (92% success), created 7,411 searchable chunks
- **Validation:** Search quality improved from 0-1/5 to 4-5/5 relevant results
- **Pattern Recognition:** Discovered I was applying Requirements Engineering to datasets

### The Pattern

I documented the approach in `EVA-DATA-PIPELINE-PATTERN.md`:
- **Core Concept:** Treat each dataset as a "client" with specific requirements
- **Template Structure:** Profile each dataset (format, constraints, chunking strategy, validation queries)
- **5 Dataset Profiles Created:** EI Act, IT Collective Agreement, Jurisprudence, PSHCP/PSDCP, AssistMe
- **Result:** Clear transformation roadmap based on client needs

### The Discovery

After documenting the pattern, Marco revealed:
> "I created EVA Data Pipeline three or four days ago in the BACKUP repo. It basically re-used the concept of P02 requirements gathering to understand the client requirements following a specific template."

Then Marco found **SP02 (EVA Data Ingestion)** in `eva-meta` repository:
- **Created:** December 5, 2025 (4 days before my re-discovery)
- **Location:** `eva-meta/docs/agents/personas/SP02-eva-data-ingestion.md`
- **Purpose:** "From brief to ingestion plan to drafted ingestion pipeline and audited corpus definition"
- **Workflow:** Brief → Plan → Pipeline → Execution → Audit
- **Autonomy:** C0-C1 (semi-automated)

**Convergent Design:** I re-discovered SP02's exact workflow without reading the specification, proving the pattern is sound.

---

## The Problem: Missing Integration

### Repository Structure (Provided to You Earlier Today)

```
eva-orchestrator/  (SDLC control plane)
├── agents/registry.yaml          # 19 agents (P01-P15 DevTools)
├── docs/                          # Generic docs
├── .eva-memory.json              # Repository context
└── scripts/                       # Automation scripts

eva-rag/  (RAG implementation)
├── src/eva_rag/
│   ├── services/
│   │   ├── ingestion_service.py
│   │   └── search_service.py
├── data-sources/                  # 49 documents
├── .eva-memory.json              # Repository context
└── EVA-DATA-PIPELINE-PATTERN.md  # NEW: Pattern documentation

eva-meta/  (The "EVA about EVA" knowledge base)
├── config/
│   └── agents-registry.yaml      # FULL agent metadata (SP01-SP08, P01-P21)
├── docs/
│   ├── agents/
│   │   ├── personas/
│   │   │   ├── SP00-personas-overview.md
│   │   │   ├── SP01-senior-advisor.md
│   │   │   ├── SP02-eva-data-ingestion.md  # ← THE PATTERN
│   │   │   └── SP06-ato-auditor.md
│   │   └── devtools/
│   │       ├── P07-testing-agent.md
│   │       ├── P12-ux-accessibility-agent.md
│   │       └── P16-P21-meta-patterns.md     # ← META PATTERNS
├── memory/
│   ├── p07/                       # Per-agent memory
│   ├── p12/
│   └── sp02/                      # ← SP02's memory location
├── tools/
│   ├── p07/                       # Per-agent tools
│   └── sp02/                      # ← SP02's tools location
└── orchestration/
    ├── p07/execution-logs/
    └── sp02/execution-logs/       # ← SP02's audit logs
```

### What's Missing

**1. Repository Awareness Gap**
- `eva-orchestrator` doesn't reference `eva-meta` in its workspace
- `eva-rag` doesn't know about SP02 or its specifications
- No cross-repository linking mechanism

**2. Pattern Documentation Gap**
- SP02 exists in `eva-meta`, but implementation is in `eva-rag`
- Dataset profiles (my document) should live somewhere SP02 can find them
- No clear "handoff" between SP02 (planning) and eva-rag (execution)

**3. Memory/Orchestration Gap**
- `eva-meta` defines memory locations (`memory/sp02/`, `orchestration/sp02/`)
- But `eva-rag` doesn't write to these locations
- Today's ingestion session has no audit trail in SP02's logs

**4. Agent Registry Gap**
- `eva-orchestrator/agents/registry.yaml` lists 19 agents (P01-P15)
- `eva-meta/config/agents-registry.yaml` lists 27+ agents (SP01-SP08, P01-P21)
- No synchronization between these registries

**5. Meta Patterns Gap**
- P16-P21 (Awareness, Swarm Review, Safety, Provenance, etc.) documented in `eva-meta`
- But no agents currently implement these patterns
- No "glue" to make P16-P21 operational across repos

---

## What I Found in eva-meta (That orchestrator Doesn't Mention)

### Service Personas (SPxx) - External-Facing Agents

| Code | Name | Purpose | Status |
|------|------|---------|--------|
| SP00 | Personas Overview | Catalog + principles | ✅ Documented |
| SP01 | Senior Advisor | High-level framing (YOU!) | ✅ Documented |
| SP02 | EVA Data Ingestion | Brief → pipeline → audit | ✅ Documented |
| SP03 | Knowledge Explorer | RAG Q&A | 📋 Defined |
| SP04 | Drafting Assistant | Bilingual text | 📋 Defined |
| SP05 | Context Summarizer | Case summaries | 📋 Defined |
| SP06 | ATO/Controls Auditor | ITSG-33 compliance | ✅ Documented |
| SP07 | Policy & Risk Coach | Plain-language constraints | 📋 Defined |
| SP08 | Training Coach | EVA adoption | 📋 Defined |

### Meta Patterns (P16-P21) - Cross-Cutting Behaviors

| Code | Pattern | Purpose |
|------|---------|---------|
| P16 | Awareness Protocol | Confidence, reflection, risks |
| P17 | Swarm PR Review | Parallel micro-agents |
| P18 | Tool/API Auto-Onboarding | Generate from OpenAPI |
| P19 | Action Classification & Safety | C0-C3 autonomy levels |
| P20 | Continuous Self-Improvement | Learn from logs |
| P21 | Provenance & Fingerprinting | Complete audit trail |

**None of these are mentioned in `eva-orchestrator` documentation.**

---

## Your Advisory Request

**Question:** How should we integrate `eva-meta` as the "source of truth" with the operational repositories (`eva-orchestrator`, `eva-rag`, etc.)?

### Specific Sub-Questions

1. **Repository Structure**
   - Should `eva-meta` be added to `EVA-2.0.code-workspace`?
   - How do repos discover and reference `eva-meta` content?
   - Should each repo's `.eva-memory.json` point to `eva-meta`?

2. **SP02 Integration**
   - Where should dataset profiles live? (eva-rag? eva-meta? both?)
   - How does SP02 "hand off" to eva-rag implementation?
   - Should `EVA-DATA-PIPELINE-PATTERN.md` move to `eva-meta/docs/patterns/`?

3. **Agent Registry Synchronization**
   - Why two registries? (`orchestrator/agents/` vs `eva-meta/config/`)
   - Should orchestrator's registry be a subset that references meta's?
   - How to keep them in sync?

4. **Memory & Orchestration Logs**
   - Should eva-rag write to `eva-meta/memory/sp02/`?
   - Should ingestion logs go to `eva-meta/orchestration/sp02/`?
   - Or should each repo maintain local logs and meta aggregates?

5. **Meta Patterns Implementation**
   - P16-P21 are documented but not implemented - is this intentional?
   - Should repos gradually adopt these patterns?
   - Is there a maturity model for pattern adoption?

6. **Workspace Configuration**
   - Current workspace: `eva-orchestrator`, `eva-rag` only
   - Should it include `eva-meta`?
   - How does this affect Copilot context loading?

---

## Constraints & Context

**What I Know:**
- SP02 was designed Dec 5, independently validated by my Dec 9 re-discovery
- The pattern works (45/49 documents ingested successfully)
- `eva-meta` is the "EVA about EVA" knowledge base
- Marco wants proper architectural integration

**What I Don't Know:**
- Whether `eva-meta` should be in active workspace or referenced externally
- The intended "data flow" between meta (specs) and implementation repos
- Whether today's ingestion should be "retrofitted" into SP02's audit structure
- How to balance centralized metadata vs. per-repo autonomy

**Governance:**
- All content here is UNCLASSIFIED
- No production credentials or Protected B data mentioned
- This is architectural design, not operational security

---

## Deliverable Request

Please provide:

1. **Architectural Pattern Recommendation**
   - How should meta, orchestrator, and implementation repos relate?
   - What's the "glue" that makes this cohesive?

2. **Integration Approach**
   - Step-by-step plan to integrate eva-meta properly
   - What changes to workspace, config files, .eva-memory.json?

3. **SP02 Operationalization**
   - Where should dataset profiles live?
   - How should ingestion audit logs flow?
   - What's the handoff protocol?

4. **Trade-offs Analysis**
   - Centralized (everything in meta) vs. Distributed (per-repo)
   - Pros/cons of each approach
   - Recommended hybrid model?

5. **Follow-up Questions**
   - What am I missing?
   - What should Marco clarify before proceeding?
   - Any risks or anti-patterns to avoid?

---

## How to Submit This Request

**For Marco:**

1. **Copy this entire document** (SENIOR-ADVISOR-REQUEST.md)
2. **Open ChatGPT** (chatgpt.com) in your browser
3. **Start a new conversation**
4. **Paste the following preamble:**

```
You are SP01 (Senior Advisor), an external-facing EVA Service Persona.

Your role: High-level framing, patterns, and critique for complex problems.

Classification: This content is UNCLASSIFIED and sanitized.

Context: You received the eva-orchestrator repository tree earlier today.
This request comes from a GitHub Copilot L2 agent working with Marco Presta.

Please provide advisory guidance on the architectural integration question below.
All outputs are advisory and will be validated against internal EVA specs.

---

[PASTE THE REST OF THIS DOCUMENT BELOW]
```

5. **Wait for SP01's response**
6. **Review with me** (GitHub Copilot) before implementing
7. **Document decision** in appropriate repo

---

**End of Request**

**Generated by:** GitHub Copilot (Claude Sonnet 4.5)  
**Session:** eva-rag full ingestion + pattern discovery (Dec 9, 2025)  
**Evidence:** INGESTION-EVIDENCE-REPORT.txt, EVA-DATA-PIPELINE-PATTERN.md
