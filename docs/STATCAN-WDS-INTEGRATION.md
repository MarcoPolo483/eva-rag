# Statistics Canada Web Data Service (WDS) Integration

**Purpose:** Document how clients can integrate Statistics Canada's Web Data Service with eva-rag  
**Date:** December 8, 2025  
**Status:** Information & Planning Document

---

## Overview

Statistics Canada's **Web Data Service (WDS)** is a RESTful API that provides access to Canadian statistical data and metadata released daily at 8:30 AM EST. This document explains how clients using eva-rag can integrate WDS data for enhanced RAG capabilities.

---

## What is Statistics Canada WDS?

### Key Features
- **RESTful API** over HTTPS
- **JSON format** responses (also CSV and SDMX available)
- **15 API methods** for data access
- **Daily updates** at 8:30 AM EST
- **No authentication required** (public API)
- **Rate limits:** 50 requests/second (25 per IP)
- **24/7 availability** (some methods locked during updates 12 AM - 8:30 AM)

### Data Structure
- **Cubes/Tables:** Multi-dimensional data tables (e.g., employment stats, GDP, inflation)
- **Product IDs (PID):** 8-digit identifiers (e.g., 35100003 for youth correctional services)
- **Vectors:** Short identifiers for time series (e.g., V1234567890)
- **Coordinates:** Dimensional identifiers (e.g., "1.3.1.1.1.1.0.0.0.0")

---

## API Endpoints

### Base URL
```
https://www150.statcan.gc.ca/t1/wds/rest/
```

### Core Methods (15 available)

#### 1. Change Detection
- `getChangedSeriesList` - What data series changed today
- `getChangedCubeList/{date}` - What tables changed on specific date

#### 2. Metadata Discovery
- `getCubeMetadata` - Table structure, dimensions, footnotes
- `getSeriesInfoFromVector` - Time series metadata by vector ID
- `getSeriesInfoFromCubePidCoord` - Series metadata by product ID + coordinate
- `getAllCubesList` - Complete inventory with dimensions
- `getAllCubesListLite` - Complete inventory (minimal info)

#### 3. Data Retrieval
- `getDataFromVectorsAndLatestNPeriods` - Recent N periods by vector
- `getDataFromCubePidCoordAndLatestNPeriods` - Recent N periods by coordinate
- `getChangedSeriesDataFromVector` - Today's changed data by vector
- `getChangedSeriesDataFromCubePidCoord` - Today's changed data by coordinate
- `getBulkVectorDataByRange` - Data by date range
- `getDataFromVectorByReferencePeriodRange` - Data by reference period range
- `getFullTableDownloadCSV/{pid}/{lang}` - Complete table in CSV format
- `getFullTableDownloadSDMX/{pid}` - Complete table in SDMX (XML) format

#### 4. Supporting Data
- `getCodeSets` - Code descriptions (scales, frequencies, symbols)

---

## Integration Scenarios with eva-rag

### Scenario 1: Import StatCan Tables as Documents

**Use Case:** Client wants to query employment statistics using natural language

**Approach:**
1. Download full table as CSV using `getFullTableDownloadCSV`
2. Convert CSV to structured text/markdown format
3. Ingest into eva-rag using existing CSV/text loaders
4. Chunk and index with metadata (PID, table title, subject codes)
5. Users ask questions like "What was Canada's unemployment rate in Q2 2024?"

**Example Workflow:**
```python
# Step 1: Get CSV download URL
response = requests.get(
    "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/14100287/en"
)
csv_url = response.json()["object"]

# Step 2: Download and process CSV
csv_data = requests.get(csv_url).content

# Step 3: Load into eva-rag
from eva_rag.loaders import TextLoader
loader = TextLoader()
document = loader.load(csv_data, "statcan_14100287.csv")

# Step 4: Chunk and index
# (use existing eva-rag chunking service)
```

### Scenario 2: Real-Time Data Queries

**Use Case:** Client dashboard needs latest economic indicators

**Approach:**
1. Query WDS API directly for latest N periods
2. Format response as context for RAG queries
3. Combine with historical analysis from indexed documents

**Example:**
```python
# Get latest 3 months of unemployment data
import requests

response = requests.post(
    "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods",
    json=[{"vectorId": 2062815, "latestN": 3}]
)

data_points = response.json()[0]["object"]["vectorDataPoint"]
# [{"refPer": "2024-10-01", "value": 6.5, ...}, ...]

# Use as context in RAG query
context = f"Latest unemployment rates: {data_points}"
```

### Scenario 3: Automated Daily Updates

**Use Case:** Keep RAG knowledge base current with daily StatCan releases

**Approach:**
1. Schedule daily job at 8:31 AM EST
2. Call `getChangedCubeList` for current date
3. Download changed tables using `getFullTableDownloadCSV`
4. Re-ingest updated documents
5. Update vector embeddings for changed content

**Example Cron Job:**
```python
# scheduled_update.py
from datetime import date

def update_statcan_data():
    today = date.today().isoformat()
    
    # Get changed tables
    response = requests.get(
        f"https://www150.statcan.gc.ca/t1/wds/rest/getChangedCubeList/{today}"
    )
    
    changed_tables = response.json()["object"]
    
    for table in changed_tables:
        pid = table["productId"]
        # Download and re-ingest table
        update_table(pid)
```

### Scenario 4: Hybrid RAG with Live Data

**Use Case:** Answer questions combining historical analysis + live data

**Approach:**
1. Use RAG to retrieve relevant historical documents
2. Augment with real-time data from WDS API
3. LLM synthesizes both sources in response

**Example Query:**
```
User: "How does current unemployment compare to 2008 financial crisis?"

System:
1. RAG retrieves documents about 2008 crisis
2. WDS API fetches current unemployment data
3. LLM compares and explains trends
```

---

## Data Format Examples

### Metadata Response (getCubeMetadata)
```json
{
  "productId": "35100003",
  "cansimId": "251-0008",
  "cubeTitleEn": "Average counts of young persons...",
  "cubeTitleFr": "Comptes moyens des adolescents...",
  "cubeStartDate": "1997-01-01",
  "cubeEndDate": "2015-01-01",
  "frequencyCode": 12,
  "dimension": [
    {
      "dimensionNameEn": "Geography",
      "dimensionPositionId": 1,
      "member": [
        {"memberId": 1, "memberNameEn": "Newfoundland and Labrador"}
      ]
    }
  ]
}
```

### Data Point Response
```json
{
  "vectorId": 32164132,
  "vectorDataPoint": [
    {
      "refPer": "2024-10-01",
      "value": 1052.5,
      "decimals": 1,
      "scalarFactorCode": 0,
      "symbolCode": 0,
      "statusCode": 0,
      "releaseTime": "2024-10-23T08:30",
      "frequencyCode": 9
    }
  ]
}
```

---

## Implementation Recommendations

### For eva-rag Enhancement

#### Option 1: External Data Source Connector
```python
# src/eva_rag/connectors/statcan_connector.py

class StatCanConnector:
    BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest"
    
    def get_table_csv(self, product_id: int, lang: str = "en") -> str:
        """Download full table as CSV"""
        url = f"{self.BASE_URL}/getFullTableDownloadCSV/{product_id}/{lang}"
        response = requests.get(url)
        csv_url = response.json()["object"]
        return requests.get(csv_url).text
    
    def get_latest_data(self, vector_id: int, periods: int = 12) -> list:
        """Get latest N periods for a vector"""
        url = f"{self.BASE_URL}/getDataFromVectorsAndLatestNPeriods"
        response = requests.post(url, json=[{
            "vectorId": vector_id,
            "latestN": periods
        }])
        return response.json()[0]["object"]["vectorDataPoint"]
```

#### Option 2: Scheduled Ingestion Service
```python
# src/eva_rag/services/statcan_ingestion_service.py

class StatCanIngestionService:
    def __init__(self, connector, document_service, chunking_service):
        self.connector = connector
        self.doc_service = document_service
        self.chunking = chunking_service
    
    async def ingest_changed_tables(self, date: str):
        """Daily ingestion of changed tables"""
        changed = self.connector.get_changed_cubes(date)
        
        for table in changed:
            csv_data = self.connector.get_table_csv(table["productId"])
            document = await self.doc_service.create_from_csv(csv_data)
            await self.chunking.chunk_and_index(document)
```

#### Option 3: RAG Query Augmentation
```python
# src/eva_rag/services/query_service.py

class QueryService:
    async def query_with_live_data(self, question: str, vector_ids: list[int] = None):
        """Augment RAG with live StatCan data"""
        # Standard RAG retrieval
        retrieved_docs = await self.retrieve(question)
        
        # Augment with live data if vector IDs provided
        if vector_ids:
            live_data = self.statcan.get_latest_data(vector_ids[0], periods=3)
            context = self._format_live_data(live_data)
            retrieved_docs.append(context)
        
        # Generate response
        return await self.llm.generate(question, retrieved_docs)
```

### For Client Applications

#### Dashboard with Live Stats
```python
# Client application example
from eva_rag_client import EVARagClient
import requests

client = EVARagClient()

# Get unemployment vector data
response = requests.post(
    "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods",
    json=[{"vectorId": 2062815, "latestN": 12}]  # Unemployment rate
)
live_data = response.json()

# Query RAG for analysis
analysis = client.query(
    "Analyze unemployment trends over past year",
    context={"live_data": live_data}
)
```

---

## Key Considerations

### Rate Limits
- **50 requests/second globally**
- **25 requests/second per IP**
- Consider caching and batch processing

### Data Updates
- **Daily release:** 8:30 AM EST
- **Locked period:** 12:00 AM - 8:30 AM (some methods unavailable)
- Schedule ingestion for 8:31 AM or later

### Data Volume
- Use `getFullTableDownloadCSV` for large tables
- Use vector-based methods for specific time series
- Full tables can be 10+ MB (zipped CSV)

### Metadata Management
- Store Product IDs with documents for traceability
- Index by subject codes for easier discovery
- Maintain vector ID mappings for time series

### Language Support
- All metadata is **bilingual** (English/French)
- CSV downloads available in both languages
- SDMX format is inherently bilingual

---

## Use Case Examples

### Example 1: Economic Analysis Chatbot
**Question:** "What's the trend in Canada's GDP over the last 5 years?"

**Implementation:**
1. User asks question
2. System identifies relevant vector (e.g., V62305752 for GDP)
3. Calls `getDataFromVectorsAndLatestNPeriods` with latestN=20 (5 years quarterly)
4. RAG retrieves related analysis documents
5. LLM synthesizes trend analysis with charts

### Example 2: Employment Equity Dashboard
**Question:** "Show me employment rates by demographic for Ontario"

**Implementation:**
1. Identify relevant table PID (e.g., 14100287)
2. Download via `getFullTableDownloadCSV`
3. Filter for Ontario using coordinates
4. Present in dashboard with RAG-powered insights

### Example 3: Alert System
**Scenario:** Monitor inflation rate and alert if > 3%

**Implementation:**
```python
# Daily check
inflation_vector = 41690973  # CPI All-items
data = get_latest_data(inflation_vector, periods=1)
rate = data[0]["value"]

if rate > 3.0:
    send_alert(f"Inflation at {rate}%, exceeding 3% threshold")
    
    # Get RAG analysis
    context = rag.query("What happens when inflation exceeds 3%?")
    send_analysis(context)
```

---

## Technical Specifications

### Request Format
```
GET:  https://www150.statcan.gc.ca/t1/wds/rest/{method}/{params}
POST: https://www150.statcan.gc.ca/t1/wds/rest/{method}
      Body: JSON array of request objects
```

### Response Format
```json
{
  "status": "SUCCESS" | "FAILED",
  "object": { /* response data */ }
}
```

### Common Codes
- **Frequency:** 1=Daily, 6=Monthly, 9=Quarterly, 12=Annual
- **Scalar:** 0=units, 3=thousands, 6=millions
- **Symbol:** 0=None, 1=Estimated, 6=Preliminary
- **Status:** 0=Final, 7=Archived

---

## Resources

- **WDS Homepage:** https://www.statcan.gc.ca/en/developers/wds
- **User Guide:** https://www.statcan.gc.ca/eng/developers/wds/user-guide
- **CANSIM-PID Concordance:** https://www.statcan.gc.ca/eng/developers/concordance
- **Code Sets (Live):** https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets
- **Delta File (Bulk):** https://www.statcan.gc.ca/eng/developers/df
- **SDMX Service:** https://www.statcan.gc.ca/eng/developers/sdmx/user-guide

---

## Next Steps for Implementation

1. **Research Phase** ✅ Complete (this document)
2. **Design Connector:** Create StatCanConnector class
3. **Test Integration:** Prototype with sample tables
4. **Build Ingestion:** Automated daily updates
5. **Enhance Query:** Hybrid RAG + live data
6. **Client Examples:** Sample applications for clients
7. **Documentation:** API reference and tutorials

---

**Prepared for:** eva-rag development team  
**Contact:** Statistics Canada - https://www.statcan.gc.ca/en/reference/refcentre/index
