# streamlit_app.py

import streamlit as st
import pandas as pd
import io
from zipfile import ZipFile
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from tempfile import NamedTemporaryFile

# === APP TITLE ===
st.title("CSV to Excel Report Generator")

# === FILE UPLOAD ===
st.header("Upload Files")
master_file = st.file_uploader("Upload Master Excel File", type=["xlsx"])
uploaded_csvs = st.file_uploader(
    "Upload CSV Files", 
    type=["csv"], 
    accept_multiple_files=True
)

if master_file and uploaded_csvs:
    st.success("Files uploaded successfully!")

    # Load master file
    master_df = pd.read_excel(master_file, engine='openpyxl')
    master_df.columns = [col.strip().title() for col in master_df.columns]

    # Process CSV files
    all_data = []
    for file in uploaded_csvs:
        try:
            df = pd.read_csv(file, header=None, names=['Timestamp', 'Asset Name', 'Active Power', 'Wind Speed'], on_bad_lines='skip')
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], dayfirst=True, errors='coerce')
            df['Date'] = df['Timestamp'].dt.date
            df = df.dropna(subset=['Timestamp', 'Asset Name'])
            all_data.append(df[['Timestamp', 'Date', 'Asset Name', 'Active Power']])
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    compiled_df = pd.concat(all_data, ignore_index=True)

    # === SHEET 1: COMPILED DATA ===
    sheet1 = compiled_df.merge(master_df, on='Asset Name', how='left')

    # === SHEET 2: DATA COUNT ===
    sheet2_counts = compiled_df.groupby(['Asset Name', 'Date']).size().reset_index(name='Count')
    sheet2 = sheet2_counts.merge(master_df, on='Asset Name', how='left')
    sheet2 = sheet2.groupby(['Make', 'Site', 'Date'])['Count'].sum().reset_index()
    sheet2_pivot = sheet2.pivot(index=['Make', 'Site'], columns='Date', values='Count').fillna(0).astype(int)
    sheet2_pivot.columns = [col.strftime('%d-%m-%Y') for col in sheet2_pivot.columns]
    sheet2_pivot.reset_index(inplace=True)

    # === SHEET 3: AVAILABILITY STATUS ===
    status_rows = []
    all_dates = sorted(compiled_df['Date'].dropna().unique())
    for (make, site), group in master_df.groupby(['Make', 'Site']):
        assets = group['Asset Name'].tolist()
        for date in all_dates:
            date_data = compiled_df[(compiled_df['Asset Name'].isin(assets)) & (compiled_df['Date'] == date)]
            asset_counts = date_data.groupby('Asset Name').size()
            total_assets = len(assets)
            avg = asset_counts.sum() / total_assets if total_assets > 0 else 0
            status = "Data Available" if avg >= 130 else "Data Not Available"
            status_rows.append({'Make': make, 'Site': site, 'Date': date, 'Status': status})

    sheet3 = pd.DataFrame(status_rows)
    sheet3_pivot = sheet3.pivot(index=['Make', 'Site'], columns='Date', values='Status')
    sheet3_pivot.columns = [col.strftime('%d-%m-%Y') for col in sheet3_pivot.columns]
    sheet3_pivot.reset_index(inplace=True)

    # === WRITE TO EXCEL (IN-MEMORY) ===
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        sheet1.to_excel(writer, index=False, sheet_name='Compiled Data')
        sheet2_pivot.to_excel(writer, index=False, sheet_name='Compiled Summary')
        sheet3_pivot.to_excel(writer, index=False, sheet_name='Result Data')

    # === COLOR SHEET 3 ===
    output.seek(0)
    wb = load_workbook(output)
    ws = wb['Result Data']

    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

    for row in ws.iter_rows(min_row=2, min_col=3):
        for cell in row:
            if cell.value == "Data Available":
                cell.fill = green_fill
            elif cell.value == "Data Not Available":
                cell.fill = red_fill

    final_output = io.BytesIO()
    wb.save(final_output)
    final_output.seek(0)

    # === PREVIEW DATAFRAMES ===
    st.header("Preview Sheets")
    with st.expander("Compiled Data"):
        st.dataframe(sheet1.head(50))
    with st.expander("Compiled Summary"):
        st.dataframe(sheet2_pivot.head(50))
    with st.expander("Result Data"):
        st.dataframe(sheet3_pivot.head(50))

    # === DOWNLOAD BUTTON ===
    st.download_button(
        label="📥 Download Excel File",
        data=final_output,
        file_name=f"final_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
