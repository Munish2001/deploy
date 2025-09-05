import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Asset Data Visualizer")

# Step 1: File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Step 2: Load CSV
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")

    st.write("### Preview of Data")
    st.dataframe(df.head())

    # Step 3: User selections
    with st.sidebar:
        st.header("🔍 Filter Options")

        # Select asset column
        asset_column = st.selectbox("Select Asset Name Column", df.columns)
        asset_names = df[asset_column].unique().tolist()
        selected_assets = st.multiselect("Select Asset(s)", asset_names)

        # Select measurement columns (only numeric)
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        selected_columns = st.multiselect("Select columns to plot", numeric_columns)

        # Select date column
        date_column = st.selectbox("Select Date Column", df.columns)

        # Convert date column to datetime for filtering
        try:
            df[date_column] = pd.to_datetime(df[date_column])
            min_date = df[date_column].min().date()
            max_date = df[date_column].max().date()
            selected_date_range = st.date_input("Select Date Range", [min_date, max_date])
        except Exception as e:
            st.error(f"Date conversion error: {e}")
            st.stop()

    # Step 4: Filter and Plot
    if selected_assets and selected_columns and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    mask = (
        df[asset_column].isin(selected_assets) &
        (df[date_column] >= pd.to_datetime(start_date)) &
        (df[date_column] <= pd.to_datetime(end_date))
    )
    filtered_df = df[mask]

    if not filtered_df.empty:
        st.write("### 📈 Interactive Line Chart (Plotly)")

        # Melt data for Plotly (long format)
        melted_df = filtered_df.melt(
            id_vars=[date_column, asset_column],
            value_vars=selected_columns,
            var_name="Metric",
            value_name="Value"
        )

        # Combine Asset and Metric for legend clarity
        melted_df["Series"] = melted_df[asset_column] + " - " + melted_df["Metric"]

        # Create Plotly chart
        fig = px.line(
            melted_df,
            x=date_column,
            y="Value",
            color="Series",
            title="Line Chart of Selected Metrics by Asset",
            template="plotly_dark",  # Dark mode
            markers=True
        )

        fig.update_layout(
            legend_title_text="Assets & Metrics",
            xaxis_title="Date",
            yaxis_title="Values",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
else:
    st.warning("Please select Asset(s), Column(s), and Date Range to plot.")
