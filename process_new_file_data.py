#!/usr/bin/env python3
"""
Process and consolidate data from all tabs in New File.xlsx
Creates a clean, unified dataset for the dashboard
"""

import pandas as pd
import numpy as np
from pathlib import Path

def process_all_tabs():
    """Process all tabs from New File.xlsx and create a unified dataset"""
    
    # Read all sheets
    excel_file = "New File.xlsx"
    xls = pd.ExcelFile(excel_file)
    
    print(f"Processing {len(xls.sheet_names)} sheets from {excel_file}")
    
    # Store all processed dataframes
    all_dfs = []
    
    # Process each sheet
    for sheet_name in xls.sheet_names:
        print(f"\nProcessing sheet: {sheet_name}")
        
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Skip empty sheets
            if df.empty:
                print(f"  - Sheet '{sheet_name}' is empty, skipping...")
                continue
            
            # Add tab source
            df['tab_source'] = sheet_name
            
            # Standardize column names
            # First, identify if this is a provider sheet (has Last Name, First Name) or organization sheet
            cols = df.columns.str.lower()
            
            if 'last name' in cols or 'lastname' in cols:
                # Provider sheet - standardize provider columns
                df = standardize_provider_columns(df)
                df['record_type'] = 'provider'
            elif 'companyname' in cols or 'company name' in cols or 'medical group' in cols:
                # Organization sheet - standardize org columns
                df = standardize_org_columns(df)
                df['record_type'] = 'organization'
            else:
                # Unknown format - try to identify by content
                print(f"  - Unknown format for sheet '{sheet_name}', analyzing...")
                df = analyze_and_standardize(df)
            
            # Ensure NPI column is standardized
            df = standardize_npi_column(df)
            
            if 'npi' not in df.columns:
                print(f"  - No NPI column found in sheet '{sheet_name}', skipping...")
                continue
                
            # Add to collection
            all_dfs.append(df)
            print(f"  - Processed {len(df)} records")
            
        except Exception as e:
            print(f"  - Error processing sheet '{sheet_name}': {e}")
            continue
    
    # Combine all dataframes
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)
        
        # Create display columns for consistent naming
        combined_df = create_display_columns(combined_df)
        
        # Save the processed data
        output_file = "processed_npi_data.csv"
        combined_df.to_csv(output_file, index=False)
        print(f"\n✓ Saved {len(combined_df)} total records to {output_file}")
        
        # Create summary
        create_summary(combined_df)
        
        return combined_df
    else:
        print("\n✗ No data was successfully processed!")
        return None

def standardize_npi_column(df):
    """Standardize the NPI column name"""
    # Look for NPI column variations
    npi_variations = ['NPI', 'npi', 'Npi', 'provider_npi', 'Provider NPI']
    
    for col in df.columns:
        if col in npi_variations:
            df.rename(columns={col: 'npi'}, inplace=True)
            break
    
    # Convert NPI to string and clean
    if 'npi' in df.columns:
        df['npi'] = df['npi'].astype(str).str.strip()
        # Remove any .0 from float conversion
        df['npi'] = df['npi'].str.replace(r'\.0$', '', regex=True)
        # Remove invalid NPIs
        df = df[df['npi'].str.match(r'^\d{10}$', na=False)]
    
    return df

def standardize_provider_columns(df):
    """Standardize columns for provider records"""
    column_mapping = {
        'Last Name': 'last_name',
        'lastname': 'last_name',
        'First Name': 'first_name',
        'firstname': 'first_name',
        'Middle Name': 'middle_name',
        'middlename': 'middle_name',
        'City': 'city',
        'State': 'state',
        'Phone': 'phone',
        'Credential': 'credential',
        'Primary Specialty': 'primary_specialty',
        'Primary Hospital Affiliation': 'primary_hospital',
        'Secondary Hospital Affiliation': 'secondary_hospital',
        'Claim Based Specialty Primary': 'claim_specialty',
        'Role': 'role'
    }
    
    # Rename columns
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    return df

def standardize_org_columns(df):
    """Standardize columns for organization records"""
    column_mapping = {
        'medical group': 'organization_name',
        'Medical Group': 'organization_name',
        'CompanyName': 'organization_name',
        'Company Name': 'organization_name',
        'address': 'address_1',
        'Address': 'address_1',
        'address 2': 'address_2',
        'Addressline2': 'address_2',
        'city': 'city',
        'City': 'city',
        'state': 'state',
        'State': 'state',
        'zip': 'zip_code',
        'ZipCode': 'zip_code',
        'TIN': 'tin'
    }
    
    # Rename columns
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    return df

def analyze_and_standardize(df):
    """Try to identify and standardize unknown format"""
    # Check if it has unnamed columns (likely malformed data)
    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
    
    if len(unnamed_cols) > len(df.columns) / 2:
        # Mostly unnamed columns - try to infer structure
        print("    - Sheet has mostly unnamed columns, attempting to parse...")
        df['record_type'] = 'unknown'
    else:
        # Check content to determine type
        text_content = ' '.join(df.astype(str).iloc[0].values) if len(df) > 0 else ''
        if any(term in text_content.lower() for term in ['clinic', 'hospital', 'center', 'health']):
            df['record_type'] = 'organization'
        else:
            df['record_type'] = 'unknown'
    
    return df

def create_display_columns(df):
    """Create unified display columns for the dashboard"""
    # Create name display
    if 'last_name' in df.columns and 'first_name' in df.columns:
        df['name_display'] = df['first_name'].fillna('').astype(str) + ' ' + df['last_name'].fillna('').astype(str)
    elif 'organization_name' in df.columns:
        df['name_display'] = df['organization_name'].fillna('').astype(str)
    else:
        df['name_display'] = 'Unknown'
    
    df['name_display'] = df['name_display'].str.strip()
    
    # Create location display
    if 'city' in df.columns and 'state' in df.columns:
        df['location_display'] = df['city'].fillna('').astype(str) + ', ' + df['state'].fillna('').astype(str)
    else:
        df['location_display'] = 'Unknown'
    
    df['location_display'] = df['location_display'].str.strip(', ')
    
    # Ensure state is uppercase
    if 'state' in df.columns:
        df['state_display'] = df['state'].fillna('').astype(str).str.upper().str.strip()
    else:
        df['state_display'] = 'Unknown'
    
    # Tab display
    df['tab_display'] = df['tab_source'].fillna('Unknown')
    
    return df

def create_summary(df):
    """Create a summary of the processed data"""
    summary = {
        'Total Records': len(df),
        'Unique NPIs': df['npi'].nunique(),
        'Total Tabs': df['tab_source'].nunique(),
        'Provider Records': len(df[df['record_type'] == 'provider']),
        'Organization Records': len(df[df['record_type'] == 'organization']),
        'Unknown Records': len(df[df['record_type'] == 'unknown']),
        'States Covered': df['state_display'].nunique(),
        'Records by Tab': df['tab_source'].value_counts().to_dict()
    }
    
    print("\n📊 Data Summary:")
    print("=" * 50)
    for key, value in summary.items():
        if key != 'Records by Tab':
            print(f"{key}: {value:,}")
    
    print("\n📑 Records by Tab:")
    for tab, count in summary['Records by Tab'].items():
        print(f"  - {tab}: {count:,}")
    
    # Save summary
    with open('data_processing_summary.txt', 'w') as f:
        f.write("NPI Data Processing Summary\n")
        f.write("=" * 50 + "\n")
        for key, value in summary.items():
            if key != 'Records by Tab':
                f.write(f"{key}: {value}\n")
        f.write("\nRecords by Tab:\n")
        for tab, count in summary['Records by Tab'].items():
            f.write(f"  - {tab}: {count}\n")

if __name__ == "__main__":
    print("🔄 Starting NPI data processing...")
    process_all_tabs()
    print("\n✅ Processing complete!") 