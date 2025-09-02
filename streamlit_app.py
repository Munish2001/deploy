# streamlit_app.py

import streamlit as st
import pandas as pd
import io
from zipfile import ZipFile
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from tempfile import NamedTemporaryFile

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="BCT Data Availability",
    page_icon="📊",
    layout="wide",
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
        body {
            background-color: #f7f9fa;
        }
        .reportview-container .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stButton>button {
            background-color: #009999;
            color: white;
            border-radius: 8px;
            padding: 0.6em 1em;
        }
        .stDownloadButton>button {
            background-color: #0066cc;
            color: white;
            border-radius: 8px;
            padding: 0.6em 1em;
            font-weight: bold;
        }
        h1, h2, h3 {
            color: #004d66;
        }
        .custom-table thead tr {
            background-color: #004d66;
            color: white;
        }
        .custom-table td, .custom-table th {
            border: 1px solid #ccc;
            padding: 8px 12px;
        }
        .custom-table {
            border-collapse: collapse;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.title("📈 BCT Data Availability Dashboard")

# --- FILE UPLOAD ---
st.header("📂 Upload Required Files")

col1, col2 = st.columns(2)
with col1:
    master_file = st.file_uploader("Upload Master Excel File", type=["xlsx"])
with col2:
    uploaded_csvs = st.file_uploader(
        "Upload CSV Files",
        type=["csv"],
        accept_multiple_files=True
    )

if master_file and uploaded_csvs:
    st.success("✅ Files uploaded successfully!")

    # --- READ MASTER FILE ---
    master_df = pd.read_excel(master_file, engine='openpyxl')
    master_df.columns = [col.strip().title() for col in master_df.columns]

    # --- READ CSV FILES ---
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

    # === SHEET 1 ===
    sheet1 = compiled_df.merge(master_df, on='Asset Name', how='left')

    # === SHEET 2 ===
    sheet2_counts = compiled_df.groupby(['Asset Name', 'Date']).size().reset_index(name='Count')
    sheet2 = sheet2_counts.merge(master_df, on='Asset Name', how='left')
    sheet2 = sheet2.groupby(['Make', 'Site', 'Date'])['Count'].sum().reset_index()
    sheet2_pivot = sheet2.pivot(index=['Make', 'Site'], columns='Date', values='Count').fillna(0).astype(int)
    sheet2_pivot.columns = [col.strftime('%d-%m-%Y') for col in sheet2_pivot.columns]
    sheet2_pivot.reset_index(inplace=True)

    # === SHEET 3 ===
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

    # === EXPORT TO EXCEL ===
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

    # === DATA PREVIEW ===
    st.header("🔍 Preview of Processed Data")

    def display_as_html_table(df, title):
        st.subheader(title)
        html = df.head(50).to_html(classes='custom-table', index=False, escape=False)
        st.markdown(html, unsafe_allow_html=True)

    display_as_html_table(sheet2_pivot, "Compiled Summary")
    display_as_html_table(sheet3_pivot, "Result Data")

    # === DOWNLOAD BUTTON ===
    st.download_button(
        label="📥 Download Final Excel File",
        data=final_output,
        file_name=f"data_availability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    def display_status_table(df):
    styled_df = df.copy()
    for col in styled_df.columns[2:]:
        styled_df[col] = styled_df[col].replace({
            'Data Available': '<span style="background-color:#c6efce; color:#006100; padding:4px; border-radius:4px;">Available</span>',
            'Data Not Available': '<span style="background-color:#ffc7ce; color:#9c0006; padding:4px; border-radius:4px;">Not Available</span>'
        })
    html = styled_df.to_html(escape=False, index=False, classes="custom-table")
    st.markdown(html, unsafe_allow_html=True)


    import matplotlib.pyplot as plt

def plot_pie_charts(df):
    st.subheader("📊 Data Availability Distribution (Pie Charts)")

    grouped = df.groupby(['Make', 'Site'])
    for (make, site), group in grouped:
        counts = group['Status'].value_counts()
        labels = counts.index.tolist()
        values = counts.values.tolist()

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%',
               startangle=90, colors=["#2ecc71", "#e74c3c"])
        ax.axis('equal')  # Equal aspect ratio for pie
        st.markdown(f"**{make} - {site}**")
        st.pyplot(fig)


else:
    st.warning("📌 Please upload both Master Excel and CSV files to continue.")
