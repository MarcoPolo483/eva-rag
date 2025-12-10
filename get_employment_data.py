"""
Get actual employment data from Statistics Canada
Focus on Labour Force Survey - the primary employment indicator
"""
import requests
import json
import pandas as pd
from datetime import datetime

print('='*70)
print('STATISTICS CANADA - LABOUR FORCE SURVEY DATA RETRIEVAL')
print('='*70)

# Look for Labour Force Survey tables
print('\n1. Searching for Labour Force Survey tables...')

# Load our catalog
with open('employment_tables_catalog.json', 'r', encoding='utf-8') as f:
    employment_tables = json.load(f)

# Filter for "Labour force" tables (most frequently updated)
lfs_tables = [t for t in employment_tables 
              if 'labour force' in t['titleEn'].lower() 
              and t['frequencyCode'] == '6']  # Monthly

print(f'   Found {len(lfs_tables)} monthly Labour Force Survey tables')

# If no LFS tables, get employment insurance tables instead
if not lfs_tables:
    print('   No LFS tables found, searching for employment insurance...')
    lfs_tables = [t for t in employment_tables 
                  if ('employment insurance' in t['titleEn'].lower() 
                      or 'labor force' in t['titleEn'].lower()
                      or 'labour' in t['titleEn'].lower())
                  and t['frequencyCode'] == '6']
    print(f'   Found {len(lfs_tables)} monthly employment tables')

# Select the main LFS table
target_table = None
for table in lfs_tables[:10]:
    print(f'   - PID {table["productId"]}: {table["titleEn"][:70]}...')
    if 'characteristics' in table['titleEn'].lower() and 'sex' in table['titleEn'].lower():
        target_table = table
        break

if not target_table and lfs_tables:
    # Fallback to first table
    target_table = lfs_tables[0]
elif not target_table:
    # No suitable tables found - use known PID
    print('   Using known Labour Force Survey table PID 14100287')
    target_table = {
        'productId': 14100287,
        'titleEn': 'Labour force characteristics by province, monthly',
        'startDate': '1976-01-01',
        'endDate': '2024-12-01',
        'frequencyCode': '6'
    }

print(f'\n2. Selected table: PID {target_table["productId"]}')
print(f'   Title: {target_table["titleEn"]}')
print(f'   Period: {target_table["startDate"]} to {target_table["endDate"]}')

# Get metadata for this table
print('\n3. Fetching table metadata...')
pid = target_table['productId']
metadata_url = f'https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata'
params = [{'productId': pid}]
response = requests.post(metadata_url, json=params)
metadata = response.json()[0]

print(f'   Dimensions: {len(metadata["object"]["dimension"])}')
for i, dim in enumerate(metadata['object']['dimension'][:5], 1):
    print(f'   {i}. {dim["dimensionNameEn"]}: {len(dim["member"])} members')

# Get vectors for key employment indicators
print('\n4. Identifying key employment vectors...')
vectors_to_get = []

# Look for employment, unemployment, participation rate vectors
for dim in metadata['object']['dimension']:
    if 'characteristics' in dim['dimensionNameEn'].lower():
        for member in dim['member']:
            name = member['memberNameEn'].lower()
            if any(keyword in name for keyword in ['employment', 'unemployment rate', 'participation rate']):
                # Build coordinate
                coord = '.'.join([str(member.get('memberId', '0')) 
                                 for member in dim['member']])
                print(f'   - {member["memberNameEn"]}')

# Alternative: Get some sample vectors from series info
print('\n5. Getting sample data (latest 12 months)...')

# Use known vectors for Canada unemployment rate
sample_vectors = [
    2062815,  # Unemployment rate, Canada
    2062814,  # Employment, Canada
    2062816,  # Participation rate, Canada
]

# Get data for each vector separately
all_data = []
for vector_id in sample_vectors:
    data_url = 'https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods'
    
    # Build request - send ONE vector per request
    request_body = [{
        'vectorId': vector_id,
        'latestN': 12
    }]
    
    response = requests.post(data_url, json=request_body)
    if response.status_code == 200:
        result = response.json()
        all_data.append(result[0])
    else:
        print(f'   Error for vector {vector_id}: {response.status_code}')
        print(f'   Response: {response.text[:200]}')

print(f'   Retrieved data for {len(all_data)} vectors')

# Create combined result structure
data = {
    'object': {
        'vectorDataPoint': all_data
    }
}

# Create combined result structure
data = {
    'object': {
        'vectorDataPoint': all_data
    }
}

# Process and display the data
print('\n6. EMPLOYMENT DATA - LATEST 12 MONTHS')
print('='*70)

for vector_result in all_data:
    vector_data = vector_result['object']
    print(f'\nVector {vector_data["vectorId"]}')
    print(f'Product ID: {vector_data["productId"]}')
    print(f'\nDate                Value      Status')
    print('-'*40)
    
    for point in vector_data['vectorDataPoint'][-12:]:  # Last 12 months
        ref_per = point['refPer']
        value = point['value']
        status = point.get('symbolCode', '')
        
        print(f'{ref_per:20} {value:>8} {status:>10}')

# Save full data to CSV
print('\n\n7. Saving data to CSV...')
rows = []
for vector_result in all_data:
    vector_data = vector_result['object']
    vector_id = vector_data['vectorId']
    product_id = vector_data['productId']
    
    for point in vector_data['vectorDataPoint']:
        rows.append({
            'vector_id': vector_id,
            'product_id': product_id,
            'date': point['refPer'],
            'value': point['value'],
            'decimals': point.get('decimals', 0),
            'scalar_code': point.get('scalarFactorCode', 0),
            'status': point.get('symbolCode', ''),
            'release_time': point.get('releaseTime', '')
        })

df = pd.DataFrame(rows)
output_csv = 'canada_employment_data_latest_12mo.csv'
df.to_csv(output_csv, index=False)
print(f'   Data saved to: {output_csv}')
print(f'   Records: {len(df)}')

print('\n' + '='*70)
print('DATA RETRIEVAL COMPLETE')
print('='*70)
