#!/usr/bin/env python3
"""
M365 Unified Audit Log JSON Extractor

This script extracts and processes the AuditData column from M365 Unified Audit Log CSV files.
The AuditData column contains JSON formatted data that this script will parse and extract.

Usage:
    python m365_audit_extractor.py input_file.csv [output_file.json]

Features:
- Extracts JSON data from AuditData column
- Validates JSON format
- Provides multiple output options (pretty JSON, CSV, or individual JSON files)
- Handles malformed JSON gracefully
- Provides statistics on processing results
"""

import csv
import json
import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

class M365AuditExtractor:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file
        self.extracted_data = []
        self.errors = []
        self.stats = {
            'total_rows': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'empty_audit_data': 0
        }
    
    def extract_audit_data(self) -> List[Dict[str, Any]]:
        """Extract JSON data from AuditData column in CSV file."""
        print(f"Processing file: {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8-sig') as csvfile:
                # Auto-detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Check if AuditData column exists
                if 'AuditData' not in reader.fieldnames:
                    raise ValueError("AuditData column not found in CSV file")
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    self.stats['total_rows'] += 1
                    audit_data = row.get('AuditData', '').strip()
                    
                    if not audit_data:
                        self.stats['empty_audit_data'] += 1
                        continue
                    
                    try:
                        # Parse JSON data
                        json_data = json.loads(audit_data)
                        
                        # Add metadata
                        extracted_record = {
                            'row_number': row_num,
                            'original_row_data': {k: v for k, v in row.items() if k != 'AuditData'},
                            'audit_data': json_data
                        }
                        
                        self.extracted_data.append(extracted_record)
                        self.stats['successful_extractions'] += 1
                        
                    except json.JSONDecodeError as e:
                        error_info = {
                            'row_number': row_num,
                            'error': str(e),
                            'raw_data': audit_data[:200] + '...' if len(audit_data) > 200 else audit_data
                        }
                        self.errors.append(error_info)
                        self.stats['failed_extractions'] += 1
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")
        
        return self.extracted_data
    
    def save_as_json(self, output_file: str = None, pretty: bool = True) -> None:
        """Save extracted data as JSON file."""
        if not output_file:
            base_name = os.path.splitext(self.input_file)[0]
            output_file = f"{base_name}_extracted_audit_data.json"
        
        output_data = {
            'metadata': {
                'source_file': self.input_file,
                'extraction_timestamp': datetime.now().isoformat(),
                'statistics': self.stats
            },
            'extracted_records': self.extracted_data,
            'errors': self.errors
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(output_data, f, ensure_ascii=False)
        
        print(f"Extracted data saved to: {output_file}")
    
    def save_audit_data_only(self, output_file: str = None) -> None:
        """Save only the AuditData JSON objects as a JSON array."""
        if not output_file:
            base_name = os.path.splitext(self.input_file)[0]
            output_file = f"{base_name}_audit_data_only.json"
        
        audit_data_only = [record['audit_data'] for record in self.extracted_data]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data_only, f, indent=2, ensure_ascii=False)
        
        print(f"Audit data only saved to: {output_file}")
    
    def save_as_csv(self, output_file: str = None) -> None:
        """Save extracted data as flattened CSV."""
        if not output_file:
            base_name = os.path.splitext(self.input_file)[0]
            output_file = f"{base_name}_flattened_audit_data.csv"
        
        if not self.extracted_data:
            print("No data to save as CSV")
            return
        
        # Flatten the JSON data
        flattened_records = []
        for record in self.extracted_data:
            flat_record = record['original_row_data'].copy()
            flat_record['row_number'] = record['row_number']
            
            # Flatten audit_data
            def flatten_dict(d, parent_key='', sep='_'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    elif isinstance(v, list):
                        items.append((new_key, json.dumps(v)))
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            flattened_audit = flatten_dict(record['audit_data'], 'audit')
            flat_record.update(flattened_audit)
            flattened_records.append(flat_record)
        
        # Write CSV
        if flattened_records:
            fieldnames = set()
            for record in flattened_records:
                fieldnames.update(record.keys())
            fieldnames = sorted(fieldnames)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_records)
            
            print(f"Flattened CSV saved to: {output_file}")
    
    def save_individual_json_files(self, output_dir: str = None) -> None:
        """Save each audit record as individual JSON files."""
        if not output_dir:
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_dir = f"{base_name}_individual_audit_records"
        
        os.makedirs(output_dir, exist_ok=True)
        
        for i, record in enumerate(self.extracted_data):
            filename = f"audit_record_{record['row_number']:04d}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(record['audit_data'], f, indent=2, ensure_ascii=False)
        
        print(f"Individual JSON files saved to directory: {output_dir}")
    
    def print_statistics(self) -> None:
        """Print processing statistics."""
        print("\n" + "="*50)
        print("PROCESSING STATISTICS")
        print("="*50)
        print(f"Total rows processed: {self.stats['total_rows']}")
        print(f"Successful extractions: {self.stats['successful_extractions']}")
        print(f"Failed extractions: {self.stats['failed_extractions']}")
        print(f"Empty AuditData fields: {self.stats['empty_audit_data']}")
        
        if self.errors:
            print(f"\nFirst few errors:")
            for error in self.errors[:3]:
                print(f"  Row {error['row_number']}: {error['error']}")
            if len(self.errors) > 3:
                print(f"  ... and {len(self.errors) - 3} more errors")
    
    def preview_data(self, num_records: int = 3) -> None:
        """Preview extracted data."""
        if not self.extracted_data:
            print("No data extracted to preview")
            return
        
        print(f"\nPREVIEW - First {min(num_records, len(self.extracted_data))} records:")
        print("-" * 50)
        
        for i, record in enumerate(self.extracted_data[:num_records]):
            print(f"\nRecord {i+1} (Row {record['row_number']}):")
            print(f"Original data keys: {list(record['original_row_data'].keys())}")
            print(f"Audit data keys: {list(record['audit_data'].keys())}")
            
            # Show some key audit data fields if they exist
            audit_data = record['audit_data']
            preview_fields = ['Operation', 'UserId', 'CreationTime', 'Workload', 'ObjectId']
            for field in preview_fields:
                if field in audit_data:
                    print(f"  {field}: {audit_data[field]}")

def main():
    parser = argparse.ArgumentParser(description='Extract JSON data from M365 Unified Audit Log CSV files')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument('--format', choices=['json', 'csv', 'individual', 'audit-only'], 
                       default='json', help='Output format (default: json)')
    parser.add_argument('--preview', action='store_true', help='Show preview of extracted data')
    parser.add_argument('--no-pretty', action='store_true', help='Disable pretty printing for JSON')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    try:
        # Create extractor and process file
        extractor = M365AuditExtractor(args.input_file, args.output)
        extractor.extract_audit_data()
        
        # Print statistics
        extractor.print_statistics()
        
        # Preview data if requested
        if args.preview:
            extractor.preview_data()
        
        # Save in requested format
        if args.format == 'json':
            extractor.save_as_json(args.output, pretty=not args.no_pretty)
        elif args.format == 'csv':
            extractor.save_as_csv(args.output)
        elif args.format == 'individual':
            extractor.save_individual_json_files(args.output)
        elif args.format == 'audit-only':
            extractor.save_audit_data_only(args.output)
        
        print(f"\nProcessing completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
