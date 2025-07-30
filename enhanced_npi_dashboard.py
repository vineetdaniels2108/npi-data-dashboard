import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page and Style Configuration ---
st.set_page_config(
    page_title="NPI Data Dashboard - Complete Multi-Tab Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 1rem; }
    .sub-header { text-align: center; color: #555; margin-bottom: 2rem; }
    .search-tip { background-color: #fff4e6; padding: 0.5rem; border-radius: 0.3rem; border-left: 3px solid #ff8c00; margin-bottom: 1rem; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- State Name Mapping ---
STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida',
    'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana',
    'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
    'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
    'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota',
    'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# --- Data Loading and Processing ---
@st.cache_data
def load_and_process_data():
    """Loads, cleans, and standardizes data from the complete multi-tab CSV."""
    try:
        # Try to load the processed data first
        import os
        if os.path.exists("processed_npi_data.csv"):
            df = pd.read_csv("processed_npi_data.csv", low_memory=False)
        else:
            df = pd.read_csv("complete_npi_dataset_all_tabs.csv", low_memory=False, dtype=str)

        # First, handle duplicate columns by making them unique
        # Get all column names
        cols = df.columns.tolist()
        new_cols = []
        seen = {}
        
        # Make column names unique by appending _1, _2, etc. to duplicates
        for col in cols:
            if col.lower() in seen:
                seen[col.lower()] += 1
                new_cols.append(f"{col}_{seen[col.lower()]}")
            else:
                seen[col.lower()] = 0
                new_cols.append(col)
        
        df.columns = new_cols
        
        # Now standardize column names
        column_mapping = {
            'NPI': 'npi', 'npi': 'npi', 'NPI_1': 'npi_alt',
            'CompanyName': 'organization_name', 'medical group': 'organization_name',
            'Company Name': 'organization_name_alt', 
            'Last Name': 'last_name', 'First Name': 'first_name',
            'Middle Name': 'middle_name', 
            'City': 'city_alt', 'city': 'city', 'City_1': 'city_alt2',
            'State': 'state_alt', 'state': 'state', 'State_1': 'state_alt2',
            'Address': 'address_alt', 'address': 'address', 'Address_1': 'address_alt2',
            'Addressline2': 'address_2_alt', 'address 2': 'address_2',
            'ZipCode': 'zip_alt', 'zip': 'zip',
            'Primary Specialty': 'primary_specialty', 
            'Role': 'role', 'Phone': 'phone',
            'Credential': 'credential', 
            'Primary Hospital Affiliation': 'primary_hospital',
            'Secondary Hospital Affiliation': 'secondary_hospital',
            'Claim Based Specialty Primary': 'claim_specialty_primary',
        }
        df = df.rename(columns=column_mapping)
        
        # Merge duplicate columns (prefer non-null values from alternative columns)
        if 'npi_alt' in df.columns and 'npi' in df.columns:
            df['npi'] = df['npi'].fillna(df['npi_alt'])
            df = df.drop(columns=['npi_alt'])
        if 'organization_name_alt' in df.columns and 'organization_name' in df.columns:
            df['organization_name'] = df['organization_name'].fillna(df['organization_name_alt'])
            df = df.drop(columns=['organization_name_alt'])
        if 'city_alt' in df.columns and 'city' in df.columns:
            df['city'] = df['city'].fillna(df['city_alt'])
            df = df.drop(columns=['city_alt', 'city_alt2'], errors='ignore')
        if 'state_alt' in df.columns and 'state' in df.columns:
            df['state'] = df['state'].fillna(df['state_alt'])
            df = df.drop(columns=['state_alt', 'state_alt2'], errors='ignore')
        if 'address_alt' in df.columns and 'address' in df.columns:
            df['address'] = df['address'].fillna(df['address_alt'])
            df = df.drop(columns=['address_alt', 'address_alt2'], errors='ignore')
        if 'zip_alt' in df.columns and 'zip' in df.columns:
            df['zip'] = df['zip'].fillna(df['zip_alt'])
            df = df.drop(columns=['zip_alt'], errors='ignore')

        # Clean up data
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        if 'npi' in df.columns:
            df['npi'] = pd.to_numeric(df['npi'], errors='coerce').fillna(0).astype(int).astype(str)
            df = df[df['npi'].str.len() >= 10]
        
        # Remove any remaining duplicate columns by keeping only the first occurrence
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Consolidate organization name (now that duplicates are resolved)
        org_cols = [col for col in ['organization_name', 'medical group', 'CompanyName', 'Company Name'] if col in df.columns]
        if org_cols and len(org_cols) > 1:
            # Only consolidate if we have multiple org columns
            df['organization_name'] = df[org_cols].bfill(axis=1).iloc[:, 0]

        # Add state display name
        if 'state' in df.columns:
            df['state'] = df['state'].str.upper().str.strip()
            df['state_full'] = df['state'].map(STATE_NAMES).fillna(df['state'])
            df['state_display'] = df['state'] + ' - ' + df['state_full']

        # Build comprehensive search field
        search_cols = [col for col in ['organization_name', 'last_name', 'first_name', 'primary_specialty', 'role', 'primary_hospital', 'tab_source'] if col in df.columns]
        if search_cols:
            # Convert each column to string first, then join
            df['searchable_text'] = df[search_cols].fillna('').astype(str).apply(lambda x: ' '.join(x), axis=1).str.lower()
        else:
            df['searchable_text'] = ''
        
        return df

    except FileNotFoundError:
        st.error("`complete_npi_dataset_all_tabs.csv` not found. Please ensure the file is in the correct directory.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return pd.DataFrame()

# --- Helper Functions ---
def perform_lazy_search(df, search_term):
    if not search_term or 'searchable_text' not in df.columns:
        return df
    return df[df['searchable_text'].str.contains(search_term.lower().strip(), na=False)]

def get_all_available_columns(df):
    preferred = ['npi', 'organization_name', 'last_name', 'first_name', 'primary_specialty', 'role', 'primary_hospital', 'secondary_hospital', 'claim_specialty_primary', 'city', 'state_display', 'zip', 'tab_source']
    return [p for p in preferred if p in df.columns] + [c for c in df.columns if c not in preferred and c != 'searchable_text']

def build_agg_dict(df):
    """Dynamically builds an aggregation dictionary based on available columns."""
    agg_dict = {}
    if 'npi' in df.columns:
        agg_dict['npi'] = ['count', 'nunique']
    if 'organization_name' in df.columns:
        agg_dict['organization_name'] = 'nunique'
    if 'primary_specialty' in df.columns:
        agg_dict['primary_specialty'] = 'nunique'
    if 'primary_hospital' in df.columns:
        agg_dict['primary_hospital'] = 'nunique'
    if 'state' in df.columns:
        agg_dict['state'] = 'nunique'
    return agg_dict

# --- Main Application ---
def main():
    st.markdown('<h1 class="main-header">NPI Data Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Complete Multi-Tab Analysis of All Healthcare Systems</p>', unsafe_allow_html=True)
    
    # Add cache clear button in development
    if st.sidebar.button("🔄 Clear Cache & Reload Data"):
        st.cache_data.clear()
        st.rerun()
    
    df = load_and_process_data()
    if df.empty:
        return

    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filters & Search")
    
    # NPI search
    st.sidebar.markdown('<div class="search-tip">🆔 <strong>NPI Search:</strong> Search by specific NPI number.</div>', unsafe_allow_html=True)
    npi_search = st.sidebar.text_input("Search by NPI:", placeholder="e.g., 1234567890", max_chars=10)
    if npi_search:
        # Clean and validate NPI input
        clean_npi = npi_search.strip()
        if clean_npi.isdigit() and len(clean_npi) == 10:
            if 'npi' in df.columns:
                df = df[df['npi'].astype(str).str.strip() == clean_npi]
                if df.empty:
                    st.sidebar.warning(f"No records found for NPI: {clean_npi}")
            else:
                st.sidebar.error("NPI column not available in data")
        elif clean_npi:
            st.sidebar.error("Please enter a valid 10-digit NPI number")
    
    # Lazy search
    st.sidebar.markdown('<div class="search-tip">💡 <strong>General Search:</strong> Find any provider, specialty, or system.</div>', unsafe_allow_html=True)
    search_term = st.sidebar.text_input("Search Anything:", placeholder="e.g., Beth, Cardiology, Mayo...")
    if search_term:
        df = perform_lazy_search(df, search_term)

    # Filters with "Select All"
    all_tabs = sorted(df['tab_source'].dropna().unique())
    select_all_tabs = st.sidebar.checkbox("Select All Systems/Tabs", value=True)
    selected_tabs = all_tabs if select_all_tabs else st.sidebar.multiselect("Select Systems/Tabs:", all_tabs, default=all_tabs[:min(10, len(all_tabs))])

    all_states = sorted(df['state_display'].dropna().unique())
    select_all_states = st.sidebar.checkbox("Select All States", value=True)
    selected_states_display = all_states if select_all_states else st.sidebar.multiselect("Select States:", all_states, default=all_states[:min(10, len(all_states))])
    selected_state_codes = [s.split(' - ')[0] for s in selected_states_display]

    # Dynamic filters
    optional_filters = ['primary_specialty', 'role']
    for col in optional_filters:
        if col in df.columns:
            options = sorted(df[col].dropna().unique())
            st.sidebar.multiselect(f"Filter by {col.replace('_', ' ').title()}:", options)

    # Apply filters
    filtered_df = df[
        df['tab_source'].isin(selected_tabs) &
        df['state_display'].isin(selected_states_display)
    ]

    # --- Main Content ---
    st.subheader("Filtered Results Overview")
    metric_cols = st.columns(5)
    metric_cols[0].metric("Total Records", f"{len(filtered_df):,}")
    if 'npi' in filtered_df: metric_cols[1].metric("Unique NPIs", f"{filtered_df['npi'].nunique():,}")
    if 'tab_source' in filtered_df: metric_cols[2].metric("Systems", f"{filtered_df['tab_source'].nunique():,}")
    if 'state' in filtered_df: metric_cols[3].metric("States", f"{filtered_df['state'].nunique():,}")
    if 'primary_specialty' in filtered_df: metric_cols[4].metric("Specialties", f"{filtered_df['primary_specialty'].nunique():,}")

    # --- Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics Dashboard", "🔍 Search Results", "🏥 By Healthcare System", "💾 Data Quality"])

    with tab1:
        st.header("Overall Analytics")
        # Charts for top systems and states
        if not filtered_df.empty:
            c1, c2 = st.columns(2)
            if 'tab_source' in filtered_df and not filtered_df['tab_source'].dropna().empty:
                try:
                    top_tabs = filtered_df['tab_source'].value_counts().nlargest(15)
                    if len(top_tabs) > 0:
                        tab_data = pd.DataFrame({'Systems': top_tabs.index, 'Count': top_tabs.values})
                        c1.plotly_chart(px.bar(tab_data, y='Systems', x='Count', orientation='h', title='Top 15 Systems by Record Count'), use_container_width=True)
                except Exception as e:
                    c1.error(f"Error creating systems chart: {str(e)}")
            
            if 'state_display' in filtered_df and not filtered_df['state_display'].dropna().empty:
                try:
                    top_states = filtered_df['state_display'].value_counts().nlargest(15)
                    if len(top_states) > 0:
                        state_data = pd.DataFrame({'State': top_states.index, 'Count': top_states.values})
                        c2.plotly_chart(px.bar(state_data, y='State', x='Count', orientation='h', title='Top 15 States by Record Count'), use_container_width=True)
                except Exception as e:
                    c2.error(f"Error creating states chart: {str(e)}")
            
            if 'primary_specialty' in filtered_df and not filtered_df['primary_specialty'].dropna().empty:
                st.header("Top Medical Specialties")
                try:
                    top_specialties = filtered_df['primary_specialty'].value_counts().nlargest(20)
                    if len(top_specialties) > 0:
                        specialty_data = pd.DataFrame({'Specialty': top_specialties.index, 'Count': top_specialties.values})
                        st.plotly_chart(px.bar(specialty_data, y='Specialty', x='Count', orientation='h', title='Top 20 Specialties'), use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating specialties chart: {str(e)}")
    
    with tab2:
        st.header("Search Results")
        if not filtered_df.empty:
            st.info(f"Showing {len(filtered_df):,} records based on your filters.")
            all_cols = get_all_available_columns(filtered_df)
            default_cols = [c for c in ['npi', 'last_name', 'first_name', 'primary_specialty', 'organization_name', 'city', 'state_display', 'tab_source'] if c in all_cols]
            selected_cols = st.multiselect("Select columns to display:", all_cols, default=default_cols)
            st.dataframe(filtered_df[selected_cols], use_container_width=True, height=500)
            st.download_button("📥 Download Results as CSV", filtered_df[selected_cols].to_csv(index=False), "filtered_npi_data.csv", "text/csv")
        else:
            st.warning("No results match your current filters.")

    with tab3:
        st.header("Analysis by Healthcare System")
        if not filtered_df.empty and 'tab_source' in filtered_df:
            agg_dict = build_agg_dict(filtered_df)
            if agg_dict:
                system_summary = filtered_df.groupby('tab_source').agg(agg_dict)
                st.dataframe(system_summary, use_container_width=True)

    with tab4:
        st.header("Data Quality and Completeness")
        completeness_data = []
        for col in df.columns:
            if col != 'searchable_text':
                non_nulls = df[col].notna().sum()
                total = len(df)
                completeness = (non_nulls / total) * 100
                completeness_data.append({'Column': col, 'Non-Null Records': f"{non_nulls:,}", 'Completeness %': f"{completeness:.2f}%"})
        st.dataframe(pd.DataFrame(completeness_data), use_container_width=True)

if __name__ == "__main__":
    main() 