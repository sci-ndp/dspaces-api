#!/usr/bin/env python3
"""
Test script to verify column name mapping between CSV and DataSpaces.
"""

from api.helpers.file_download import get_dynamic_ingestion_path


# First, let's examine the CSV structure and understand column cleaning
def test_column_cleaning():
    print("=== Testing Column Name Cleaning ===")
    
    # Read the CSV header manually
    with open(get_dynamic_ingestion_path("salt_lake_county_utah"), "r") as f:
        header = f.readline().strip()
        columns = [col.strip('"') for col in header.split(',')]
    
    print(f"Original CSV columns ({len(columns)}):")
    for i, col in enumerate(columns):
        print(f"  {i+1:2d}. '{col}'")
    
    # Apply the same cleaning logic as the ingestion
    def clean_column_name(col_name: str) -> str:
        """Clean column name for DataSpaces storage by removing special characters."""
        return (col_name.replace(" ", "_")
                        .replace("(", "")
                        .replace(")", "")
                        .replace("/", "_")
                        .replace("-", "_"))
    
    print("\nCleaned columns for DataSpaces storage:")
    cleaned_columns = {}
    for i, col in enumerate(columns):
        cleaned = clean_column_name(col)
        cleaned_columns[col] = cleaned
        print(f"  {i+1:2d}. '{col}' -> '{cleaned}'")
    
    return columns, cleaned_columns

if __name__ == "__main__":
    # Test column cleaning
    original_cols, cleaned_cols = test_column_cleaning()
