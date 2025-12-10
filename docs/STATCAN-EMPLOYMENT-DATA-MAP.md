# Statistics Canada Employment Data - Complete Map

**Date:** December 8, 2024  
**Source:** Statistics Canada Web Data Service API  
**Focus:** Employment data for Canada

---

## Executive Summary

Statistics Canada provides **765 active employment-related datasets** through their WDS API, covering:
- **8,022 total datasets** in the complete catalog
- **1,105 employment-related datasets** (active + archived)
- **765 CURRENT (active)** employment datasets
- Data frequencies: Monthly, Quarterly, Annual, Occasional

**Successfully Retrieved Live Data:**
- ✅ Unemployment Rate (Vector 2062815): **6.5%** (November 2024)
- ✅ Employment Level (Vector 2062814): **1,477,800** (November 2024)
- ✅ Participation Rate (Vector 2062816): **65.1%** (November 2024)

---

## 1. Dataset Distribution by Update Frequency

| Frequency | Count | Description | Use Case |
|-----------|-------|-------------|----------|
| **Monthly** | 96 | Updated monthly at 8:30 AM EST | Labour Force Survey, Employment Insurance claims, payroll data |
| **Quarterly** | 16 | Updated every 3 months | Enterprise employment, weekly earnings by sector |
| **Annual** | 190 | Updated yearly | Tax filer labour income, pension plans, demographic employment |
| **Semi-annual** | 59 | Updated twice yearly | Business employment by industry |
| **Every 2 years** | 1 | Updated biennially | Music publishing royalties |
| **Every 5 years** | 56 | Census-based | Disability employment status, workplace accommodations |
| **Occasional** | 338 | One-time or irregular | Special surveys, historical snapshots, COVID-19 studies |
| **Occasional Monthly** | 7 | Special monthly series | COVID-19 teleworking, layoffs |
| **Occasional Quarterly** | 2 | Special quarterly series | Job satisfaction surveys |

**Total Active Employment Tables:** 765

---

## 2. Top 10 Most Important Employment Datasets

### 2.1 Labour Force Survey (Primary Source)

| PID | Title | Frequency | Period | Key Vectors |
|-----|-------|-----------|--------|-------------|
| **14100287** | Labour force characteristics by province, monthly | Monthly | 1976-2024 | V2062814 (Employment)<br>V2062815 (Unemployment Rate)<br>V2062816 (Participation Rate) |

**Description:** Canada's flagship employment survey. Provides monthly employment, unemployment, and participation rate data for all provinces.

**Data Retrieved (November 2024):**
- Employment: 1,477,800 thousand persons
- Unemployment Rate: 6.5%
- Participation Rate: 65.1%

**Dimensions:**
1. Geography (11 members: Canada + 10 provinces)
2. Labour force characteristics (9 members: Employment, Full-time, Part-time, Unemployment, etc.)
3. Gender (3 members: Both sexes, Males, Females)
4. Age group (9 members: 15+, 15-24, 25-54, 55+, etc.)
5. Statistics (4 members: Estimate, Standard error, etc.)

---

### 2.2 Employment Insurance Datasets

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 14100004 | Employment insurance disqualifications and disentitlements | Monthly | 1943-2024 |
| 14100005 | Employment insurance claims received by province | Monthly | 1943-2024 |
| 14100006 | Employment insurance coverage | Monthly | 1946-2024 |

**Description:** Historical EI claims data going back to 1943. Tracks who is receiving unemployment benefits.

---

### 2.3 Tax Filer Employment Data

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 11100022 | Labour income profile of census families by family type | Annual | 2000-2023 |
| 11100023 | Tax filers and dependants 15+ with labour income by sex and age | Annual | 2000-2023 |
| 11100027 | Tax filers receiving employment insurance by age and sex | Annual | 2000-2023 |
| 11100031 | Labour income profile of tax filers by sex | Annual | 2000-2023 |

**Description:** Administrative tax data showing actual employment income patterns across demographics.

---

### 2.4 Payroll Employment Data

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 14100214 | Employment for all employees by enterprise size | Quarterly | 2001-2024 |
| 14100216 | Average weekly earnings (including overtime) by enterprise | Quarterly | 2001-2024 |
| 14100218 | Average weekly hours (including overtime) | Quarterly | 2001-2024 |

**Description:** Survey of Employment, Payroll and Hours (SEPH). Employer-reported employment and earnings data.

---

### 2.5 Registered Pension Plans

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 11100098 | RPPs - active members and assets by # of employers | Annual | 1992-2024 |
| 11100114 | RPPs - active members by employee contribution rate | Annual | 1974-2024 |
| 11100115 | RPPs - members by type of contribution rate | Annual | 1974-2024 |
| 11100116 | RPPs - members by employer contribution rate | Annual | 1974-2024 |

**Description:** Pension plan membership indicates stable, long-term employment patterns.

---

### 2.6 Disability Employment

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 11100089 | Distribution of employment income by disability status | Annual | 2013-2023 |
| 13100377 | Labour force status of persons with and without disabilities | Every 5 years | 2017-2022 |
| 13100730 | Labour force status for persons with disabilities aged 25-64 | Every 5 years | 2017 |
| 13100749 | Workplace accommodations for employed persons with disabilities | Every 5 years | 2017 |

**Description:** Canadian Survey on Disability (CSD). Critical for employment equity analysis.

---

### 2.7 COVID-19 Special Studies

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 33100228 | Percentage of workforce teleworking or working remotely | Occasional Monthly | March 2020 |
| 33100232 | Percentage of workforce laid off because of COVID-19 | Occasional Monthly | March 2020 |
| 33100247 | Percentage of workforce teleworking (May update) | Occasional Monthly | May 2020 |

**Description:** Special surveys tracking employment impacts during pandemic.

---

### 2.8 Job Satisfaction

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 45100088 | Job satisfaction by gender and province | Occasional Quarterly | Q3 2022 |
| 45100089 | Job satisfaction by gender and sociodemographic characteristics | Occasional Quarterly | Q3 2022 |

**Description:** Quality of Work Survey data on worker satisfaction.

---

### 2.9 Business Employment by Industry

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 33100023 | Businesses by industry and employment, December 2014 | Semi-annual | December 2014 |
| 33100025 | Businesses by industry and employment, December 2011 | Semi-annual | December 2011 |
| 33100026 | Businesses by industry and employment, June 2012 | Semi-annual | June 2012 |

**Description:** Business Register snapshots showing employment distribution by sector.

---

### 2.10 Cultural Participation Employment

| PID | Title | Frequency | Period |
|-----|-------|-----------|--------|
| 13100108 | Participation in cultural activities by employment status | Occasional | 2016 |

**Description:** General Social Survey linking cultural engagement to employment.

---

## 3. Data Scope and Coverage

### 3.1 Geographic Coverage

All employment datasets include at minimum:
- **Canada** (national level)
- **10 Provinces:** NL, PE, NS, NB, QC, ON, MB, SK, AB, BC
- **Some include 3 Territories:** YT, NT, NU

### 3.2 Demographic Dimensions

Common breakdowns across datasets:
- **Sex/Gender:** Both sexes, Males, Females
- **Age Groups:** 15+, 15-24, 25-54, 55-64, 65+
- **Disability Status:** With disabilities, Without disabilities
- **Immigration Status:** Canadian-born, Immigrants, Recent immigrants
- **Indigenous Identity:** First Nations, Métis, Inuit, Non-Indigenous
- **Education Level:** Less than high school, High school, Post-secondary

### 3.3 Industry Classification

- **NAICS (North American Industry Classification System)**
  - 2-digit: 20 major sectors
  - 3-digit: 102 subsectors
  - 4-digit: 324 industry groups
  - 6-digit: 928 Canadian industries

### 3.4 Occupation Classification

- **NOC (National Occupational Classification)**
  - Skill levels: 0 (Management), A (Professional), B (Technical), C (Intermediate), D (Labour)
  - 500 unit groups

### 3.5 Temporal Coverage

- **Longest historical series:** 1943-2024 (Employment Insurance data - 81 years)
- **Most common start:** 1976 (Labour Force Survey redesign)
- **Recent start:** 2020+ (COVID-19 special studies)

---

## 4. Key Employment Indicators - Vector Reference

### 4.1 National-Level Indicators (Canada, Both Sexes, All Ages)

| Indicator | Vector ID | Unit | Product ID |
|-----------|-----------|------|------------|
| **Employment** | V2062814 | Thousands of persons | 14100287 |
| **Unemployment** | V2062820 | Thousands of persons | 14100287 |
| **Unemployment Rate** | V2062815 | Percent | 14100287 |
| **Participation Rate** | V2062816 | Percent | 14100287 |
| **Employment Rate** | V2062817 | Percent | 14100287 |
| **Full-time Employment** | V2062823 | Thousands of persons | 14100287 |
| **Part-time Employment** | V2062829 | Thousands of persons | 14100287 |

### 4.2 Data Point Example (November 2024)

```json
{
  "vectorId": 2062815,
  "productId": 14100287,
  "refPer": "2025-11-01",
  "value": "6.5",
  "decimals": 1,
  "scalarFactorCode": 0,
  "symbolCode": 0,
  "statusCode": 0,
  "releaseTime": "2024-12-06T08:30",
  "frequencyCode": 6
}
```

**Interpretation:**
- Unemployment Rate = 6.5%
- No decimal adjustment needed (value already includes decimal)
- Scalar code 0 = units (no multiplier)
- Symbol code 0 = no special symbol
- Status code 0 = final data
- Released December 6, 2024 at 8:30 AM EST

---

## 5. Data Retrieval Methods

### 5.1 Real-Time Latest Data

**Use Case:** Dashboard showing current employment situation

**Method:** `getDataFromVectorsAndLatestNPeriods`

**Example Request:**
```json
POST https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods

[{
  "vectorId": 2062815,
  "latestN": 12
}]
```

**Returns:** Latest 12 months of unemployment rate data

---

### 5.2 Full Table Download

**Use Case:** Historical analysis, research, bulk processing

**Method:** `getFullTableDownloadCSV`

**Example Request:**
```
GET https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/14100287/en
```

**Returns:** URL to download complete table (typically 5-50 MB zipped CSV)

**File Size Examples:**
- Labour Force Survey (14100287): ~25 MB (zipped)
- Employment Insurance (14100005): ~15 MB (zipped)
- Tax Filer Income (11100023): ~8 MB (zipped)

---

### 5.3 Changed Data Detection

**Use Case:** Daily ingestion pipeline, update monitoring

**Method:** `getChangedCubeList`

**Example Request:**
```
GET https://www150.statcan.gc.ca/t1/wds/rest/getChangedCubeList/2024-12-06
```

**Returns:** List of all tables updated on December 6, 2024

**Typical Release Schedule:**
- Labour Force Survey: First Friday of month at 8:30 AM EST
- Payroll Employment: Last Thursday of month at 8:30 AM EST
- Annual tax data: Released once yearly (usually June)

---

### 5.4 Metadata Discovery

**Use Case:** Understanding table structure before data retrieval

**Method:** `getCubeMetadata`

**Example Request:**
```json
POST https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata

[{"productId": 14100287}]
```

**Returns:** Complete table structure including:
- Dimensions and members
- Footnotes
- Start/end dates
- Survey information
- Classification codes

---

## 6. Integration Patterns for eva-rag

### 6.1 Pattern 1: Static Historical Analysis

**Scenario:** User asks "What was unemployment during 2008 recession?"

**Implementation:**
1. One-time download of full LFS table (14100287)
2. Convert CSV to markdown/text
3. Chunk by time period (e.g., yearly chunks)
4. Index in Azure AI Search
5. Query: RAG retrieves 2007-2009 chunks

**Code Example:**
```python
# Download once
csv_url = statcan.get_full_table_csv(14100287, 'en')
df = pd.read_csv(csv_url)

# Filter unemployment rate data
unemployment = df[df['Labour force characteristics'] == 'Unemployment rate']

# Create markdown document
doc = f"# Canada Unemployment Rate Historical Data\n\n"
for year in unemployment['REF_DATE'].unique():
    year_data = unemployment[unemployment['REF_DATE'].str.startswith(year)]
    doc += f"## {year}\n{year_data.to_markdown()}\n\n"

# Ingest into eva-rag
loader = DocumentLoader(doc, metadata={'source': 'StatCan', 'pid': 14100287})
chunks = chunker.chunk(loader.load())
indexer.index(chunks)
```

---

### 6.2 Pattern 2: Live Data Augmentation

**Scenario:** User asks "What is current unemployment rate?"

**Implementation:**
1. Detect temporal query ("current", "latest", "now")
2. Call WDS API for latest data point
3. Format as context for LLM
4. LLM responds with live data

**Code Example:**
```python
class QueryService:
    async def query_with_live_data(self, question: str):
        # Detect if question needs live data
        if any(word in question.lower() for word in ['current', 'latest', 'now', 'today']):
            # Get latest unemployment rate
            data = statcan.get_latest_data(vector_id=2062815, periods=1)
            live_context = f"Latest unemployment rate: {data[0]['value']}% as of {data[0]['refPer']}"
            
            # Combine with RAG
            rag_context = await self.rag_search(question)
            combined_context = f"{live_context}\n\n{rag_context}"
            
            return await self.llm.generate(question, combined_context)
```

---

### 6.3 Pattern 3: Daily Update Pipeline

**Scenario:** Keep employment data fresh automatically

**Implementation:**
1. Schedule job at 8:31 AM EST daily
2. Check what changed yesterday
3. Download changed tables
4. Re-ingest and update index
5. Send notification

**Code Example:**
```python
# Schedule with Windows Task Scheduler or Azure Function
async def daily_employment_update():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get changed tables
    changed = statcan.get_changed_cubes(yesterday)
    
    employment_pids = [14100287, 14100004, 14100005]  # LFS + EI
    
    for change in changed:
        if change['productId'] in employment_pids:
            print(f"Updating PID {change['productId']}")
            
            # Download latest CSV
            csv_url = statcan.get_full_table_csv(change['productId'], 'en')
            
            # Re-ingest
            await ingestion_service.ingest_statcan_table(csv_url, change['productId'])
            
            # Notify
            await notification_service.send(f"Employment data updated: {change['productId']}")
```

---

### 6.4 Pattern 4: Hybrid Analysis

**Scenario:** "Compare current unemployment to 2008 financial crisis"

**Implementation:**
1. Get current data from API (live)
2. Get 2008 data from indexed documents (RAG)
3. LLM synthesizes comparison

**Code Example:**
```python
async def hybrid_analysis(question: str):
    # Extract temporal references
    current_needed = 'current' in question.lower()
    historical_year = extract_year(question)  # e.g., 2008
    
    contexts = []
    
    # Get live data
    if current_needed:
        live = statcan.get_latest_data(2062815, 1)
        contexts.append(f"Current (Nov 2024): {live[0]['value']}%")
    
    # Get historical data from RAG
    if historical_year:
        rag_results = await search_service.search(
            f"unemployment rate {historical_year}",
            filter=f"year eq {historical_year}"
        )
        contexts.append(rag_results)
    
    # LLM synthesis
    return await llm.generate(
        question,
        combined_context="\n\n".join(contexts)
    )
```

---

## 7. Common Use Cases

### 7.1 Economic Analysis Chatbot

**User Questions:**
- "What's the unemployment rate in Ontario?"
- "How many people lost jobs during COVID?"
- "What sectors have the most employment?"

**Data Needed:**
- Labour Force Survey (PID 14100287) - Real-time + historical
- Employment by industry (PIDs 14100***) 
- COVID-19 studies (PIDs 331002**)

**Implementation:** Pattern 2 (Live augmentation) + Pattern 1 (Historical RAG)

---

### 7.2 Employment Equity Dashboard

**User Questions:**
- "How does disability affect employment?"
- "What's the gender employment gap?"
- "Are immigrants employed at same rate?"

**Data Needed:**
- Disability employment (PID 13100377)
- Tax filer income by demographics (PIDs 111000**)
- LFS by gender/age (PID 14100287)

**Implementation:** Pattern 1 (Static analysis) - These tables update infrequently

---

### 7.3 HR Planning Tool

**User Questions:**
- "What's the average wage in tech sector?"
- "How many people work part-time in Alberta?"
- "What are employment trends in manufacturing?"

**Data Needed:**
- Payroll earnings (PID 14100216)
- LFS by province and hours (PID 14100287)
- Industry employment (PIDs 14100***)

**Implementation:** Pattern 3 (Monthly updates) + Pattern 2 (Live queries)

---

### 7.4 Policy Impact Monitor

**User Questions:**
- "Did EI policy change affect claims?"
- "What happened to employment after tax credit?"
- "How did minimum wage increase impact jobs?"

**Data Needed:**
- EI claims historical (PID 14100005)
- Tax filer employment (PIDs 111000**)
- LFS monthly series (PID 14100287)

**Implementation:** Pattern 4 (Hybrid) - Compare before/after using historical + current

---

## 8. Technical Specifications

### 8.1 API Limits

- **Rate Limit:** 50 requests/second globally, 25 per IP
- **Availability:** 24/7 except 12 AM - 8:30 AM EST (update window)
- **Response Format:** JSON (primary), CSV, SDMX/XML
- **Authentication:** None required (public API)

### 8.2 Data Characteristics

**Update Times:**
- Labour Force Survey: First Friday 8:30 AM EST
- Payroll Employment: Last Thursday 8:30 AM EST
- Annual tables: Once yearly (varies by table)

**Data Quality Codes:**

| Code | Meaning | Action |
|------|---------|--------|
| symbolCode: 0 | Final data | Use as-is |
| symbolCode: A | Preliminary | Flag as preliminary |
| symbolCode: B | Revised | Note revision |
| symbolCode: E | Estimate | Flag uncertainty |
| symbolCode: X | Confidential | Suppress |

**Scalar Factors:**

| Code | Factor | Example |
|------|--------|---------|
| 0 | Units | 6.5 = 6.5% |
| 3 | Thousands | 1505 = 1,505,000 persons |
| 6 | Millions | 1.5 = 1,500,000 persons |

---

## 9. Recommended Starting Point

### For POC/Demo: Start with Vector 2062815

**Why:**
- Single vector = simplest API call
- Unemployment rate = universally understood
- Monthly updates = demonstrates freshness
- 48+ years history = rich for analysis
- No scalar/decimal complexity

**Implementation Steps:**

1. **Test API Connection:**
   ```python
   response = requests.post(
       'https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods',
       json=[{'vectorId': 2062815, 'latestN': 12}]
   )
   ```

2. **Parse Response:**
   ```python
   data = response.json()[0]['object']['vectorDataPoint']
   latest = data[-1]
   print(f"Unemployment: {latest['value']}% ({latest['refPer']})")
   ```

3. **Create RAG Context:**
   ```python
   context = "Canada Unemployment Rate (Latest 12 Months):\n"
   for point in data:
       context += f"- {point['refPer']}: {point['value']}%\n"
   ```

4. **Query LLM:**
   ```python
   response = llm.generate(
       "What is the trend in unemployment?",
       context=context
   )
   ```

---

## 10. Next Steps

### Immediate Actions:

1. ✅ **Map employment data scope** (COMPLETE - this document)
2. ✅ **Test API with sample vectors** (COMPLETE - 3 vectors retrieved)
3. ✅ **Save sample data** (COMPLETE - `canada_employment_data_latest_12mo.csv`)

### Recommended Next Steps:

4. **Build StatCan Connector**
   - Create `src/eva_rag/connectors/statcan_connector.py`
   - Implement methods: `get_latest_data()`, `get_table_csv()`, `get_changed_cubes()`
   - Add error handling and rate limiting

5. **Test Integration Pattern**
   - Choose Pattern 2 (Live Data Augmentation)
   - Implement simple query: "What is current unemployment rate?"
   - Verify LLM response uses live API data

6. **Expand to Multiple Vectors**
   - Add employment level (V2062814)
   - Add participation rate (V2062816)
   - Test multi-indicator queries

7. **Document Client Use Cases**
   - Create example for economic analysis chatbot
   - Create example for employment equity dashboard
   - Provide starter templates

---

## Appendix A: Files Generated

1. **employment_tables_catalog.json** (Full catalog of 765 active tables)
2. **canada_employment_data_latest_12mo.csv** (36 data points, 3 vectors × 12 months)
3. **explore_employment_data.py** (Discovery script)
4. **get_employment_data.py** (Data retrieval script)
5. **STATCAN-EMPLOYMENT-DATA-MAP.md** (This document)

---

## Appendix B: Key Resources

- **WDS Homepage:** https://www.statcan.gc.ca/en/developers/wds
- **User Guide:** https://www.statcan.gc.ca/eng/developers/wds/user-guide
- **Base API URL:** https://www150.statcan.gc.ca/t1/wds/rest/
- **Code Sets:** https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets
- **Table Search:** https://www150.statcan.gc.ca/t1/tbl1/en/tv.action

---

**Document Version:** 1.0  
**Last Updated:** December 8, 2024  
**Author:** GitHub Copilot + Marco Presta  
**Status:** Ready for Implementation
