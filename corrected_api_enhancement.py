#!/usr/bin/env python3
"""
CORRECTED: Enhance Alignment File with Live NPI API Lookups
- Column W (PROVIDER_FIRST_NAME) + Column X (PROVIDER_LAST_NAME) → NPI-1  
- Column AH (Practice Name) → NPI-2
"""

import pandas as pd
import requests
import time
import json
from typing import Dict, List, Optional

def get_provider_npi_by_name(first_name: str, last_name: str) -> Optional[Dict]:
    """Look up individual provider NPI by first and last name"""
    api_url = "https://npiregistry.cms.hhs.gov/api/"
    
    # Clean the names
    first_clean = str(first_name).strip() if pd.notna(first_name) else ""
    last_clean = str(last_name).strip() if pd.notna(last_name) else ""
    
    if not first_clean or not last_clean:
        return None
    
    params = {
        "version": "2.1",
        "first_name": first_clean,
        "last_name": last_clean,
        "enumeration_type": "NPI-1",  # Individual providers
        "limit": 5
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                # Return the first match with details
                result = data['results'][0]
                basic = result.get('basic', {})
                addresses = result.get('addresses', [{}])
                
                return {
                    'npi': result.get('number', ''),
                    'name': f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
                    'credential': basic.get('credential', ''),
                    'enumeration_type': basic.get('enumeration_type', ''),
                    'state': addresses[0].get('state', '') if addresses else '',
                    'city': addresses[0].get('city', '') if addresses else ''
                }
        
        return None
        
    except Exception as e:
        print(f"      ⚠️ Error looking up {first_name} {last_name}: {e}")
        return None

def get_organization_npi_by_name(org_name: str) -> Optional[Dict]:
    """Look up organization NPI by practice/organization name"""
    api_url = "https://npiregistry.cms.hhs.gov/api/"
    
    # Clean the organization name
    org_clean = str(org_name).strip() if pd.notna(org_name) else ""
    
    if not org_clean or org_clean.lower() in ['n/a', 'na', 'none', '']:
        return None
    
    params = {
        "version": "2.1",
        "organization_name": org_clean,
        "enumeration_type": "NPI-2",  # Organizations
        "limit": 5
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                # Return the first match with details
                result = data['results'][0]
                basic = result.get('basic', {})
                addresses = result.get('addresses', [{}])
                
                return {
                    'npi': result.get('number', ''),
                    'name': basic.get('organization_name', ''),
                    'enumeration_type': basic.get('enumeration_type', ''),
                    'state': addresses[0].get('state', '') if addresses else '',
                    'city': addresses[0].get('city', '') if addresses else ''
                }
        
        return None
        
    except Exception as e:
        print(f"      ⚠️ Error looking up organization {org_name}: {e}")
        return None

def test_corrected_enhancement():
    """Test the corrected enhancement on first 5 records"""
    print("🔧 TESTING CORRECTED API ENHANCEMENT")
    print("=" * 60)
    
    # Load the alignment file
    df = pd.read_csv('Alignment Simpl - Alignment Simpl.csv')
    print(f"✅ Loaded {len(df)} total records")
    
    # Verify correct columns
    print(f"\n📋 Verifying correct columns:")
    print(f"   Column W (23): {df.columns[22]} ← Provider First Name")
    print(f"   Column X (24): {df.columns[23]} ← Provider Last Name") 
    print(f"   Column AH (34): {df.columns[33]} ← Practice Name")
    
    # Test on first 5 records
    test_df = df.head(5).copy()
    print(f"\n🔍 Testing on first {len(test_df)} records with CORRECT columns")
    
    # Initialize new columns
    test_df['NPI-1'] = ''
    test_df['NPI-1_Name'] = ''
    test_df['NPI-1_State'] = ''
    test_df['NPI-2'] = ''
    test_df['NPI-2_Name'] = ''
    test_df['NPI-2_State'] = ''
    
    provider_found = 0
    practice_found = 0
    
    for index, row in test_df.iterrows():
        print(f"\n📋 Testing record {index + 1}/5")
        
        # Provider lookup (NPI-1) - Using CORRECT columns
        provider_first = row.get('PROVIDER_FIRST_NAME', '')
        provider_last = row.get('PROVIDER_LAST_NAME', '')
        
        print(f"   🔍 Provider: {provider_first} {provider_last}")
        
        provider_info = get_provider_npi_by_name(provider_first, provider_last)
        if provider_info:
            test_df.at[index, 'NPI-1'] = provider_info['npi']
            test_df.at[index, 'NPI-1_Name'] = provider_info['name']
            test_df.at[index, 'NPI-1_State'] = provider_info['state']
            provider_found += 1
            print(f"      ✅ Found NPI-1: {provider_info['npi']} - {provider_info['name']}")
        else:
            print(f"      ❌ No NPI-1 found")
        
        time.sleep(1)
        
        # Practice lookup (NPI-2) - Using CORRECT column
        practice_name = row.get('Practice Name', '')
        
        print(f"   🏢 Practice: {practice_name}")
        
        org_info = get_organization_npi_by_name(practice_name)
        if org_info:
            test_df.at[index, 'NPI-2'] = org_info['npi']
            test_df.at[index, 'NPI-2_Name'] = org_info['name']
            test_df.at[index, 'NPI-2_State'] = org_info['state']
            practice_found += 1
            print(f"      ✅ Found NPI-2: {org_info['npi']} - {org_info['name']}")
        else:
            print(f"      ❌ No NPI-2 found")
        
        time.sleep(1)
    
    # Results
    print(f"\n🎯 CORRECTED TEST RESULTS:")
    print("=" * 60)
    print(f"✅ Provider NPIs found: {provider_found}/5 ({provider_found/5*100:.1f}%)")
    print(f"✅ Practice NPIs found: {practice_found}/5 ({practice_found/5*100:.1f}%)")
    
    # Show results table
    print(f"\n📋 CORRECTED ENHANCED TEST RECORDS:")
    print("-" * 140)
    
    display_cols = ['PROVIDER_FIRST_NAME', 'PROVIDER_LAST_NAME', 'Practice Name', 
                   'NPI-1', 'NPI-1_Name', 'NPI-2', 'NPI-2_Name']
    
    for col in display_cols:
        if col in test_df.columns:
            print(f"{col:<20}", end=" | ")
    print()
    print("-" * 140)
    
    for _, row in test_df.iterrows():
        for col in display_cols:
            if col in test_df.columns:
                value = str(row[col])[:19] if pd.notna(row[col]) else 'N/A'
                print(f"{value:<20}", end=" | ")
        print()
    
    # Save test results
    test_df.to_csv('Test_Corrected_Enhanced_5_Records.csv', index=False)
    print(f"\n💾 Test results saved to: Test_Corrected_Enhanced_5_Records.csv")
    
    return provider_found, practice_found

def run_full_corrected_enhancement():
    """Run the corrected enhancement on all records"""
    print("🚀 RUNNING FULL CORRECTED API ENHANCEMENT")
    print("=" * 70)
    
    # Load the alignment file
    df = pd.read_csv('Alignment Simpl - Alignment Simpl.csv')
    print(f"✅ Loaded {len(df)} records")
    
    # Initialize new columns
    df['NPI-1'] = ''  # Individual provider NPI
    df['NPI-1_Name'] = ''  # Matched provider name
    df['NPI-1_State'] = ''  # Provider state
    df['NPI-2'] = ''  # Practice/organization NPI
    df['NPI-2_Name'] = ''  # Matched organization name
    df['NPI-2_State'] = ''  # Organization state
    
    # Process records
    total_records = len(df)
    provider_found = 0
    practice_found = 0
    
    print(f"\n🔍 Processing {total_records} records with CORRECT columns...")
    print(f"⏱️ Estimated time: {total_records * 2/60:.1f} minutes (with API rate limiting)")
    
    for index, row in df.iterrows():
        print(f"\n   📋 Processing record {index + 1}/{total_records}")
        
        # Look up individual provider NPI (NPI-1) - CORRECTED
        provider_first = row.get('PROVIDER_FIRST_NAME', '')
        provider_last = row.get('PROVIDER_LAST_NAME', '')
        
        print(f"      🔍 Looking up provider: {provider_first} {provider_last}")
        
        provider_info = get_provider_npi_by_name(provider_first, provider_last)
        if provider_info:
            df.at[index, 'NPI-1'] = provider_info['npi']
            df.at[index, 'NPI-1_Name'] = provider_info['name']
            df.at[index, 'NPI-1_State'] = provider_info['state']
            provider_found += 1
            print(f"         ✅ Found NPI-1: {provider_info['npi']} - {provider_info['name']}")
        else:
            print(f"         ❌ No NPI-1 found")
        
        # Small delay between requests
        time.sleep(1)
        
        # Look up practice/organization NPI (NPI-2) - CORRECTED
        practice_name = row.get('Practice Name', '')
        
        print(f"      🏢 Looking up practice: {practice_name}")
        
        org_info = get_organization_npi_by_name(practice_name)
        if org_info:
            df.at[index, 'NPI-2'] = org_info['npi']
            df.at[index, 'NPI-2_Name'] = org_info['name']
            df.at[index, 'NPI-2_State'] = org_info['state']
            practice_found += 1
            print(f"         ✅ Found NPI-2: {org_info['npi']} - {org_info['name']}")
        else:
            print(f"         ❌ No NPI-2 found")
        
        # Delay between records
        time.sleep(1)
        
        # Progress checkpoint every 25 records
        if (index + 1) % 25 == 0:
            print(f"\n   📊 Progress: {index + 1}/{total_records} ({(index + 1)/total_records*100:.1f}%)")
            print(f"       Providers found: {provider_found}")
            print(f"       Practices found: {practice_found}")
    
    # Save enhanced file
    output_filename = 'Alignment_Simpl_Enhanced_with_CORRECTED_NPIs.csv'
    print(f"\n💾 Saving enhanced file as: {output_filename}")
    
    df.to_csv(output_filename, index=False)
    
    # Final summary
    print(f"\n🎯 CORRECTED ENHANCEMENT COMPLETE!")
    print("=" * 70)
    print(f"📊 Total records processed: {total_records}")
    print(f"✅ Provider NPIs found (NPI-1): {provider_found} ({provider_found/total_records*100:.1f}%)")
    print(f"✅ Practice NPIs found (NPI-2): {practice_found} ({practice_found/total_records*100:.1f}%)")
    print(f"💾 Enhanced file saved: {output_filename}")

def main():
    """Main execution function"""
    print("🔧 CORRECTED NPI API ENHANCEMENT")
    print("=" * 70)
    
    # First test on 5 records
    provider_found, practice_found = test_corrected_enhancement()
    
    if provider_found > 0 or practice_found > 0:
        print(f"\n✅ Test successful! Found {provider_found} providers and {practice_found} practices")
        
        response = input("\n🚀 Run full enhancement on all 697 records? (y/n): ")
        if response.lower() == 'y':
            run_full_corrected_enhancement()
        else:
            print("👍 Test completed. Full enhancement cancelled.")
    else:
        print(f"\n⚠️ Test found no matches. Check column mapping before proceeding.")

if __name__ == "__main__":
    main() 