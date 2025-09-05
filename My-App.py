import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

        # List 1: Select Asset Name
        asset_column = st.selectbox("Select Asset Name Column", df.columns)
        asset_names = df[asset_column].unique().tolist()
        selected_assets = st.multiselect("Select Asset(s)", asset_names)

        # List 2: Select measurement columns
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        selected_columns = st.multiselect("Select columns to plot", numeric_columns)

        # List 3: Select Date Column
        date_column = st.selectbox("Select Date Column", df.columns)

    # Filter data based on selections
    if selected_assets and selected_columns and date_column:
        filtered_df = df[df[asset_column].isin(selected_assets)]

        # Convert date column to datetime
        try:
            filtered_df[date_column] = pd.to_datetime(filtered_df[date_column])
        except Exception as e:
            st.error(f"Error parsing dates: {e}")
            st.stop()

        # Step 4: Plot
        st.write("### 📈 Line Chart")
        fig, ax = plt.subplots(figsize=(12, 6))

        for asset in selected_assets:
            asset_data = filtered_df[filtered_df[asset_column] == asset]
            for col in selected_columns:
                ax.plot(asset_data[date_column], asset_data[col], label=f"{asset} - {col}")

        ax.set_xlabel("Date")
        ax.set_ylabel("Values")
        ax.set_title("Line Chart of Selected Data")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

    else:
        st.warning("Please select Asset(s), Column(s), and Date column to plot.")
