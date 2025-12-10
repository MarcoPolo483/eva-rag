# Kaggle Employment Data Integration

This document describes how to integrate Canadian employment datasets from Kaggle with eva-rag.

## Overview

EVA-RAG now supports ingesting employment and economic datasets from Kaggle, specifically optimized for two key Canadian employment datasets.

## Supported Datasets

### 1. Canada Employment Trend Cycle Dataset (Official)

**Source:** https://www.kaggle.com/datasets/rohithmahadevan/canada-employment-trend-cycle-dataset-official

**Description:**
- Employment by industry, monthly data (seasonally adjusted, trend-cycle, and unadjusted)
- Standard error of estimate, month-to-month change, and year-over-year change
- Based on North American Industry Classification System (NAICS)
- Last 5 months of data

**File Details:**
- `14100355.csv` (120.04 MB)
- `14100355_MetaData.csv` (metadata file)
- 17 columns total
- Original source: Statistics Canada Table 14-10-0355-03

**Columns:**
1. REF_DATE - Reference period (year-month)
2. GEO - Geographic area
3. North American Industry Classification System (NAICS)
4. Data type (Seasonally adjusted, Trend-cycle, Unadjusted)
5. UOM - Unit of measurement
6. UOM_ID - Unit of measurement ID
7. SCALAR_FACTOR - Scalar factor
8. SCALAR_ID - Scalar ID
9. VECTOR - Statistics Canada vector identifier
10. COORDINATE - Coordinate reference
11. VALUE - Employment value
12. STATUS - Data status
13. SYMBOL - Data symbol
14. TERMINATED - Termination indicator
15. DECIMALS - Decimal places
16. And additional metadata columns

**Use Cases:**
- Industry-specific employment trend analysis
- Seasonal adjustment comparison
- Economic forecasting models
- Labor market research
- Regional economic planning

### 2. Unemployment in Canada by Province (1976-Present)

**Source:** https://www.kaggle.com/datasets/pienik/unemployment-in-canada-by-province-1976-present

**Description:**
- Labor Force Statistics in Canada by Province
- Monthly data from 1976 to present
- Comprehensive demographic breakdowns

**File Details:**
- `Unemployment_Canada_1976_present.csv` (4.52 MB)
- 13 columns
- Original source: Statistics Canada Table 14-10-0287-03
- Monthly updates

**Dimensions:**
- REF_DATE: Reference period (by year, month)
- GEO: Geographic area (provinces)
- Sex: Male, Female, Both sexes
- Age group: Various age brackets (15+, 15-24, 25-54, 55+, etc.)

**Metrics:**
- Employment: Total employed persons
- Full-time employment: Persons working 30+ hours/week
- Part-time employment: Persons working <30 hours/week
- Labour force: Civilian, non-institutionalized persons 15+
- Population: Working age population (15+)
- Unemployment: Persons without work, actively seeking
- Employment rate: Employment as % of population
- Participation rate: Labour force as % of population
- Unemployment rate: Unemployment as % of labour force

**Use Cases:**
- Provincial unemployment comparison
- Demographic labor market analysis
- Historical trend analysis (50+ years of data)
- Policy impact evaluation
- Regional economic health monitoring

## Integration with EVA-RAG

### File Format Support

EVA-RAG supports CSV files through the new `CSVLoader`:

```python
from eva_rag.loaders.csv_loader import CSVLoader

# Load large CSV files efficiently
loader = CSVLoader(
    sample_rows=10000,  # Sample for large files
    max_preview_rows=50,  # Limit markdown preview
    encoding="utf-8",  # Auto-detected by default
    delimiter=","  # Auto-detected by default
)

with open("14100355.csv", "rb") as f:
    doc = loader.load_from_stream(f)

print(doc.metadata["column_count"])  # 17
print(doc.metadata["row_count"])  # Total rows
print(doc.metadata["statistics"])  # Column statistics
```

### Features

**1. Automatic Delimiter Detection**
- Supports comma, semicolon, tab, pipe delimiters
- Uses csv.Sniffer for intelligent detection

**2. Encoding Handling**
- Auto-detects UTF-8, UTF-8-BOM, Latin-1, CP1252, ISO-8859-1
- Fallback mechanisms for robust loading

**3. Large File Support**
- Sampling strategy for files >100MB
- Configurable row limits
- Memory-efficient streaming

**4. Statistical Analysis**
- Detects numeric vs categorical columns
- Calculates min/max/mean for numeric columns
- Extracts unique values for categorical columns
- Sample values for quick data profiling

**5. Markdown Conversion**
- Generates LLM-readable markdown tables
- Column metadata extraction
- Truncates long values for readability

### Folder Ingestion

Process multiple CSV files at once:

```python
from eva_rag.loaders.folder_loader import FolderLoader

loader = FolderLoader(
    folder_path="kaggle_employment_data/",
    recursive=True,
    include_patterns=["*.csv"],
    continue_on_error=True
)

docs = loader.load_all()
print(f"Processed {len(docs)} CSV files")
print(f"Success rate: {loader.progress['success_rate']}%")
```

## Microsoft 365 Support

EVA-RAG also supports Microsoft 365 file formats commonly used with Kaggle data:

### Excel Files (.xlsx, .xls)

```python
from eva_rag.loaders.excel_loader import ExcelLoader

loader = ExcelLoader(
    max_rows_per_sheet=1000,
    include_formulas=True
)

with open("employment_analysis.xlsx", "rb") as f:
    doc = loader.load_from_stream(f)

print(doc.metadata["sheet_count"])  # Number of sheets
print(doc.metadata["sheet_names"])  # ['Summary', 'Data', 'Charts']
```

**Features:**
- Multiple sheet support
- Formula extraction (shows formulas + calculated values)
- Merged cell detection
- Table and named range support
- Workbook properties (author, created date, etc.)

### PowerPoint Files (.pptx)

```python
from eva_rag.loaders.pptx_loader import PowerPointLoader

loader = PowerPointLoader(
    include_notes=True,
    include_tables=True
)

with open("employment_presentation.pptx", "rb") as f:
    doc = loader.load_from_stream(f)

print(doc.metadata["slide_count"])  # 15 slides
print(doc.text)  # All slides as markdown
```

**Features:**
- Slide title and body text extraction
- Speaker notes inclusion
- Table data extraction from slides
- Slide order preservation
- Presentation metadata (author, created, modified)

## Data Processing Workflow

### 1. Download Datasets from Kaggle

```powershell
# Download from Kaggle (requires Kaggle API)
kaggle datasets download rohithmahadevan/canada-employment-trend-cycle-dataset-official
kaggle datasets download pienik/unemployment-in-canada-by-province-1976-present

# Extract
unzip canada-employment-trend-cycle-dataset-official.zip -d employment_trend/
unzip unemployment-in-canada-by-province-1976-present.zip -d unemployment_provincial/
```

### 2. Ingest with EVA-RAG

```python
from eva_rag.loaders.csv_loader import CSVLoader
from eva_rag.services.ingestion_service import IngestionService

# Initialize service
service = IngestionService()

# Load large employment dataset (120MB)
loader_large = CSVLoader(sample_rows=50000)  # Sample 50K rows
with open("employment_trend/14100355.csv", "rb") as f:
    doc_large = loader_large.load_from_stream(f)

# Load provincial unemployment dataset (4.5MB)
loader_small = CSVLoader()  # Load all rows
with open("unemployment_provincial/Unemployment_Canada_1976_present.csv", "rb") as f:
    doc_small = loader_small.load_from_stream(f)

# Ingest into RAG system
await service.ingest_document(doc_large, "employment_trend_2024")
await service.ingest_document(doc_small, "unemployment_provincial_history")
```

### 3. Query Employment Data

```python
# Example queries after ingestion:
# - "What was the unemployment rate in Ontario in November 2024?"
# - "Show employment trends by industry over the last 5 months"
# - "Compare full-time vs part-time employment across provinces"
# - "What demographic has the highest unemployment rate?"
```

## Performance Considerations

### Large File Handling

**120MB Employment Dataset:**
- Use `sample_rows` parameter to limit memory usage
- Recommended: `sample_rows=10000` for 120MB file
- Processing time: ~5-10 seconds with sampling

**4.5MB Unemployment Dataset:**
- Can load entirely into memory
- Processing time: ~1-2 seconds
- No sampling needed

### Memory Usage

| File Size | Rows | Columns | Recommended Sample | Memory Usage |
|-----------|------|---------|-------------------|--------------|
| 120 MB | ~500K | 17 | 10,000 rows | ~50 MB |
| 4.5 MB | ~20K | 13 | All rows | ~15 MB |

### Chunking Strategy

For optimal RAG performance:
1. **Time-based chunks**: Group by year or quarter
2. **Geographic chunks**: Separate by province/region
3. **Industry chunks**: Group by NAICS classification
4. **Metric chunks**: Separate employment vs unemployment data

## Integration with StatCan WDS API

Combine Kaggle historical data with live StatCan API data:

```python
# Historical data from Kaggle (1976-2024)
kaggle_data = load_csv("Unemployment_Canada_1976_present.csv")

# Live data from StatCan WDS API (current month)
statcan_data = get_latest_employment_data()  # From earlier implementation

# Merge for complete time series
complete_dataset = merge_historical_and_live(kaggle_data, statcan_data)
```

## Example Use Cases

### 1. Provincial Comparison Dashboard
- Load unemployment data by province
- Query: "Compare unemployment rates across all provinces for 2024"
- Visualize with time series

### 2. Industry Employment Tracker
- Load industry-specific employment trends
- Query: "Show employment changes in healthcare sector over 5 months"
- Track NAICS categories

### 3. Demographic Analysis
- Filter by age group and sex
- Query: "Youth unemployment (15-24) trends by province"
- Cross-reference with education data

### 4. Economic Forecasting
- Historical trends + statistical models
- Query: "Predict next quarter's employment based on trends"
- Seasonally adjusted data analysis

## Troubleshooting

### Issue: Large file timeout
**Solution:** Increase `sample_rows` parameter or process in batches

### Issue: Encoding errors
**Solution:** Specify encoding explicitly: `CSVLoader(encoding="utf-8-sig")`

### Issue: Memory errors
**Solution:** Use sampling + incremental processing

### Issue: Delimiter detection fails
**Solution:** Specify delimiter: `CSVLoader(delimiter=",")`

## Future Enhancements

1. **Streaming CSV parser** for files >1GB
2. **Automatic time-series detection** and chunking
3. **Geographic data enrichment** (coordinates, region hierarchies)
4. **Cross-dataset joining** (merge unemployment + employment)
5. **Statistical visualization generation** (charts embedded in docs)

## References

- **Kaggle Employment Dataset**: https://www.kaggle.com/datasets/rohithmahadevan/canada-employment-trend-cycle-dataset-official
- **Kaggle Unemployment Dataset**: https://www.kaggle.com/datasets/pienik/unemployment-in-canada-by-province-1976-present
- **Statistics Canada Table 14-10-0355**: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410035503
- **Statistics Canada Table 14-10-0287**: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028703
- **NAICS Classification**: https://www.statcan.gc.ca/en/subjects/standard/naics/2017/index

## License

Both Kaggle datasets are under CC0: Public Domain license, allowing free use for any purpose.

---

**Last Updated:** December 8, 2024  
**EVA-RAG Version:** 0.1.0  
**Supported Formats:** CSV, Excel, PowerPoint, PDF, HTML, XML, DOCX, TXT
