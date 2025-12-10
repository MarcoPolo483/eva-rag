"""
Explore Statistics Canada employment data via WDS API
"""
import requests
import json
from collections import defaultdict

print('='*70)
print('STATISTICS CANADA WDS - EMPLOYMENT DATA DISCOVERY')
print('='*70)

# Step 1: Get all cubes list
print('\n1. Fetching complete catalog of data tables...')
url = 'https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite'
response = requests.get(url)
all_cubes = response.json()

print(f'   Total tables in StatCan: {len(all_cubes)}')

# Step 2: Filter for employment-related tables
print('\n2. Filtering for employment-related tables...')
employment_keywords = ['employ', 'labour', 'labor', 'job', 'work', 'unemployment']

employment_tables = []
for cube in all_cubes:
    title_en = cube.get('cubeTitleEn', '').lower()
    title_fr = cube.get('cubeTitleFr', '').lower()
    
    if any(keyword in title_en or keyword in title_fr for keyword in employment_keywords):
        employment_tables.append({
            'productId': cube['productId'],
            'titleEn': cube['cubeTitleEn'],
            'titleFr': cube['cubeTitleFr'],
            'startDate': cube.get('cubeStartDate'),
            'endDate': cube.get('cubeEndDate'),
            'frequencyCode': cube.get('frequencyCode'),
            'archived': cube.get('archived')
        })

print(f'   Found {len(employment_tables)} employment-related tables')

# Step 3: Get frequency descriptions
print('\n3. Getting code descriptions...')
codeset_url = 'https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets'
codeset_response = requests.get(codeset_url)
codesets = codeset_response.json()['object']

frequency_map = {f['frequencyCode']: f['frequencyDescEn'] 
                for f in codesets.get('frequency', [])}

# Step 4: Display summary by frequency
print('\n4. EMPLOYMENT TABLES BY FREQUENCY')
print('-'*70)

active_tables = [t for t in employment_tables if t['archived'] == '2']  # 2 = CURRENT

by_frequency = defaultdict(list)
for table in active_tables:
    freq_code = table['frequencyCode']
    freq_desc = frequency_map.get(freq_code, f'Unknown ({freq_code})')
    by_frequency[freq_desc].append(table)

for freq, tables in sorted(by_frequency.items()):
    print(f'\n{freq}: {len(tables)} tables')
    for i, table in enumerate(tables[:3], 1):
        title_short = table['titleEn'][:60]
        print(f'  {i}. [PID {table["productId"]}] {title_short}...')
        if table['startDate'] and table['endDate']:
            print(f'     Period: {table["startDate"]} to {table["endDate"]}')
    if len(tables) > 3:
        print(f'  ... and {len(tables) - 3} more')

# Step 5: Show top 10 employment tables
print('\n\n5. TOP 10 CURRENT EMPLOYMENT TABLES')
print('='*70)
for i, table in enumerate(active_tables[:10], 1):
    freq_desc = frequency_map.get(table['frequencyCode'], 'Unknown')
    print(f'\n{i}. PID {table["productId"]} - {freq_desc}')
    print(f'   {table["titleEn"]}')
    if table['startDate'] and table['endDate']:
        print(f'   Period: {table["startDate"]} to {table["endDate"]}')

print('\n' + '='*70)
print(f'SUMMARY: {len(active_tables)} active employment tables available')
print('='*70)

# Save the full list to JSON
output_file = 'employment_tables_catalog.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(active_tables, f, indent=2, ensure_ascii=False)

print(f'\nFull catalog saved to: {output_file}')
