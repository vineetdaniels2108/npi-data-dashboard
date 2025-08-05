#!/usr/bin/env python3
"""
Map Enhanced NPIs to Ellkay Complete Dataset
Check coverage of live API-sourced NPIs against local Ellkay dataset
"""

import pandas as pd
import numpy as np

def analyze_enhanced_npi_coverage():
    """Analyze coverage of enhanced NPIs against Ellkay complete dataset"""
    print("🔍 MAPPING ENHANCED NPIs TO ELLKAY COMPLETE DATASET")
    print("=" * 70)
    
    # Load enhanced alignment file with live API NPIs
    print("📋 Loading enhanced alignment file...")
    try:
        enhanced_df = pd.read_csv('Alignment_Simpl_Enhanced_with_CORRECTED_NPIs.csv')
        print(f"✅ Loaded {len(enhanced_df)} enhanced alignment records")
    except Exception as e:
        print(f"❌ Error loading enhanced file: {e}")
        return
    
    # Load Ellkay complete dataset
    print("\n📊 Loading Ellkay complete dataset...")
    try:
        ellkay_df = pd.read_csv('complete_npi_dataset_all_tabs.csv', low_memory=False)
        print(f"✅ Loaded {len(ellkay_df)} Ellkay dataset records")
    except Exception as e:
        print(f"❌ Error loading Ellkay dataset: {e}")
        return
    
    # Extract NPIs from Ellkay dataset
    print("\n🔍 Extracting NPIs from Ellkay dataset...")
    ellkay_npis = set()
    
    # Check both possible NPI columns
    if 'NPI' in ellkay_df.columns:
        npi_upper = ellkay_df['NPI'].dropna().astype(str).str.replace('.0', '', regex=False)
        ellkay_npis.update(npi_upper)
        print(f"   📈 Found {len(npi_upper)} NPIs in 'NPI' column")
    
    if 'npi' in ellkay_df.columns:
        npi_lower = ellkay_df['npi'].dropna().astype(str).str.replace('.0', '', regex=False)
        ellkay_npis.update(npi_lower)
        print(f"   📈 Found {len(npi_lower)} NPIs in 'npi' column")
    
    print(f"📊 Total unique NPIs in Ellkay dataset: {len(ellkay_npis)}")
    
    # Analyze NPI-1 (Individual Provider NPIs)
    print(f"\n🔍 ANALYZING NPI-1 (INDIVIDUAL PROVIDER) COVERAGE")
    print("-" * 60)
    
    # Get NPI-1 values
    npi1_values = enhanced_df['NPI-1'].dropna().astype(str)
    npi1_unique = npi1_values.unique()
    npi1_unique = [npi for npi in npi1_unique if npi != '' and npi != 'nan']
    
    print(f"📋 Enhanced NPIs (NPI-1): {len(npi1_unique)} unique individual provider NPIs")
    
    # Check coverage
    npi1_found = []
    npi1_missing = []
    
    for npi in npi1_unique:
        clean_npi = str(npi).replace('.0', '')
        if clean_npi in ellkay_npis:
            npi1_found.append(clean_npi)
        else:
            npi1_missing.append(clean_npi)
    
    npi1_coverage = len(npi1_found) / len(npi1_unique) * 100 if npi1_unique else 0
    
    print(f"✅ Found in Ellkay: {len(npi1_found)} NPIs ({npi1_coverage:.1f}%)")
    print(f"❌ Missing from Ellkay: {len(npi1_missing)} NPIs ({100-npi1_coverage:.1f}%)")
    
    # Show sample found NPIs
    if npi1_found:
        print(f"\n🎯 Sample NPI-1 matches in Ellkay:")
        for i, npi in enumerate(npi1_found[:10]):
            print(f"   {i+1:2d}. {npi}")
        if len(npi1_found) > 10:
            print(f"   ... and {len(npi1_found) - 10} more")
    
    # Show sample missing NPIs
    if npi1_missing:
        print(f"\n❌ Sample NPI-1 missing from Ellkay:")
        for i, npi in enumerate(npi1_missing[:10]):
            print(f"   {i+1:2d}. {npi}")
        if len(npi1_missing) > 10:
            print(f"   ... and {len(npi1_missing) - 10} more")
    
    # Analyze NPI-2 (Practice/Organization NPIs)
    print(f"\n🏢 ANALYZING NPI-2 (PRACTICE/ORGANIZATION) COVERAGE")
    print("-" * 60)
    
    # Get NPI-2 values
    npi2_values = enhanced_df['NPI-2'].dropna().astype(str)
    npi2_unique = npi2_values.unique()
    npi2_unique = [npi for npi in npi2_unique if npi != '' and npi != 'nan']
    
    print(f"📋 Enhanced NPIs (NPI-2): {len(npi2_unique)} unique practice/organization NPIs")
    
    # Check coverage
    npi2_found = []
    npi2_missing = []
    
    for npi in npi2_unique:
        clean_npi = str(npi).replace('.0', '')
        if clean_npi in ellkay_npis:
            npi2_found.append(clean_npi)
        else:
            npi2_missing.append(clean_npi)
    
    npi2_coverage = len(npi2_found) / len(npi2_unique) * 100 if npi2_unique else 0
    
    print(f"✅ Found in Ellkay: {len(npi2_found)} NPIs ({npi2_coverage:.1f}%)")
    print(f"❌ Missing from Ellkay: {len(npi2_missing)} NPIs ({100-npi2_coverage:.1f}%)")
    
    # Show sample found NPIs
    if npi2_found:
        print(f"\n🎯 Sample NPI-2 matches in Ellkay:")
        for i, npi in enumerate(npi2_found[:10]):
            print(f"   {i+1:2d}. {npi}")
        if len(npi2_found) > 10:
            print(f"   ... and {len(npi2_found) - 10} more")
    
    # Show sample missing NPIs
    if npi2_missing:
        print(f"\n❌ Sample NPI-2 missing from Ellkay:")
        for i, npi in enumerate(npi2_missing[:10]):
            print(f"   {i+1:2d}. {npi}")
        if len(npi2_missing) > 10:
            print(f"   ... and {len(npi2_missing) - 10} more")
    
    # Combined Analysis
    print(f"\n📊 COMBINED ENHANCED NPI ANALYSIS")
    print("=" * 70)
    
    all_enhanced_npis = set(npi1_unique + npi2_unique)
    total_enhanced = len(all_enhanced_npis)
    all_found = set(npi1_found + npi2_found)
    total_found = len(all_found)
    
    overall_coverage = total_found / total_enhanced * 100 if total_enhanced else 0
    
    print(f"📋 Total unique enhanced NPIs (NPI-1 + NPI-2): {total_enhanced}")
    print(f"✅ Found in Ellkay dataset: {total_found} ({overall_coverage:.1f}%)")
    print(f"❌ Missing from Ellkay dataset: {total_enhanced - total_found} ({100-overall_coverage:.1f}%)")
    
    # Create detailed coverage report
    create_coverage_report(enhanced_df, ellkay_npis, npi1_found, npi1_missing, npi2_found, npi2_missing)
    
    return {
        'npi1_coverage': npi1_coverage,
        'npi2_coverage': npi2_coverage,
        'overall_coverage': overall_coverage,
        'npi1_found': len(npi1_found),
        'npi1_missing': len(npi1_missing),
        'npi2_found': len(npi2_found),
        'npi2_missing': len(npi2_missing)
    }

def create_coverage_report(enhanced_df, ellkay_npis, npi1_found, npi1_missing, npi2_found, npi2_missing):
    """Create detailed coverage report CSV"""
    print(f"\n📄 Creating detailed coverage report...")
    
    # Prepare report data
    report_data = []
    
    for index, row in enhanced_df.iterrows():
        npi1 = str(row.get('NPI-1', '')).replace('.0', '') if pd.notna(row.get('NPI-1')) else ''
        npi2 = str(row.get('NPI-2', '')).replace('.0', '') if pd.notna(row.get('NPI-2')) else ''
        
        # NPI-1 status
        npi1_status = 'Not Found'
        if npi1 and npi1 != 'nan' and npi1 != '':
            if npi1 in ellkay_npis:
                npi1_status = 'Found in Ellkay'
            else:
                npi1_status = 'Missing from Ellkay'
        else:
            npi1_status = 'No NPI-1'
        
        # NPI-2 status
        npi2_status = 'Not Found'
        if npi2 and npi2 != 'nan' and npi2 != '':
            if npi2 in ellkay_npis:
                npi2_status = 'Found in Ellkay'
            else:
                npi2_status = 'Missing from Ellkay'
        else:
            npi2_status = 'No NPI-2'
        
        report_data.append({
            'Record_Index': index + 1,
            'Provider_First_Name': row.get('PROVIDER_FIRST_NAME', ''),
            'Provider_Last_Name': row.get('PROVIDER_LAST_NAME', ''),
            'Practice_Name': row.get('Practice Name', ''),
            'NPI-1': npi1,
            'NPI-1_Name': row.get('NPI-1_Name', ''),
            'NPI-1_Status': npi1_status,
            'NPI-2': npi2,
            'NPI-2_Name': row.get('NPI-2_Name', ''),
            'NPI-2_Status': npi2_status
        })
    
    # Create DataFrame and save
    report_df = pd.DataFrame(report_data)
    report_filename = 'Enhanced_NPIs_Ellkay_Coverage_Report.csv'
    report_df.to_csv(report_filename, index=False)
    
    print(f"✅ Coverage report saved: {report_filename}")
    print(f"📋 Report contains {len(report_df)} records with detailed coverage analysis")

def main():
    """Main execution function"""
    print("🚀 ENHANCED NPI TO ELLKAY MAPPING ANALYSIS")
    print("=" * 70)
    
    results = analyze_enhanced_npi_coverage()
    
    if results:
        print(f"\n🎯 FINAL SUMMARY:")
        print("=" * 70)
        print(f"🔍 NPI-1 (Individual) Coverage: {results['npi1_coverage']:.1f}%")
        print(f"🏢 NPI-2 (Practice) Coverage: {results['npi2_coverage']:.1f}%")
        print(f"📊 Overall Enhanced NPI Coverage: {results['overall_coverage']:.1f}%")
        print(f"💡 This shows how many live API NPIs exist in your local Ellkay dataset")

if __name__ == "__main__":
    main() 