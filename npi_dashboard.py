import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page
st.set_page_config(
    page_title="NPI Data Dashboard - Complete Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .stDataFrame {
        border: 1px solid #e6e9ef;
        border-radius: 0.5rem;
    }
    .data-source {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the enhanced NPI data"""
    try:
        # Try to load the enhanced dataset first
        try:
            df = pd.read_csv("enhanced_npi_data.csv")
            st.success("✅ Loaded enhanced dataset with tab identification")
        except FileNotFoundError:
            # Fallback to original file and add tab column
            df = pd.read_csv("ELLKAY NPI List 2025.7.xlsx - Direct EHR 1A.csv")
            df['tab_source'] = "Direct EHR 1A"  # Add tab identifier
            st.info("📝 Added tab identification to original dataset")
        
        # Clean the data
        df = df.dropna(subset=['npi'])  # Remove rows without NPI
        df['npi'] = df['npi'].astype(str)  # Convert NPI to string for better handling
        df['state'] = df['state'].str.upper().str.strip()  # Standardize state format
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 NPI Data Dashboard - Complete Analysis</h1>', unsafe_allow_html=True)
    
    # Data source info
    st.markdown("""
    <div class="data-source">
        <h4>📋 Data Source Information</h4>
        <p><strong>Source:</strong> ELLKAY NPI List 2025.7.xlsx</p>
        <p><strong>Tab:</strong> Direct EHR 1A</p>
        <p><strong>Total Records:</strong> 160,292 entries</p>
        <p><strong>Unique NPIs:</strong> 144,142 (some NPIs appear in multiple medical groups)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading comprehensive NPI data..."):
        df = load_data()
    
    if df.empty:
        st.error("No data loaded. Please check your CSV file.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters & Search")
    
    # Tab source filter (if multiple tabs are added later)
    if 'tab_source' in df.columns:
        available_tabs = sorted(df['tab_source'].unique())
        selected_tabs = st.sidebar.multiselect(
            "Select Data Source Tabs:",
            options=available_tabs,
            default=available_tabs,
            help="Filter by data source tab"
        )
    else:
        selected_tabs = []
    
    # Search functionality
    search_term = st.sidebar.text_input(
        "🔍 Search NPIs, Medical Groups, or Addresses:",
        placeholder="Enter search term..."
    )
    
    # State filter
    all_states = sorted(df['state'].dropna().unique())
    selected_states = st.sidebar.multiselect(
        "🗺️ Select States:",
        options=all_states,
        default=all_states[:10] if len(all_states) > 10 else all_states,
        help="Select one or more states"
    )
    
    # Medical Group filter
    all_medical_groups = sorted(df['medical group'].dropna().unique())
    selected_medical_groups = st.sidebar.multiselect(
        "🏢 Select Medical Groups:",
        options=all_medical_groups[:100],  # Limit to first 100 for performance
        help="Select specific medical groups (showing top 100)"
    )
    
    # City filter (dynamic based on selected states)
    if selected_states:
        available_cities = sorted(df[df['state'].isin(selected_states)]['city'].dropna().unique())
        selected_cities = st.sidebar.multiselect(
            "🏙️ Select Cities:",
            options=available_cities[:50],  # Limit for performance
            help="Cities filtered by selected states (showing top 50)"
        )
    else:
        selected_cities = []
    
    # Apply filters
    filtered_df = df.copy()
    
    # Apply tab filter
    if selected_tabs and 'tab_source' in df.columns:
        filtered_df = filtered_df[filtered_df['tab_source'].isin(selected_tabs)]
    
    # Apply state filter
    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]
    
    # Apply medical group filter
    if selected_medical_groups:
        filtered_df = filtered_df[filtered_df['medical group'].isin(selected_medical_groups)]
    
    # Apply city filter
    if selected_cities:
        filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
    
    # Apply search filter
    if search_term:
        search_mask = (
            filtered_df['npi'].str.contains(search_term, case=False, na=False) |
            filtered_df['medical group'].str.contains(search_term, case=False, na=False) |
            filtered_df['address'].str.contains(search_term, case=False, na=False) |
            filtered_df['city'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Main dashboard metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📄 Total Records", f"{len(filtered_df):,}")
    
    with col2:
        st.metric("🏥 Unique NPIs", f"{filtered_df['npi'].nunique():,}")
    
    with col3:
        st.metric("🗺️ States", len(filtered_df['state'].unique()) if not filtered_df.empty else 0)
    
    with col4:
        st.metric("🏙️ Cities", len(filtered_df['city'].unique()) if not filtered_df.empty else 0)
    
    with col5:
        st.metric("🏢 Medical Groups", len(filtered_df['medical group'].unique()) if not filtered_df.empty else 0)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🗺️ By State", "🔍 Search Results", "📈 Analytics", "💾 Data Quality"])
    
    with tab1:
        st.subheader("📊 Data Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top states by NPI count
            if not filtered_df.empty:
                state_counts = filtered_df['state'].value_counts().head(15)
                fig_states = px.bar(
                    x=state_counts.values,
                    y=state_counts.index,
                    orientation='h',
                    title="Top 15 States by Record Count",
                    labels={'x': 'Number of Records', 'y': 'State'},
                    color=state_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_states.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_states, use_container_width=True)
        
        with col2:
            # Distribution by tab source
            if not filtered_df.empty and 'tab_source' in filtered_df.columns:
                tab_counts = filtered_df['tab_source'].value_counts()
                fig_tabs = px.pie(
                    values=tab_counts.values,
                    names=tab_counts.index,
                    title="Distribution by Data Source Tab"
                )
                fig_tabs.update_layout(height=500)
                st.plotly_chart(fig_tabs, use_container_width=True)
        
        # Duplicate NPI analysis
        st.subheader("🔄 Duplicate NPI Analysis")
        duplicate_npis = filtered_df[filtered_df['npi'].duplicated(keep=False)]
        if not duplicate_npis.empty:
            st.write(f"Found {len(duplicate_npis)} records with duplicate NPIs")
            duplicate_summary = duplicate_npis.groupby('npi').agg({
                'medical group': lambda x: list(x.unique()),
                'state': lambda x: list(x.unique()),
                'city': lambda x: list(x.unique())
            }).head(10)
            st.dataframe(duplicate_summary, use_container_width=True)
        else:
            st.info("No duplicate NPIs found in current filter")
    
    with tab2:
        st.subheader("🗺️ NPIs by State")
        
        if not filtered_df.empty:
            # Group by state
            state_summary = filtered_df.groupby('state').agg({
                'npi': ['count', 'nunique'],
                'medical group': 'nunique',
                'city': 'nunique',
                'tab_source': lambda x: ', '.join(x.unique()) if 'tab_source' in filtered_df.columns else 'N/A'
            }).round(2)
            
            # Flatten column names
            state_summary.columns = ['Total Records', 'Unique NPIs', 'Unique Medical Groups', 'Cities', 'Data Sources']
            state_summary = state_summary.sort_values('Total Records', ascending=False)
            
            # Display state summary table
            st.dataframe(
                state_summary,
                use_container_width=True,
                height=400
            )
            
            # Detailed view by selected state
            st.subheader("🔍 Detailed State View")
            selected_state_detail = st.selectbox(
                "Select a state for detailed view:",
                options=all_states
            )
            
            if selected_state_detail:
                state_data = df[df['state'] == selected_state_detail]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📄 Total Records", f"{len(state_data):,}")
                with col2:
                    st.metric("🏥 Unique NPIs", f"{state_data['npi'].nunique():,}")
                with col3:
                    st.metric("🏢 Medical Groups", state_data['medical group'].nunique())
                with col4:
                    st.metric("🏙️ Cities", state_data['city'].nunique())
                
                # Show data for selected state
                st.dataframe(
                    state_data,
                    use_container_width=True,
                    height=400
                )
                
                # Download button for state data
                csv = state_data.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {selected_state_detail} data as CSV",
                    data=csv,
                    file_name=f"npi_data_{selected_state_detail}.csv",
                    mime="text/csv"
                )
    
    with tab3:
        st.subheader("🔍 Search Results")
        
        if not filtered_df.empty:
            st.write(f"Showing **{len(filtered_df):,}** results")
            
            # Include tab_source in display if available
            display_columns = list(filtered_df.columns)
            
            # Display results
            st.dataframe(
                filtered_df[display_columns],
                use_container_width=True,
                height=500
            )
            
            # Download filtered data
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download filtered data as CSV",
                data=csv,
                file_name="filtered_npi_data.csv",
                mime="text/csv"
            )
        else:
            st.info("No results found. Try adjusting your search criteria.")
    
    with tab4:
        st.subheader("📈 Analytics Dashboard")
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Medical groups distribution
                mg_counts = filtered_df['medical group'].value_counts().head(20)
                fig_mg = px.bar(
                    x=mg_counts.values,
                    y=mg_counts.index,
                    orientation='h',
                    title="Top 20 Medical Groups by Record Count",
                    labels={'x': 'Number of Records', 'y': 'Medical Group'},
                    color=mg_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig_mg.update_layout(height=600, showlegend=False)
                st.plotly_chart(fig_mg, use_container_width=True)
            
            with col2:
                # ZIP code distribution
                zip_counts = filtered_df['zip'].value_counts().head(20)
                fig_zip = px.bar(
                    x=zip_counts.values,
                    y=zip_counts.index.astype(str),
                    orientation='h',
                    title="Top 20 ZIP Codes by Record Count",
                    labels={'x': 'Number of Records', 'y': 'ZIP Code'},
                    color=zip_counts.values,
                    color_continuous_scale='Plasma'
                )
                fig_zip.update_layout(height=600, showlegend=False)
                st.plotly_chart(fig_zip, use_container_width=True)
            
            # Geographic heat map
            st.subheader("🗺️ Geographic Distribution")
            state_summary_for_map = filtered_df.groupby('state').size().reset_index(name='count')
            fig_map = px.choropleth(
                state_summary_for_map,
                locations='state',
                color='count',
                locationmode='USA-states',
                scope='usa',
                title='NPI Distribution by State',
                color_continuous_scale='Blues'
            )
            fig_map.update_layout(height=500)
            st.plotly_chart(fig_map, use_container_width=True)
    
    with tab5:
        st.subheader("💾 Data Quality Analysis")
        
        # Data completeness analysis
        st.write("### 📊 Data Completeness by Column")
        completeness_data = []
        for col in df.columns:
            non_null = df[col].notna().sum()
            total = len(df)
            completeness = (non_null / total) * 100
            completeness_data.append({
                'Column': col,
                'Non-Null Records': f"{non_null:,}",
                'Total Records': f"{total:,}",
                'Completeness %': f"{completeness:.2f}%"
            })
        
        completeness_df = pd.DataFrame(completeness_data)
        st.dataframe(completeness_df, use_container_width=True)
        
        # Tab source summary
        if 'tab_source' in df.columns:
            st.write("### 🏷️ Data Source Tab Summary")
            tab_summary = df.groupby('tab_source').agg({
                'npi': ['count', 'nunique'],
                'medical group': 'nunique',
                'state': 'nunique'
            })
            tab_summary.columns = ['Total Records', 'Unique NPIs', 'Medical Groups', 'States']
            st.dataframe(tab_summary, use_container_width=True)
        
        # Summary statistics
        st.write("### 📈 Overall Dataset Statistics")
        summary_stats = pd.DataFrame({
            'Metric': [
                'Total Records', 
                'Unique NPIs', 
                'Unique States', 
                'Unique Cities', 
                'Unique Medical Groups',
                'Records with Address 2',
                'Duplicate NPIs'
            ],
            'Count': [
                f"{len(df):,}",
                f"{df['npi'].nunique():,}",
                f"{df['state'].nunique()}",
                f"{df['city'].nunique():,}",
                f"{df['medical group'].nunique():,}",
                f"{df['address 2'].notna().sum():,}",
                f"{df['npi'].duplicated().sum():,}"
            ]
        })
        st.dataframe(summary_stats, use_container_width=True)

if __name__ == "__main__":
    main() 