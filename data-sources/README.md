# Data Sources Organization

This directory contains **structured, agent-ready specifications** for all EVA-RAG data sources.

## 📁 Structure

```
data-sources/
├── _templates/          # Templates for business analysts
├── jurisprudence/       # Legal research (example)
├── canada-ca/           # Government services
├── employment/          # Employment analytics
└── assistme/            # Legal guidance
```

Each data source folder follows the **P02-ready pattern**:

```
[data-source-name]/
├── requirements.json              # P02-consumable requirements
├── constraints.json               # Safety boundaries
├── ingestion-spec.md              # Human-readable blueprint
├── config/
│   └── pipeline-config.yaml       # Runtime configuration
├── discover/
│   └── sources.yaml               # Source catalog
├── normalize/
│   ├── metadata_schema.json       # Metadata definition
│   └── cleaning_rules.yaml        # Content cleaning
└── publish/
    ├── chunking_strategy.yaml     # Chunking rules
    └── vector_config.yaml         # Vector store settings
```

## 🎯 Purpose

Enable **business analysts** to define data ingestion requirements using structured formats that can be automatically processed by EVA's P02 Requirements Engine to generate complete ingestion pipelines.

## 🚀 Quick Start

### For Business Analysts

1. **Copy the template:**
   ```
   cp _templates/ingestion-prompt.md [your-project]/ingestion-request.md
   ```

2. **Fill in your requirements** (no technical knowledge needed)

3. **Submit for review** via Slack/Email/GitHub

### For Developers

1. **Read the requirements:**
   ```python
   import json
   with open('jurisprudence/requirements.json') as f:
       requirements = json.load(f)
   ```

2. **Generate pipeline** using P02 Agent

3. **Execute ingestion** using generated scripts

## 📖 Documentation

- **[Organization Standard](../docs/DATA-SOURCE-ORGANIZATION-STANDARD.md)** - Complete specification
- **[Data Inventory](../docs/DATA-INVENTORY-FOR-REVIEW.md)** - Current ingested data
- **[Jurisprudence Example](jurisprudence/)** - Full working example

## 🔗 Related

- **eva-orchestrator/jurispipeline** - Original proof-of-concept
- **src/eva_rag/pipelines/** - Generated pipeline code
- **data/ingested/** - RAG-ready output

---

**Last Updated:** December 8, 2024  
**Owner:** EVA-RAG Team
