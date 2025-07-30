# NPI Data Dashboard 🏥

A comprehensive Streamlit dashboard for exploring and analyzing National Provider Identifier (NPI) data with complete multi-tab analysis and enhanced search capabilities.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/[your-username]/npi-matching.git
cd npi-matching

# Install dependencies
pip install -r requirements.txt

# Add your data files (see Data Setup section)

# Launch the dashboard
python3 launch_dashboard.py
```

## 📊 Dataset Overview
- **199,484 total records** processed from **31 healthcare systems/tabs**
- **179,410 unique NPIs** with comprehensive validation
- **56 states** covered (including DC and territories)
- **Multiple data formats** seamlessly integrated and standardized
- **Advanced provider information** including specialties, roles, and affiliations

## ✨ Key Features

### 🆔 NPI Search
- **Direct NPI lookup** with 10-digit validation
- **Real-time feedback** for invalid NPIs
- **Instant results** with comprehensive provider details

### 🔍 Advanced Search & Filtering
- **General text search** across all fields
- **State filtering** with full state names
- **System/Tab filtering** by healthcare organization
- **Specialty filtering** by medical specialties
- **Real-time results** with instant updates

## 📁 Data Setup

1. **Add your Excel file**: Place your multi-tab Excel file as `New File.xlsx` in the project directory
2. **Process the data**: Run `python3 process_new_file_data.py` to clean and standardize all data
3. **Launch dashboard**: Use `python3 launch_dashboard.py` to start the application

The data processor handles:
- **Multiple sheet formats** (provider records, organization records)
- **Column standardization** across different data sources  
- **Data validation** with NPI format checking
- **Unified output** in `processed_npi_data.csv`

## 🛠️ Technical Features

### 📊 Enhanced Dashboard Views

#### 1. Overview Tab
- Key metrics display (Total Records, Unique NPIs, States, Cities, Medical Groups)
- Top 15 states by record count (interactive bar chart)
- Distribution by data source tab (pie chart)
- **Duplicate NPI Analysis**: Shows NPIs that appear in multiple medical groups

#### 2. By State Tab
- Enhanced summary table with Total Records, Unique NPIs, Medical Groups, Cities, and Data Sources
- Detailed state view with comprehensive metrics
- Full data table for selected state with all columns including tab_source
- Download CSV for individual state data

#### 3. Search Results Tab
- Display filtered results with all columns including tab identification
- Enhanced result count display with formatting
- Download filtered data as CSV with tab_source column

#### 4. Analytics Tab
- Top 20 medical groups by record count (enhanced visualization)
- Top 20 ZIP codes by record count (color-coded charts)
- **Geographic Heat Map**: Interactive US map showing NPI distribution by state

#### 5. Data Quality Tab (NEW)
- **Data Completeness Analysis**: Shows completeness percentage for each column
- **Tab Source Summary**: Statistics grouped by data source tab
- **Overall Dataset Statistics**: Comprehensive metrics including duplicate analysis

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your CSV file is in the same directory as the dashboard script.

## Usage

### Option 1: Use the Launcher Script (Recommended)
```bash
python3 launch_dashboard.py
```

### Option 2: Manual Launch
Try these commands in order until one works:
```bash
python3 -m streamlit run npi_dashboard.py
```
or
```bash
python -m streamlit run npi_dashboard.py
```
or
```bash
streamlit run npi_dashboard.py
```

The dashboard will automatically open in your browser (typically `http://localhost:8501`)

## Data Structure

The dashboard works with CSV files containing the following columns:
- `npi`: National Provider Identifier
- `medical group`: Medical group/organization name
- `address`: Street address
- `address 2`: Additional address information (optional)
- `city`: City name
- `state`: State abbreviation
- `zip`: ZIP code
- `tab_source`: Data source tab identifier (automatically added)

## Key Functions

### Search Functionality
- Search across multiple fields simultaneously
- Case-insensitive search
- Supports partial matches

### State-Based Analysis
- View all NPIs for any specific state
- Compare NPI distribution across states
- Export state-specific data

### Data Export
- Download filtered results as CSV
- Download state-specific data
- Maintain original data formatting

## Performance Features

- **Data Caching**: Uses Streamlit's caching to improve performance
- **Efficient Filtering**: Optimized pandas operations for large datasets
- **Responsive Design**: Wide layout for better data visualization

## Troubleshooting

### Common Issues

1. **File Not Found Error**: Ensure the CSV file name matches exactly: `ELLKAY NPI List 2025.7.xlsx - Direct EHR 1A.csv`

2. **Memory Issues**: For very large datasets, consider:
   - Using a machine with more RAM
   - Filtering data before loading
   - Processing data in chunks

3. **Slow Performance**: 
   - Close other browser tabs
   - Restart the Streamlit server
   - Clear browser cache

## Customization

You can easily customize the dashboard by:
- Modifying the color scheme in the CSS section
- Adding new chart types using Plotly
- Including additional filters or search fields
- Adding new tabs for specific analysis needs

## Dependencies

- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive plotting library
- `numpy`: Numerical computing support 