"""
Load and display IT Collective Agreement salary tables

This script extracts the 25 markdown salary tables from the IT Collective Agreement
and displays them in a structured format for analysis.
"""
import json
import re
from pathlib import Path
from typing import List, Tuple


class ITAgreementTableLoader:
    """Extract and load salary tables from IT Collective Agreement."""
    
    def __init__(self):
        self.json_path = Path("data/ingested/specific_urls/specific_urls_20251209_013238.json")
        
    def load_tables(self) -> dict:
        """
        Load IT Collective Agreement and extract all salary tables.
        
        Returns:
            Dictionary with:
            - 'en': English tables
            - 'fr': French tables
            - 'metadata': Document metadata
        """
        print("=" * 80)
        print("IT COLLECTIVE AGREEMENT - SALARY TABLE EXTRACTION")
        print("=" * 80)
        print()
        
        # Load ingested data
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get IT Collective Agreement documents
        en_doc = None
        fr_doc = None
        
        for doc in data:
            if doc.get('document_type') == 'collective_agreement' and 'IT' in doc.get('metadata', {}).get('agreement_name', ''):
                if doc.get('language') == 'en':
                    en_doc = doc
                elif doc.get('language') == 'fr':
                    fr_doc = doc
        
        if not en_doc:
            print("❌ English IT Collective Agreement not found")
            return {}
        
        result = {
            'en': {
                'content': en_doc.get('full_content', ''),
                'metadata': en_doc.get('metadata', {}),
                'tables': []
            },
            'fr': None,
            'metadata': {
                'agreement_name': en_doc.get('metadata', {}).get('agreement_name', 'Unknown'),
                'bargaining_agent': en_doc.get('metadata', {}).get('bargaining_agent', 'Unknown'),
                'source_url_en': en_doc.get('source_url', 'Unknown'),
            }
        }
        
        if fr_doc:
            result['fr'] = {
                'content': fr_doc.get('full_content', ''),
                'metadata': fr_doc.get('metadata', {}),
                'tables': []
            }
            result['metadata']['source_url_fr'] = fr_doc.get('source_url', 'Unknown')
        
        # Extract tables from English version
        print(f"📄 English content: {len(result['en']['content']):,} characters")
        result['en']['tables'] = self._extract_markdown_tables(result['en']['content'])
        print(f"✅ Extracted {len(result['en']['tables'])} English tables")
        print()
        
        # Extract tables from French version (if available)
        if result['fr']:
            print(f"📄 French content: {len(result['fr']['content']):,} characters")
            result['fr']['tables'] = self._extract_markdown_tables(result['fr']['content'], language='fr')
            print(f"✅ Extracted {len(result['fr']['tables'])} French tables")
            print()
        
        return result
    
    def _extract_markdown_tables(self, content: str, language: str = 'en') -> List[dict]:
        """
        Extract markdown tables with Step columns.
        
        Args:
            content: Full document content
            language: 'en' or 'fr'
            
        Returns:
            List of table dictionaries with metadata
        """
        tables = []
        
        # Pattern for markdown tables with Step columns
        # Matches: | header | Step 1 | Step 2 | ... | Step 8 |
        #          | ---    | ---    | ---    | ... | ---    |
        #          | row data ...
        
        if language == 'en':
            step_pattern = 'Step'
        else:
            # French might use "Étape" or "Échelon"
            step_pattern = '(?:Étape|Échelon|Step)'
        
        # Find tables with Step columns
        # Pattern: Lines starting with | that contain "Step"
        pattern = rf'\|[^\n]*{step_pattern}[^\n]*\|[^\n]*\n\|[-\s|]+\|[^\n]*\n(?:\|[^\n]+\|[^\n]*\n)+'
        
        for match in re.finditer(pattern, content, re.IGNORECASE):
            table_text = match.group()
            start_pos = match.start()
            end_pos = match.end()
            
            # Extract table metadata
            table_info = {
                'text': table_text,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'length': len(table_text),
                'classification': self._extract_classification(table_text),
                'num_rows': table_text.count('\n'),
                'num_steps': self._count_steps(table_text),
            }
            
            tables.append(table_info)
        
        return tables
    
    def _extract_classification(self, table_text: str) -> str:
        """Extract IT classification (IT-01 to IT-05) from table."""
        classifications = ['IT-01', 'IT-02', 'IT-03', 'IT-04', 'IT-05']
        for classification in classifications:
            if classification in table_text:
                return classification
        return 'unknown'
    
    def _count_steps(self, table_text: str) -> int:
        """Count number of step columns in table."""
        # Count "Step X" occurrences in header
        steps = re.findall(r'Step\s+(\d+)', table_text, re.IGNORECASE)
        return len(set(steps))
    
    def display_tables(self, tables_data: dict):
        """Display summary and samples of extracted tables."""
        
        print("=" * 80)
        print("SALARY TABLE SUMMARY")
        print("=" * 80)
        print()
        
        # Display metadata
        print("Agreement Information:")
        print(f"  Name: {tables_data['metadata']['agreement_name']}")
        print(f"  Bargaining Agent: {tables_data['metadata']['bargaining_agent']}")
        print(f"  Source (EN): {tables_data['metadata']['source_url_en']}")
        if 'source_url_fr' in tables_data['metadata']:
            print(f"  Source (FR): {tables_data['metadata']['source_url_fr']}")
        print()
        
        # English tables
        if tables_data.get('en') and tables_data['en'].get('tables'):
            self._display_language_tables(tables_data['en']['tables'], 'English')
        
        # French tables
        if tables_data.get('fr') and tables_data['fr'].get('tables'):
            self._display_language_tables(tables_data['fr']['tables'], 'French')
    
    def _display_language_tables(self, tables: List[dict], language: str):
        """Display tables for a specific language."""
        print(f"--- {language} Tables ---")
        print(f"Total tables found: {len(tables)}")
        print()
        
        # Group by classification
        by_classification = {}
        for table in tables:
            classification = table['classification']
            if classification not in by_classification:
                by_classification[classification] = []
            by_classification[classification].append(table)
        
        print(f"By Classification:")
        for classification, tables_list in sorted(by_classification.items()):
            print(f"  {classification}: {len(tables_list)} tables")
        print()
        
        # Show first 3 tables
        print(f"Sample Tables (first 3):")
        print()
        
        for i, table in enumerate(tables[:3], 1):
            print(f"Table {i}:")
            print(f"  Classification: {table['classification']}")
            print(f"  Rows: {table['num_rows']}")
            print(f"  Steps: {table['num_steps']}")
            print(f"  Length: {table['length']:,} characters")
            print(f"  Position: {table['start_pos']:,} - {table['end_pos']:,}")
            print()
            print("  Content (first 600 chars):")
            print("  " + "-" * 76)
            preview = table['text'][:600]
            for line in preview.split('\n'):
                print(f"  {line}")
            print("  " + "-" * 76)
            print()
    
    def save_tables_to_file(self, tables_data: dict, output_path: Path):
        """Save extracted tables to JSON file."""
        
        # Prepare data for JSON serialization
        output_data = {
            'metadata': tables_data['metadata'],
            'languages': {}
        }
        
        if tables_data.get('en'):
            output_data['languages']['en'] = {
                'table_count': len(tables_data['en']['tables']),
                'tables': tables_data['en']['tables']
            }
        
        if tables_data.get('fr'):
            output_data['languages']['fr'] = {
                'table_count': len(tables_data['fr']['tables']),
                'tables': tables_data['fr']['tables']
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved tables to: {output_path}")
        print()


def main():
    """Main execution."""
    
    loader = ITAgreementTableLoader()
    
    # Load tables
    tables_data = loader.load_tables()
    
    if not tables_data:
        print("❌ Failed to load tables")
        return
    
    # Display summary
    loader.display_tables(tables_data)
    
    # Save to file
    output_dir = Path("data/tables")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "it_agreement_salary_tables.json"
    loader.save_tables_to_file(tables_data, output_file)
    
    # Final summary
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print()
    
    en_count = len(tables_data.get('en', {}).get('tables', []))
    fr_count = len(tables_data.get('fr', {}).get('tables', [])) if tables_data.get('fr') else 0
    
    print(f"✅ Successfully extracted {en_count + fr_count} salary tables")
    print(f"   English: {en_count} tables")
    print(f"   French: {fr_count} tables")
    print()
    print("Next Steps:")
    print("1. Review extracted tables in: data/tables/it_agreement_salary_tables.json")
    print("2. Implement table-aware chunking to preserve table integrity")
    print("3. Add 'is_table: true' metadata to table chunks")
    print("4. Test with salary lookup queries (e.g., 'IT-03 Step 5 salary?')")
    print()


if __name__ == "__main__":
    main()
