#!/usr/bin/env python3
"""
Match Practice Names from Enhanced Alignment against Complete Dataset
Using both exact and fuzzy matching - FIXED VERSION
"""

import pandas as pd
from fuzzywuzzy import fuzz, process
import re

def clean_practice_name(name):
    """Clean and standardize practice names for better matching"""
    if pd.isna(name) or str(name).strip() == '' or str(name).lower() in ['nan', 'n/a', 'na']:
        return ""
    
    name = str(name).upper().strip()
    
    # Remove common suffixes and standardize
    replacements = {
        r'\bINC\.?\b': '',
        r'\bLLC\.?\b': '',
        r'\bLLP\.?\b': '',
        r'\bCORP\.?\b': '',
        r'\bCORPORATION\b': '',
        r'\bLIMITED\b': '',
        r'\bPROFESSIONAL\b': 'PROF',
        r'\bASSOCIATES?\b': 'ASSOC',
        r'\bASSOCIATION\b': 'ASSOC',
        r'\bMEDICAL\b': 'MED',
        r'\bGROUP\b': 'GRP',
        r'\bCLINIC\b': 'CLINIC',
        r'\bHOSPITAL\b': 'HOSP',
        r'\bHEALTH\b': 'HLTH',
        r'\bSYSTEM\b': 'SYS',
        r'\bCENTER\b': 'CTR',
        r'\bSERVICES?\b': 'SVCS',
        r'\s+': ' ',  # Multiple spaces to single
        r'[^\w\s]': ' '  # Remove special characters
    }
    
    for pattern, replacement in replacements.items():
        name = re.sub(pattern, replacement, name)
    
    return name.strip()

def find_practice_columns(df):
    """Identify columns that likely contain practice/organization names"""
    practice_columns = []
    
    for col in df.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in [
            'practice', 'organization', 'medical group', 'company', 'facility',
            'clinic', 'hospital', 'group', 'affiliation', 'health', 'system'
        ]):
            practice_columns.append(col)
    
    return practice_columns

def match_practice_names():
    """Match practice names using exact and fuzzy matching"""
    print("🏢 MATCHING PRACTICE NAMES - EXACT & FUZZY")
    print("=" * 60)
    
    # Load enhanced alignment file
    print("📋 Loading enhanced alignment file...")
    try:
        enhanced_df = pd.read_csv('Alignment_Simpl_Enhanced_with_CORRECTED_NPIs.csv')
        print(f"✅ Loaded {len(enhanced_df)} enhanced records")
    except Exception as e:
        print(f"❌ Error loading enhanced file: {e}")
        return
    
    # Load complete dataset
    print("\n📊 Loading complete dataset...")
    try:
        complete_df = pd.read_csv('complete_npi_dataset_all_tabs.csv', low_memory=False)
        print(f"✅ Loaded {len(complete_df)} complete dataset records")
    except Exception as e:
        print(f"❌ Error loading complete dataset: {e}")
        return
    
    # Get unique practice names from enhanced file
    practice_names = enhanced_df['Practice Name'].dropna().unique()
    practice_names = [name for name in practice_names if str(name).strip() != '' and str(name).lower() != 'nan']
    print(f"\n📋 Found {len(practice_names)} unique practice names to match")
    
    # Find practice-related columns in complete dataset
    practice_columns = find_practice_columns(complete_df)
    print(f"\n🔍 Practice-related columns in complete dataset:")
    for i, col in enumerate(practice_columns, 1):
        print(f"   {i:2d}. {col}")
    
    if not practice_columns:
        print("❌ No practice-related columns found in complete dataset")
        return
    
    # Perform exact matching first
    print(f"\n🎯 PHASE 1: EXACT MATCHING")
    print("-" * 40)
    
    exact_matches = []
    unmatched_practices = []
    
    for practice in practice_names:
        practice_clean = clean_practice_name(practice)
        if not practice_clean:
            continue
            
        found_match = False
        
        for col in practice_columns:
            if col not in complete_df.columns:
                continue
            
            try:
                # Create a copy of the column and clean it
                col_data = complete_df[col].dropna().astype(str)
                cleaned_col_data = col_data.apply(clean_practice_name)
                
                # Find matches
                match_indices = cleaned_col_data[cleaned_col_data == practice_clean].index
                
                if len(match_indices) > 0:
                    # Get the first match
                    match_idx = match_indices[0]
                    match_record = complete_df.loc[match_idx]
                    npi_val = match_record.get('NPI', match_record.get('npi', 'N/A'))
                    
                    exact_matches.append({
                        'Original_Practice': practice,
                        'Matched_Practice': match_record[col],
                        'Match_Type': 'Exact',
                        'Similarity_Score': 100,
                        'Matched_Column': col,
                        'NPI': npi_val,
                        'Provider_Name': match_record.get('Last Name', match_record.get('First Name', 'N/A')),
                        'City': match_record.get('City', match_record.get('city', 'N/A')),
                        'State': match_record.get('State', match_record.get('state', 'N/A')),
                        'Tab_Source': match_record.get('tab_source', 'N/A')
                    })
                    found_match = True
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Error processing column {col}: {e}")
                continue
        
        if not found_match:
            unmatched_practices.append(practice)
    
    print(f"✅ Exact matches found: {len(exact_matches)}")
    print(f"❌ Unmatched practices: {len(unmatched_practices)}")
    
    # Perform fuzzy matching on unmatched practices
    print(f"\n🔍 PHASE 2: FUZZY MATCHING")
    print("-" * 40)
    
    # Create a comprehensive list of all practice names from complete dataset
    all_practice_names = []
    practice_name_to_record = {}  # Map practice name to record info
    
    for col in practice_columns:
        if col in complete_df.columns:
            try:
                col_data = complete_df[col].dropna().astype(str)
                for idx, name in col_data.items():
                    if name and str(name).strip() != '':
                        all_practice_names.append(name)
                        practice_name_to_record[name] = {
                            'record': complete_df.loc[idx],
                            'column': col
                        }
            except Exception as e:
                print(f"   ⚠️ Error processing column {col} for fuzzy matching: {e}")
                continue
    
    # Remove duplicates
    unique_practice_names = list(set(all_practice_names))
    print(f"📊 Total unique practice names in dataset: {len(unique_practice_names)}")
    
    fuzzy_matches = []
    still_unmatched = []
    
    for practice in unmatched_practices:
        practice_clean = clean_practice_name(practice)
        if not practice_clean:
            still_unmatched.append(practice)
            continue
        
        try:
            # Try fuzzy matching with cleaned names
            cleaned_practice_names = [clean_practice_name(name) for name in unique_practice_names]
            cleaned_practice_names = [name for name in cleaned_practice_names if name]
            
            # Get best matches using both original and cleaned names
            best_matches_cleaned = process.extract(
                practice_clean, 
                cleaned_practice_names, 
                scorer=fuzz.token_sort_ratio,
                limit=5
            )
            
            best_matches_original = process.extract(
                practice, 
                unique_practice_names, 
                scorer=fuzz.token_sort_ratio,
                limit=5
            )
            
            # Combine and sort by score
            all_matches = best_matches_cleaned + best_matches_original
            all_matches = sorted(all_matches, key=lambda x: x[1], reverse=True)
            
            # Take best match if score >= 70
            if all_matches and all_matches[0][1] >= 70:
                matched_name = all_matches[0][0]
                similarity_score = all_matches[0][1]
                
                # Find the original record
                match_record = None
                matched_column = 'Unknown'
                
                # Try to find the exact match in our mapping
                if matched_name in practice_name_to_record:
                    match_info = practice_name_to_record[matched_name]
                    match_record = match_info['record']
                    matched_column = match_info['column']
                else:
                    # Try to find by cleaned name
                    for orig_name, info in practice_name_to_record.items():
                        if clean_practice_name(orig_name) == matched_name:
                            match_record = info['record']
                            matched_column = info['column']
                            matched_name = orig_name  # Use original name
                            break
                
                if match_record is not None:
                    npi_val = match_record.get('NPI', match_record.get('npi', 'N/A'))
                    
                    fuzzy_matches.append({
                        'Original_Practice': practice,
                        'Matched_Practice': matched_name,
                        'Match_Type': 'Fuzzy',
                        'Similarity_Score': similarity_score,
                        'Matched_Column': matched_column,
                        'NPI': npi_val,
                        'Provider_Name': match_record.get('Last Name', match_record.get('First Name', 'N/A')),
                        'City': match_record.get('City', match_record.get('city', 'N/A')),
                        'State': match_record.get('State', match_record.get('state', 'N/A')),
                        'Tab_Source': match_record.get('tab_source', 'N/A')
                    })
                else:
                    still_unmatched.append(practice)
            else:
                still_unmatched.append(practice)
                
        except Exception as e:
            print(f"   ⚠️ Error in fuzzy matching for {practice}: {e}")
            still_unmatched.append(practice)
    
    print(f"✅ Fuzzy matches found: {len(fuzzy_matches)}")
    print(f"❌ Still unmatched: {len(still_unmatched)}")
    
    # Combine results and create comprehensive report
    all_matches = exact_matches + fuzzy_matches
    
    print(f"\n📊 PRACTICE NAME MATCHING SUMMARY")
    print("=" * 60)
    print(f"📋 Total practices to match: {len(practice_names)}")
    print(f"✅ Exact matches: {len(exact_matches)} ({len(exact_matches)/len(practice_names)*100:.1f}%)")
    print(f"🔍 Fuzzy matches: {len(fuzzy_matches)} ({len(fuzzy_matches)/len(practice_names)*100:.1f}%)")
    print(f"✅ Total matches: {len(all_matches)} ({len(all_matches)/len(practice_names)*100:.1f}%)")
    print(f"❌ Unmatched: {len(still_unmatched)} ({len(still_unmatched)/len(practice_names)*100:.1f}%)")
    
    # Show sample matches
    if all_matches:
        print(f"\n🎯 SAMPLE MATCHES:")
        print("-" * 100)
        print(f"{'Original Practice':<30} | {'Matched Practice':<30} | {'Type':<5} | {'Score':<5} | {'NPI':<12}")
        print("-" * 100)
        
        for match in all_matches[:10]:
            orig = str(match['Original_Practice'])[:29]
            matched = str(match['Matched_Practice'])[:29]
            match_type = match['Match_Type']
            score = match['Similarity_Score']
            npi = str(match['NPI'])[:11]
            
            print(f"{orig:<30} | {matched:<30} | {match_type:<5} | {score:<5} | {npi:<12}")
        
        if len(all_matches) > 10:
            print(f"... and {len(all_matches) - 10} more matches")
    
    # Show sample unmatched
    if still_unmatched:
        print(f"\n❌ SAMPLE UNMATCHED PRACTICES:")
        print("-" * 50)
        for i, practice in enumerate(still_unmatched[:10]):
            print(f"   {i+1:2d}. {practice}")
        if len(still_unmatched) > 10:
            print(f"   ... and {len(still_unmatched) - 10} more")
    
    # Create comprehensive CSV report
    create_practice_matching_report(enhanced_df, all_matches, still_unmatched)
    
    return {
        'exact_matches': len(exact_matches),
        'fuzzy_matches': len(fuzzy_matches),
        'total_matches': len(all_matches),
        'unmatched': len(still_unmatched),
        'total_practices': len(practice_names)
    }

def create_practice_matching_report(enhanced_df, all_matches, still_unmatched):
    """Create comprehensive practice matching report"""
    print(f"\n📄 Creating comprehensive practice matching report...")
    
    # Create mapping dictionary for quick lookup
    match_dict = {}
    for match in all_matches:
        match_dict[match['Original_Practice']] = match
    
    # Prepare report data
    report_data = []
    
    for index, row in enhanced_df.iterrows():
        practice_name = row.get('Practice Name', '')
        
        if pd.notna(practice_name) and str(practice_name).strip() != '' and str(practice_name).lower() != 'nan':
            if practice_name in match_dict:
                match_info = match_dict[practice_name]
                status = f"Matched ({match_info['Match_Type']})"
                matched_practice = match_info['Matched_Practice']
                similarity_score = match_info['Similarity_Score']
                matched_npi = match_info['NPI']
                matched_column = match_info['Matched_Column']
                provider_name = match_info['Provider_Name']
                city = match_info['City']
                state = match_info['State']
            elif practice_name in still_unmatched:
                status = "Not Matched"
                matched_practice = ""
                similarity_score = 0
                matched_npi = ""
                matched_column = ""
                provider_name = ""
                city = ""
                state = ""
            else:
                status = "N/A"
                matched_practice = ""
                similarity_score = 0
                matched_npi = ""
                matched_column = ""
                provider_name = ""
                city = ""
                state = ""
        else:
            status = "No Practice Name"
            matched_practice = ""
            similarity_score = 0
            matched_npi = ""
            matched_column = ""
            provider_name = ""
            city = ""
            state = ""
        
        report_data.append({
            'Record_Index': index + 1,
            'Provider_First_Name': row.get('PROVIDER_FIRST_NAME', ''),
            'Provider_Last_Name': row.get('PROVIDER_LAST_NAME', ''),
            'Original_Practice_Name': practice_name,
            'Matching_Status': status,
            'Matched_Practice_Name': matched_practice,
            'Similarity_Score': similarity_score,
            'Matched_NPI': matched_npi,
            'Matched_Column': matched_column,
            'Associated_Provider': provider_name,
            'City': city,
            'State': state,
            'NPI-1_From_API': row.get('NPI-1', ''),
            'NPI-2_From_API': row.get('NPI-2', '')
        })
    
    # Create DataFrame and save
    report_df = pd.DataFrame(report_data)
    report_filename = 'Practice_Name_Matching_Complete_Report.csv'
    report_df.to_csv(report_filename, index=False)
    
    print(f"✅ Complete practice matching report saved: {report_filename}")
    print(f"📋 Report contains {len(report_df)} records with detailed matching analysis")

def main():
    """Main execution function"""
    print("🚀 PRACTICE NAME MATCHING ANALYSIS")
    print("=" * 60)
    
    results = match_practice_names()
    
    if results:
        total = results['total_practices']
        matched = results['total_matches']
        exact = results['exact_matches']
        fuzzy = results['fuzzy_matches']
        
        print(f"\n🎯 FINAL RESULTS:")
        print("=" * 60)
        print(f"📊 Overall Success Rate: {matched}/{total} ({matched/total*100:.1f}%)")
        print(f"🎯 Exact Matches: {exact} ({exact/total*100:.1f}%)")
        print(f"🔍 Fuzzy Matches: {fuzzy} ({fuzzy/total*100:.1f}%)")
        print(f"📄 Comprehensive report created with detailed results")

if __name__ == "__main__":
    main() 