#!/usr/bin/env python3
"""
Analyze NPI Frequency in Alignment Dataset
Find the top 10 most frequently occurring NPIs across different columns
"""

import pandas as pd
import numpy as np

def analyze_npi_frequency():
    """Analyze frequency of NPIs in the alignment dataset"""
    print("📊 NPI FREQUENCY ANALYSIS - ALIGNMENT DATASET")
    print("=" * 60)
    
    # Load enhanced alignment file
    print("📋 Loading enhanced alignment file...")
    try:
        df = pd.read_csv('Alignment_Simpl_Enhanced_with_CORRECTED_NPIs.csv')
        print(f"✅ Loaded {len(df)} records")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Total records: {len(df)}")
    print(f"   Total columns: {len(df.columns)}")
    
    # Analyze different NPI columns
    npi_columns = {
        'Original_NPI': 'NPI',  # Column V (22)
        'Practice_NPI': 'Practice NPI',  # Column AF (32) 
        'API_Provider_NPI': 'NPI-1',  # Enhanced individual provider NPI
        'API_Practice_NPI': 'NPI-2'   # Enhanced practice NPI
    }
    
    results = {}
    
    for analysis_name, col_name in npi_columns.items():
        if col_name in df.columns:
            print(f"\n🔍 ANALYZING {analysis_name.replace('_', ' ').upper()} ({col_name})")
            print("-" * 50)
            
            # Clean and prepare NPIs
            npis = df[col_name].dropna().astype(str)
            npis_clean = npis.str.replace('.0', '', regex=False)
            npis_clean = npis_clean[npis_clean != 'nan']
            npis_clean = npis_clean[npis_clean != '']
            
            if len(npis_clean) == 0:
                print(f"   ❌ No valid NPIs found in {col_name}")
                continue
            
            # Count frequencies
            npi_counts = npis_clean.value_counts()
            total_npis = len(npis_clean)
            unique_npis = len(npi_counts)
            
            print(f"   📈 Total NPI entries: {total_npis}")
            print(f"   🔢 Unique NPIs: {unique_npis}")
            print(f"   📊 Average frequency: {total_npis/unique_npis:.1f}")
            
            # Store results
            results[analysis_name] = {
                'total': total_npis,
                'unique': unique_npis,
                'top_10': npi_counts.head(10)
            }
            
            # Show top 10
            print(f"\n   🏆 TOP 10 MOST FREQUENT NPIs:")
            print(f"   {'Rank':<4} | {'NPI':<12} | {'Count':<5} | {'%':<6}")
            print(f"   {'-'*4} | {'-'*12} | {'-'*5} | {'-'*6}")
            
            for rank, (npi, count) in enumerate(npi_counts.head(10).items(), 1):
                percentage = count / total_npis * 100
                print(f"   {rank:<4} | {npi:<12} | {count:<5} | {percentage:<6.1f}")
            
            # Look up details for top NPIs
            if analysis_name in ['API_Provider_NPI', 'API_Practice_NPI']:
                print(f"\n   📋 DETAILS FOR TOP 3 NPIs:")
                lookup_npi_details(df, col_name, npi_counts.head(3), analysis_name)
        else:
            print(f"\n❌ Column '{col_name}' not found in dataset")
    
    # Cross-analysis
    print(f"\n🔄 CROSS-ANALYSIS")
    print("=" * 60)
    cross_analyze_npis(df, results)
    
    # Create summary report
    create_frequency_report(df, results)
    
    return results

def lookup_npi_details(df, npi_col, top_npis, analysis_type):
    """Look up additional details for top NPIs"""
    
    for npi, count in top_npis.items():
        # Find records with this NPI
        mask = df[npi_col].astype(str).str.replace('.0', '', regex=False) == npi
        matching_records = df[mask]
        
        if len(matching_records) > 0:
            record = matching_records.iloc[0]
            
            # Get relevant details based on NPI type
            if analysis_type == 'API_Provider_NPI':
                provider_name = record.get('NPI-1_Name', 'N/A')
                state = record.get('NPI-1_State', 'N/A')
                print(f"      🔸 {npi}: {provider_name} ({state}) - appears {count} times")
            elif analysis_type == 'API_Practice_NPI':
                practice_name = record.get('NPI-2_Name', 'N/A')
                state = record.get('NPI-2_State', 'N/A')
                print(f"      🔸 {npi}: {practice_name} ({state}) - appears {count} times")
            else:
                # For original NPIs, use provider names from the data
                provider_first = record.get('PROVIDER_FIRST_NAME', 'N/A')
                provider_last = record.get('PROVIDER_LAST_NAME', 'N/A')
                practice_name = record.get('Practice Name', 'N/A')
                print(f"      🔸 {npi}: {provider_first} {provider_last} @ {practice_name} - appears {count} times")

def cross_analyze_npis(df, results):
    """Cross-analyze relationships between different NPI columns"""
    
    # Compare original vs API NPIs
    if 'Original_NPI' in results and 'API_Provider_NPI' in results:
        print(f"📊 Original NPI vs API Provider NPI:")
        
        orig_npis = set(df['NPI'].dropna().astype(str).str.replace('.0', '', regex=False))
        api_npis = set(df['NPI-1'].dropna().astype(str).str.replace('.0', '', regex=False))
        
        orig_npis = {npi for npi in orig_npis if npi != 'nan' and npi != ''}
        api_npis = {npi for npi in api_npis if npi != 'nan' and npi != ''}
        
        overlap = orig_npis & api_npis
        orig_only = orig_npis - api_npis
        api_only = api_npis - orig_npis
        
        print(f"   🔄 NPIs in both: {len(overlap)}")
        print(f"   📋 Original only: {len(orig_only)}")
        print(f"   🆕 API only: {len(api_only)}")
        
        if len(overlap) > 0:
            overlap_rate = len(overlap) / len(orig_npis) * 100
            print(f"   📈 Overlap rate: {overlap_rate:.1f}%")
    
    # Compare Practice NPIs
    if 'Practice_NPI' in results and 'API_Practice_NPI' in results:
        print(f"\n📊 Practice NPI vs API Practice NPI:")
        
        prac_npis = set(df['Practice NPI'].dropna().astype(str).str.replace('.0', '', regex=False))
        api_prac_npis = set(df['NPI-2'].dropna().astype(str).str.replace('.0', '', regex=False))
        
        prac_npis = {npi for npi in prac_npis if npi != 'nan' and npi != ''}
        api_prac_npis = {npi for npi in api_prac_npis if npi != 'nan' and npi != ''}
        
        overlap_prac = prac_npis & api_prac_npis
        
        print(f"   🔄 NPIs in both: {len(overlap_prac)}")
        print(f"   📋 Practice only: {len(prac_npis - api_prac_npis)}")
        print(f"   🆕 API only: {len(api_prac_npis - prac_npis)}")

def create_frequency_report(df, results):
    """Create detailed frequency analysis report"""
    print(f"\n📄 Creating detailed frequency report...")
    
    report_data = []
    
    # Compile top NPIs from all categories
    for analysis_name, data in results.items():
        if 'top_10' in data:
            for rank, (npi, count) in enumerate(data['top_10'].items(), 1):
                percentage = count / data['total'] * 100
                
                # Get additional details
                col_name = {'Original_NPI': 'NPI', 'Practice_NPI': 'Practice NPI', 
                           'API_Provider_NPI': 'NPI-1', 'API_Practice_NPI': 'NPI-2'}[analysis_name]
                
                mask = df[col_name].astype(str).str.replace('.0', '', regex=False) == npi
                matching_records = df[mask]
                
                if len(matching_records) > 0:
                    record = matching_records.iloc[0]
                    
                    if analysis_name == 'API_Provider_NPI':
                        entity_name = record.get('NPI-1_Name', 'N/A')
                        entity_state = record.get('NPI-1_State', 'N/A')
                        entity_type = 'Provider'
                    elif analysis_name == 'API_Practice_NPI':
                        entity_name = record.get('NPI-2_Name', 'N/A')
                        entity_state = record.get('NPI-2_State', 'N/A')
                        entity_type = 'Practice'
                    else:
                        entity_name = f"{record.get('PROVIDER_FIRST_NAME', '')} {record.get('PROVIDER_LAST_NAME', '')}"
                        entity_state = record.get('Provider Address State', 'N/A')
                        entity_type = 'Original'
                    
                    report_data.append({
                        'Analysis_Category': analysis_name.replace('_', ' '),
                        'Rank': rank,
                        'NPI': npi,
                        'Frequency': count,
                        'Percentage': round(percentage, 1),
                        'Entity_Name': entity_name,
                        'State': entity_state,
                        'Entity_Type': entity_type
                    })
    
    # Save report
    if report_data:
        report_df = pd.DataFrame(report_data)
        report_filename = 'NPI_Frequency_Analysis_Report.csv'
        report_df.to_csv(report_filename, index=False)
        print(f"✅ Frequency analysis report saved: {report_filename}")

def identify_potential_issues(results):
    """Identify potential data quality issues based on frequency analysis"""
    print(f"\n🔍 POTENTIAL DATA QUALITY INSIGHTS")
    print("=" * 60)
    
    for analysis_name, data in results.items():
        if 'top_10' in data and len(data['top_10']) > 0:
            top_npi_count = data['top_10'].iloc[0]
            total_count = data['total']
            concentration = top_npi_count / total_count * 100
            
            print(f"{analysis_name.replace('_', ' ')}:")
            
            if concentration > 10:
                print(f"   ⚠️ High concentration: Top NPI represents {concentration:.1f}% of all entries")
            elif concentration > 5:
                print(f"   📊 Moderate concentration: Top NPI represents {concentration:.1f}% of all entries")
            else:
                print(f"   ✅ Good distribution: Top NPI represents {concentration:.1f}% of all entries")
            
            # Check for unusual patterns
            top_3_total = data['top_10'].head(3).sum()
            top_3_concentration = top_3_total / total_count * 100
            
            if top_3_concentration > 25:
                print(f"   ⚠️ Top 3 NPIs represent {top_3_concentration:.1f}% of data - may indicate skewed dataset")

def main():
    """Main execution function"""
    print("🚀 NPI FREQUENCY ANALYSIS")
    print("=" * 60)
    
    results = analyze_npi_frequency()
    
    if results:
        identify_potential_issues(results)
        
        print(f"\n🎯 ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"📊 Frequency analysis helps identify:")
        print(f"   • Most represented providers/practices")
        print(f"   • Data distribution patterns") 
        print(f"   • Potential data quality issues")
        print(f"📄 Detailed report saved for further analysis")

if __name__ == "__main__":
    main() 