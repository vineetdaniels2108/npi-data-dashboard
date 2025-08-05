#!/usr/bin/env python3
"""
Validate Fuzzy Practice Name Matches
1. Look up NPIs for fuzzy matched practice names using NPI API
2. Compare with NPI-2 values from enhanced alignment
"""

import pandas as pd
import requests
import time
from typing import Dict, List, Optional

def get_organization_npi_by_name(org_name: str) -> Optional[Dict]:
    """Look up organization NPI by practice/organization name via API"""
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

def validate_fuzzy_matches():
    """Validate fuzzy practice name matches by cross-referencing NPIs"""
    print("🔍 VALIDATING FUZZY PRACTICE NAME MATCHES")
    print("=" * 60)
    
    # Load the practice matching report
    print("📋 Loading practice matching report...")
    try:
        report_df = pd.read_csv('Practice_Name_Matching_Complete_Report.csv')
        print(f"✅ Loaded {len(report_df)} records from matching report")
    except Exception as e:
        print(f"❌ Error loading matching report: {e}")
        return
    
    # Load enhanced alignment file for NPI-2 comparison
    print("\n📊 Loading enhanced alignment file...")
    try:
        enhanced_df = pd.read_csv('Alignment_Simpl_Enhanced_with_CORRECTED_NPIs.csv')
        print(f"✅ Loaded {len(enhanced_df)} enhanced records")
    except Exception as e:
        print(f"❌ Error loading enhanced file: {e}")
        return
    
    # Filter for fuzzy matches only
    fuzzy_matches = report_df[report_df['Matching_Status'] == 'Matched (Fuzzy)'].copy()
    print(f"\n🔍 Found {len(fuzzy_matches)} fuzzy matches to validate")
    
    if len(fuzzy_matches) == 0:
        print("❌ No fuzzy matches found to validate")
        return
    
    # Get unique practice names that were matched (from complete dataset)
    unique_matched_practices = fuzzy_matches['Matched_Practice_Name'].dropna().unique()
    print(f"📋 {len(unique_matched_practices)} unique matched practice names to look up")
    
    # Look up NPIs for matched practice names
    print(f"\n🌐 Looking up NPIs for matched practice names via API...")
    practice_npi_lookup = {}
    
    for i, practice_name in enumerate(unique_matched_practices):
        print(f"\n   {i+1:2d}/{len(unique_matched_practices)}: {practice_name}")
        
        npi_info = get_organization_npi_by_name(practice_name)
        if npi_info:
            practice_npi_lookup[practice_name] = npi_info
            print(f"      ✅ Found NPI: {npi_info['npi']} - {npi_info['name']}")
        else:
            practice_npi_lookup[practice_name] = None
            print(f"      ❌ No NPI found")
        
        # Rate limiting
        time.sleep(1)
    
    # Now validate the matches
    print(f"\n🔍 VALIDATING FUZZY MATCHES")
    print("=" * 60)
    
    validation_results = []
    exact_npi_matches = 0
    no_api_npi = 0
    npi_mismatches = 0
    no_npi2_available = 0
    
    for index, row in fuzzy_matches.iterrows():
        original_practice = row['Original_Practice_Name']
        matched_practice = row['Matched_Practice_Name']
        npi2_from_api = str(row['NPI-2_From_API']).replace('.0', '') if pd.notna(row['NPI-2_From_API']) else ''
        
        # Get the API lookup result for the matched practice
        api_lookup = practice_npi_lookup.get(matched_practice)
        api_npi = api_lookup['npi'] if api_lookup else ''
        
        # Determine validation status
        if not npi2_from_api or npi2_from_api == 'nan' or npi2_from_api == '':
            validation_status = "No NPI-2 Available"
            no_npi2_available += 1
        elif not api_npi:
            validation_status = "No API NPI Found"
            no_api_npi += 1
        elif api_npi == npi2_from_api:
            validation_status = "✅ NPIs Match"
            exact_npi_matches += 1
        else:
            validation_status = "❌ NPIs Don't Match"
            npi_mismatches += 1
        
        validation_results.append({
            'Record_Index': row['Record_Index'],
            'Original_Practice': original_practice,
            'Matched_Practice': matched_practice,
            'Similarity_Score': row['Similarity_Score'],
            'NPI-2_From_API': npi2_from_api,
            'NPI_From_Matched_Practice': api_npi,
            'API_Practice_Name': api_lookup['name'] if api_lookup else '',
            'API_State': api_lookup['state'] if api_lookup else '',
            'Validation_Status': validation_status,
            'Provider_First_Name': row['Provider_First_Name'],
            'Provider_Last_Name': row['Provider_Last_Name']
        })
    
    # Create validation report
    validation_df = pd.DataFrame(validation_results)
    validation_filename = 'Fuzzy_Match_Validation_Report.csv'
    validation_df.to_csv(validation_filename, index=False)
    
    # Summary statistics
    total_fuzzy = len(fuzzy_matches)
    
    print(f"📊 VALIDATION SUMMARY:")
    print("-" * 50)
    print(f"📋 Total fuzzy matches validated: {total_fuzzy}")
    print(f"✅ Exact NPI matches: {exact_npi_matches} ({exact_npi_matches/total_fuzzy*100:.1f}%)")
    print(f"❌ NPI mismatches: {npi_mismatches} ({npi_mismatches/total_fuzzy*100:.1f}%)")
    print(f"🔍 No API NPI found: {no_api_npi} ({no_api_npi/total_fuzzy*100:.1f}%)")
    print(f"📋 No NPI-2 available: {no_npi2_available} ({no_npi2_available/total_fuzzy*100:.1f}%)")
    
    # Show sample validated matches
    print(f"\n🎯 SAMPLE VALIDATION RESULTS:")
    print("-" * 120)
    print(f"{'Original Practice':<25} | {'Matched Practice':<25} | {'NPI-2':<12} | {'API NPI':<12} | {'Status':<20}")
    print("-" * 120)
    
    for result in validation_results[:10]:
        orig = str(result['Original_Practice'])[:24]
        matched = str(result['Matched_Practice'])[:24]
        npi2 = str(result['NPI-2_From_API'])[:11]
        api_npi = str(result['NPI_From_Matched_Practice'])[:11]
        status = str(result['Validation_Status'])[:19]
        
        print(f"{orig:<25} | {matched:<25} | {npi2:<12} | {api_npi:<12} | {status:<20}")
    
    if len(validation_results) > 10:
        print(f"... and {len(validation_results) - 10} more validation results")
    
    # Show exact matches
    exact_matches = [r for r in validation_results if r['Validation_Status'] == "✅ NPIs Match"]
    if exact_matches:
        print(f"\n✅ CONFIRMED ACCURATE FUZZY MATCHES:")
        print("-" * 80)
        for match in exact_matches[:5]:
            print(f"   🎯 {match['Original_Practice']} → {match['Matched_Practice']}")
            print(f"      NPI: {match['NPI-2_From_API']} (Confirmed via API)")
        
        if len(exact_matches) > 5:
            print(f"   ... and {len(exact_matches) - 5} more confirmed matches")
    
    # Show mismatches
    mismatches = [r for r in validation_results if r['Validation_Status'] == "❌ NPIs Don't Match"]
    if mismatches:
        print(f"\n❌ POTENTIAL FALSE POSITIVES:")
        print("-" * 80)
        for mismatch in mismatches[:5]:
            print(f"   ⚠️ {mismatch['Original_Practice']} → {mismatch['Matched_Practice']}")
            print(f"      NPI-2: {mismatch['NPI-2_From_API']} vs API: {mismatch['NPI_From_Matched_Practice']}")
        
        if len(mismatches) > 5:
            print(f"   ... and {len(mismatches) - 5} more potential mismatches")
    
    print(f"\n📄 Detailed validation report saved: {validation_filename}")
    
    return {
        'total_fuzzy': total_fuzzy,
        'exact_matches': exact_npi_matches,
        'mismatches': npi_mismatches,
        'no_api_npi': no_api_npi,
        'no_npi2': no_npi2_available
    }

def analyze_validation_patterns():
    """Analyze patterns in the validation results"""
    print(f"\n📊 ANALYZING VALIDATION PATTERNS")
    print("=" * 60)
    
    try:
        validation_df = pd.read_csv('Fuzzy_Match_Validation_Report.csv')
        
        # Group by validation status
        status_counts = validation_df['Validation_Status'].value_counts()
        print(f"📋 Validation Status Distribution:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
        
        # Analyze similarity scores for different validation outcomes
        exact_matches = validation_df[validation_df['Validation_Status'] == "✅ NPIs Match"]
        mismatches = validation_df[validation_df['Validation_Status'] == "❌ NPIs Don't Match"]
        
        if len(exact_matches) > 0:
            avg_score_exact = exact_matches['Similarity_Score'].mean()
            print(f"\n📈 Average similarity score for confirmed matches: {avg_score_exact:.1f}")
        
        if len(mismatches) > 0:
            avg_score_mismatch = mismatches['Similarity_Score'].mean()
            print(f"📉 Average similarity score for mismatches: {avg_score_mismatch:.1f}")
        
    except Exception as e:
        print(f"⚠️ Error analyzing validation patterns: {e}")

def main():
    """Main execution function"""
    print("🚀 FUZZY MATCH VALIDATION ANALYSIS")
    print("=" * 60)
    
    results = validate_fuzzy_matches()
    
    if results:
        print(f"\n🎯 VALIDATION SUMMARY:")
        print("=" * 60)
        total = results['total_fuzzy']
        confirmed = results['exact_matches']
        accuracy = confirmed / total * 100 if total > 0 else 0
        
        print(f"🔍 Fuzzy Match Accuracy: {confirmed}/{total} ({accuracy:.1f}%)")
        print(f"✅ This shows how many fuzzy matches are actually correct!")
        
        analyze_validation_patterns()

if __name__ == "__main__":
    main() 