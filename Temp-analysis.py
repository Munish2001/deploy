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

# === Get Yesterday's Date ===
yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

st.title("🌡️ Suzlon Temperature Summary Report")

# === Upload CSV files ===
uploaded_files = st.file_uploader("Upload CSV files", type='csv', accept_multiple_files=True)

if uploaded_files:
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
        st.error("No valid CSV files loaded.")
        st.stop()

    # Combine all data
    compiled_df = pd.concat(raw_dfs, ignore_index=True)

    # Check required columns
    required_cols = temp_columns + ['Asset Name', 'ActivepowerGeneration']
    missing_cols = [col for col in required_cols if col not in compiled_df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    # Filter for ActivepowerGeneration > 0
    filtered_df = compiled_df[compiled_df['ActivepowerGeneration'] > 0]

    # Max aggregation per asset
    max_df = filtered_df.groupby('Asset Name')[temp_columns + ['ActivepowerGeneration']].max().reset_index()

    # Create result DataFrame with temperature flags
    result_df = max_df.copy()
    result_df['Temp11'] = (result_df[temp_columns[0]] >= 80).astype(int)
    result_df['Temp22'] = (result_df[temp_columns[1]] >= 90).astype(int)
    result_df['Temp33'] = (result_df[temp_columns[2]] >= 90).astype(int)
    result_df['Temp44'] = (result_df[temp_columns[3]] >= 90).astype(int)
    result_df['Temp55'] = (result_df[temp_columns[4]] >= 90).astype(int)
    result_df['Temp66'] = (result_df[temp_columns[5]] >= 60).astype(int)

    result_df['TempSum'] = result_df[['Temp11', 'Temp22', 'Temp33', 'Temp44', 'Temp55', 'Temp66']].sum(axis=1)

    # Filter assets multiselect
    asset_names = sorted(result_df['Asset Name'].unique())
    selected_assets = st.multiselect("Filter by Asset Name", asset_names, default=asset_names)
    filtered_result = result_df[result_df['Asset Name'].isin(selected_assets)]

    # Highlight function for rows
    def highlight_row(row):
        styles = []
        for col in row.index:
            if col.startswith('Temp') and col != 'TempSum' and row[col] == 1:
                styles.append('background-color: red; color: white')
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

    # Apply styling
    styled_df = filtered_result.style.apply(highlight_row, axis=1)

    st.markdown(f"### ✅ Result Data for {yesterday_str}")
    st.dataframe(styled_df, use_container_width=True)

else:
    st.info("Please upload one or more CSV files to proceed.")
    st.stop()
