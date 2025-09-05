import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# === Settings ===
active_power_threshold = 500
temp_columns = [
    'OilSumpTemp',
    'GearboxHighSpeedShaftDrivenEndtemp',
    'GearboxHighSpeedShaftNonDrivenEndtemp',
    'Temperaturemeasurementforgeneratorbearingdriveend',
    'Temperaturemeasurementforgeneratorbearingnondriveend',
    'MeasuredTemperatureofrotorbearing'
]

# Get Yesterday's Date for reference
yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

st.title("🌡️ Suzlon Temperature Summary Report")

# Upload main CSV files
st.header("Upload main data CSV files")
uploaded_files = st.file_uploader(
    "Upload CSV files containing temperature data",
    type='csv', accept_multiple_files=True
)

# Upload master Excel lookup file
st.header("Upload master lookup file (Excel .xlsx) with Asset Name and Site")
master_file = st.file_uploader(
    "Upload master Excel file",
    type=['xlsx']
)

if not uploaded_files or not master_file:
    st.info("Please upload both main CSV files and the master lookup Excel file to proceed.")
    st.stop()

# Read master Excel file
try:
    master_df = pd.read_excel(master_file)
    if 'Asset Name' not in master_df.columns or 'Site' not in master_df.columns:
        st.error("Master Excel file must contain 'Asset Name' and 'Site' columns.")
        st.stop()
except Exception as e:
    st.error(f"Error reading master Excel file: {e}")
    st.stop()

# Read main CSV files
raw_dfs = []
for uploaded_file in uploaded_files:
    try:
        df = pd.read_csv(uploaded_file)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        if not df.empty:
            raw_dfs.append(df)
    except Exception as e:
        st.warning(f"Error reading {uploaded_file.name}: {e}")

if not raw_dfs:
    st.error("No valid main CSV files loaded.")
    st.stop()

compiled_df = pd.concat(raw_dfs, ignore_index=True)

# Required columns check
required_cols = temp_columns + ['Asset Name', 'ActivepowerGeneration']
missing_cols = [col for col in required_cols if col not in compiled_df.columns]
if missing_cols:
    st.error(f"Missing required columns in main data files: {missing_cols}")
    st.stop()

# Filter rows where ActivepowerGeneration > 0
filtered_df = compiled_df[compiled_df['ActivepowerGeneration'] > 0]

# Max aggregation per Asset Name
max_df = filtered_df.groupby('Asset Name')[temp_columns + ['ActivepowerGeneration']].max().reset_index()

# Merge with master lookup to get Site info
result_df = max_df.merge(master_df[['Asset Name', 'Site']], on='Asset Name', how='left')

# Add temperature flags
result_df['Temp11'] = (result_df[temp_columns[0]] >= 80).astype(int)
result_df['Temp22'] = (result_df[temp_columns[1]] >= 90).astype(int)
result_df['Temp33'] = (result_df[temp_columns[2]] >= 90).astype(int)
result_df['Temp44'] = (result_df[temp_columns[3]] >= 90).astype(int)
result_df['Temp55'] = (result_df[temp_columns[4]] >= 90).astype(int)
result_df['Temp66'] = (result_df[temp_columns[5]] >= 60).astype(int)

result_df['TempSum'] = result_df[['Temp11', 'Temp22', 'Temp33', 'Temp44', 'Temp55', 'Temp66']].sum(axis=1)

# Sidebar filters for Site and Asset Name
st.sidebar.header("Filters")

site_options = sorted(result_df['Site'].dropna().unique())
selected_sites = st.sidebar.multiselect("Filter by Site", site_options, default=site_options)

filtered_site_df = result_df[result_df['Site'].isin(selected_sites)]

asset_options = sorted(filtered_site_df['Asset Name'].unique())
selected_assets = st.sidebar.multiselect("Filter by Asset Name", asset_options, default=asset_options)

final_df = filtered_site_df[filtered_site_df['Asset Name'].isin(selected_assets)]

# Highlighting styles function for dataframe.style
def highlight_row(row):
    styles = []
    for col in row.index:
        # Highlight Temp flags columns with 1 → red bg, white text
        if col in ['Temp11', 'Temp22', 'Temp33', 'Temp44', 'Temp55', 'Temp66'] and row[col] == 1:
            styles.append('background-color: red; color: white')
        # Highlight TempSum with:
        # 0 → green bg
        # 1 → yellow bg
        # >1 → red bg
        elif col == 'TempSum':
            if row[col] == 0:
                styles.append('background-color: lightgreen; color: black')
            elif row[col] == 1:
                styles.append('background-color: yellow; color: black')
            elif row[col] > 1:
                styles.append('background-color: red; color: white')
            else:
                styles.append('')
        else:
            styles.append('')
    return styles

# Display result with styling
st.markdown(f"### ✅ Result Data for {yesterday_str}")
st.dataframe(final_df.style.apply(highlight_row, axis=1), use_container_width=True)
