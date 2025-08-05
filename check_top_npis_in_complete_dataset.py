#!/usr/bin/env python3
"""
Check if Top NPIs from Alignment Data Exist in Complete Dataset
Verify coverage of most frequent providers and practices
"""

import pandas as pd
import numpy as np

def check_top_npis_in_complete_dataset():
    """Check if top NPIs from alignment analysis exist in complete dataset"""
    print("🔍 CHECKING TOP NPIS IN COMPLETE DATASET")
    print("=" * 60)
    
    # Load enhanced alignment file to get top NPIs
    print("📋 Loading enhanced alignment file...")
    try:
        alignment_df = pd.read_csv('Alignment_Simpl_Enhanced_with_CORRECTED_NPIs.csv')
        print(f"✅ Loaded {len(alignment_df)} alignment records")
    except Exception as e:
        print(f"❌ Error loading alignment file: {e}")
        return
    
    # Load complete dataset
    print("📋 Loading complete NPI dataset...")
    try:
        complete_df = pd.read_csv('complete_npi_dataset_all_tabs.csv', low_memory=False)
        print(f"✅ Loaded {len(complete_df)} complete dataset records")
    except Exception as e:
        print(f"❌ Error loading complete dataset: {e}")
        return
    
    # Get all NPIs from complete dataset
    print("🔍 Extracting NPIs from complete dataset...")
    complete_npis = set()
    
    # Check for different NPI column names in complete dataset
    npi_columns_complete = []
    for col in complete_df.columns:
        if 'npi' in col.lower() or col.upper() == 'NPI':
            npi_columns_complete.append(col)
    
    print(f"📊 Found NPI columns in complete dataset: {npi_columns_complete}")
    
    for col in npi_columns_complete:
        try:
            col_npis = complete_df[col].dropna().astype(str)
            col_npis_clean = col_npis.str.replace('.0', '', regex=False)
            col_npis_clean = col_npis_clean[col_npis_clean != 'nan']
            col_npis_clean = col_npis_clean[col_npis_clean != '']
            complete_npis.update(col_npis_clean)
        except Exception as e:
            print(f"   ⚠️ Error processing column {col}: {e}")
    
    print(f"✅ Complete dataset contains {len(complete_npis)} unique NPIs")
    
    # Get top NPIs from alignment data
    top_providers = get_top_npis_from_alignment(alignment_df, 'NPI-1', 'Provider')
    top_practices = get_top_npis_from_alignment(alignment_df, 'NPI-2', 'Practice')
    
    # Check coverage
    print(f"\n🔍 CHECKING TOP PROVIDERS IN COMPLETE DATASET")
    print("=" * 60)
    check_npis_coverage(top_providers, complete_npis, complete_df, 'Provider')
    
    print(f"\n🔍 CHECKING TOP PRACTICES IN COMPLETE DATASET")  
    print("=" * 60)
    check_npis_coverage(top_practices, complete_npis, complete_df, 'Practice')
    
    # Create summary report
    create_coverage_summary(top_providers, top_practices, complete_npis, complete_df)

def get_top_npis_from_alignment(df, npi_col, entity_type):
    """Get top 10 NPIs from alignment data with details"""
    
    if npi_col not in df.columns:
        print(f"❌ Column {npi_col} not found in alignment data")
        return []
    
    # Clean and count NPIs
    npis = df[npi_col].dropna().astype(str)
    npis_clean = npis.str.replace('.0', '', regex=False)
    npis_clean = npis_clean[npis_clean != 'nan']
    npis_clean = npis_clean[npis_clean != '']
    
    npi_counts = npis_clean.value_counts()
    
    top_npis = []
    for rank, (npi, count) in enumerate(npi_counts.head(10).items(), 1):
        # Get entity details
        mask = df[npi_col].astype(str).str.replace('.0', '', regex=False) == npi
        matching_records = df[mask]
        
        if len(matching_records) > 0:
            record = matching_records.iloc[0]
            
            if entity_type == 'Provider':
                entity_name = record.get('NPI-1_Name', 'N/A')
                entity_state = record.get('NPI-1_State', 'N/A')
            else:  # Practice
                entity_name = record.get('NPI-2_Name', 'N/A')
                entity_state = record.get('NPI-2_State', 'N/A')
            
            top_npis.append({
                'rank': rank,
                'npi': npi,
                'count': count,
                'entity_name': entity_name,
                'entity_state': entity_state,
                'entity_type': entity_type
            })
    
    return top_npis

def check_npis_coverage(top_npis, complete_npis, complete_df, entity_type):
    """Check if top NPIs exist in complete dataset and get their details"""
    
    found_count = 0
    not_found_count = 0
    
    print(f"📊 TOP 10 {entity_type.upper()}S COVERAGE:")
    print(f"{'Rank':<4} | {'NPI':<12} | {'Frequency':<9} | {'In Complete?':<12} | {'Entity Name':<40}")
    print(f"{'-'*4} | {'-'*12} | {'-'*9} | {'-'*12} | {'-'*40}")
    
    for npi_info in top_npis:
        npi = npi_info['npi']
        rank = npi_info['rank']
        count = npi_info['count']
        entity_name = npi_info['entity_name'][:38] + "..." if len(npi_info['entity_name']) > 38 else npi_info['entity_name']
        
        if npi in complete_npis:
            status = "✅ FOUND"
            found_count += 1
        else:
            status = "❌ NOT FOUND"
            not_found_count += 1
        
        print(f"{rank:<4} | {npi:<12} | {count:<9} | {status:<12} | {entity_name:<40}")
    
    coverage_rate = found_count / len(top_npis) * 100 if top_npis else 0
    print(f"\n📈 {entity_type.upper()} COVERAGE SUMMARY:")
    print(f"   ✅ Found in complete dataset: {found_count}/{len(top_npis)} ({coverage_rate:.1f}%)")
    print(f"   ❌ Not found: {not_found_count}/{len(top_npis)}")
    
    # Show details for found NPIs
    if found_count > 0:
        print(f"\n📋 DETAILS FOR FOUND {entity_type.upper()}S:")
        show_found_npi_details(top_npis, complete_npis, complete_df)

def show_found_npi_details(top_npis, complete_npis, complete_df):
    """Show detailed information for NPIs found in complete dataset"""
    
    found_details = []
    
    for npi_info in top_npis:
        npi = npi_info['npi']
        
        if npi in complete_npis:
            # Find this NPI in complete dataset
            for col in complete_df.columns:
                if 'npi' in col.lower() or col.upper() == 'NPI':
                    try:
                        mask = complete_df[col].astype(str).str.replace('.0', '', regex=False) == npi
                        matches = complete_df[mask]
                        
                        if len(matches) > 0:
                            record = matches.iloc[0]
                            
                            # Extract relevant details
                            details = {
                                'npi': npi,
                                'rank': npi_info['rank'],
                                'alignment_count': npi_info['count'],
                                'alignment_name': npi_info['entity_name'],
                                'complete_first_name': record.get('First Name', record.get('PROVIDER_FIRST_NAME', 'N/A')),
                                'complete_last_name': record.get('Last Name', record.get('PROVIDER_LAST_NAME', 'N/A')),
                                'complete_organization': record.get('Organization Name', record.get('Organization', record.get('Company Name', 'N/A'))),
                                'complete_state': record.get('Provider Business Mailing Address State Name', record.get('State', 'N/A')),
                                'complete_specialty': record.get('Healthcare Provider Primary Taxonomy Description', record.get('Provider License Number Primary State Code', 'N/A'))
                            }
                            found_details.append(details)
                            break
                    except Exception as e:
                        continue
    
    # Display found details
    for detail in found_details[:5]:  # Show top 5
        print(f"\n   🔸 RANK {detail['rank']} - NPI: {detail['npi']}")
        print(f"      📊 Appears {detail['alignment_count']} times in alignment data")
        print(f"      🏷️ Alignment Name: {detail['alignment_name']}")
        
        if detail['complete_first_name'] != 'N/A' and detail['complete_last_name'] != 'N/A':
            print(f"      👤 Complete Dataset: {detail['complete_first_name']} {detail['complete_last_name']}")
        if detail['complete_organization'] != 'N/A':
            print(f"      🏢 Organization: {detail['complete_organization']}")
        if detail['complete_state'] != 'N/A':
            print(f"      📍 State: {detail['complete_state']}")
        if detail['complete_specialty'] != 'N/A':
            print(f"      🩺 Specialty: {detail['complete_specialty']}")

def create_coverage_summary(top_providers, top_practices, complete_npis, complete_df):
    """Create comprehensive coverage summary report"""
    print(f"\n📄 Creating coverage summary report...")
    
    summary_data = []
    
    # Process providers
    for provider in top_providers:
        npi = provider['npi']
        in_complete = npi in complete_npis
        
        summary_data.append({
            'Entity_Type': 'Provider',
            'Rank': provider['rank'],
            'NPI': npi,
            'Alignment_Frequency': provider['count'],
            'Alignment_Name': provider['entity_name'],
            'Alignment_State': provider['entity_state'],
            'In_Complete_Dataset': 'Yes' if in_complete else 'No',
            'Coverage_Status': 'Found' if in_complete else 'Missing'
        })
    
    # Process practices
    for practice in top_practices:
        npi = practice['npi']
        in_complete = npi in complete_npis
        
        summary_data.append({
            'Entity_Type': 'Practice',
            'Rank': practice['rank'],
            'NPI': npi,
            'Alignment_Frequency': practice['count'],
            'Alignment_Name': practice['entity_name'],
            'Alignment_State': practice['entity_state'],
            'In_Complete_Dataset': 'Yes' if in_complete else 'No',
            'Coverage_Status': 'Found' if in_complete else 'Missing'
        })
    
    # Save summary
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_filename = 'Top_NPIs_Complete_Dataset_Coverage.csv'
        summary_df.to_csv(summary_filename, index=False)
        print(f"✅ Coverage summary saved: {summary_filename}")

def main():
    """Main execution function"""
    print("🚀 TOP NPIS COVERAGE ANALYSIS")
    print("=" * 60)
    
    check_top_npis_in_complete_dataset()
    
    print(f"\n🎯 ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"This analysis shows which of your most frequent NPIs")
    print(f"are actually present in the complete dataset, revealing")
    print(f"potential gaps in your main NPI reference data.")

if __name__ == "__main__":
    main() 