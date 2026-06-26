"""
Streamlit dashboard for the retail ETL pipeline.

Lets you upload new raw CSVs (customers/products/orders), run the full
validate -> transform -> load -> insights pipeline, and view the results
as tables and charts. Also keeps a small run-history log so you can see
data-quality trends across runs.

Run with:
    streamlit run dashboard.py
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import src.config as config
from src.insights.reporter import run_insights
from src.load.loader import run_load
from src.transform.transformer import run_transformation
from src.validation.validator import run_validation

RUN_HISTORY_PATH = config.PROJECT_ROOT / "data" / "run_history.csv"

st.set_page_config(page_title="Retail ETL Dashboard", layout="wide")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def save_uploaded_files(uploaded_files: dict) -> list[str]:
    """Write any uploaded files into data/raw/, overwriting existing ones."""
    saved = []
    config.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for entity, file in uploaded_files.items():
        if file is not None:
            target: Path = config.RAW_FILES[entity]
            target.write_bytes(file.getvalue())
            saved.append(entity)
    return saved


def append_run_history(validation_results: dict, loaded: dict) -> None:
    """Append a one-row summary of this run to data/run_history.csv."""
    row = {"timestamp": datetime.now().isoformat(timespec="seconds")}
    for entity, data in validation_results.items():
        row[f"{entity}_valid"] = len(data["valid"])
        row[f"{entity}_rejected"] = len(data["rejected"])
    for table, count in loaded.items():
        row[f"{table}_loaded"] = count

    history = pd.DataFrame([row])
    if RUN_HISTORY_PATH.exists():
        existing = pd.read_csv(RUN_HISTORY_PATH)
        history = pd.concat([existing, history], ignore_index=True)
    history.to_csv(RUN_HISTORY_PATH, index=False)


def raw_files_exist() -> bool:
    return all(path.exists() for path in config.RAW_FILES.values())


# --------------------------------------------------------------------------
# Sidebar: upload + run controls
# --------------------------------------------------------------------------

st.sidebar.header("1. Upload raw data")
st.sidebar.caption("Uploading a file replaces the existing CSV of the same type.")

uploaded_files = {
    "customers": st.sidebar.file_uploader("Customers CSV", type="csv", key="customers"),
    "products": st.sidebar.file_uploader("Products CSV", type="csv", key="products"),
    "orders": st.sidebar.file_uploader("Orders CSV", type="csv", key="orders"),
}

st.sidebar.header("2. Run the pipeline")
run_clicked = st.sidebar.button("Run ETL Pipeline", type="primary", use_container_width=True)

st.title("Retail ETL Dashboard")
st.caption("Upload data, run the pipeline, and review validation + business insights.")

if "last_run" not in st.session_state:
    st.session_state.last_run = None

# --------------------------------------------------------------------------
# Run pipeline
# --------------------------------------------------------------------------

if run_clicked:
    saved = save_uploaded_files(uploaded_files)
    if saved:
        st.sidebar.success(f"Updated: {', '.join(saved)}")

    if not raw_files_exist():
        st.error(
            "No raw data found yet. Upload customers.csv, products.csv, and "
            "orders.csv (or make sure they already exist in data/raw/) before running."
        )
    else:
        with st.spinner("Running pipeline: validate → transform → load → insights..."):
            try:
                validation_results = run_validation()
                cleaned = run_transformation(validation_results)
                loaded = run_load(cleaned)
                reports = run_insights()
                append_run_history(validation_results, loaded)

                st.session_state.last_run = {
                    "validation_results": validation_results,
                    "loaded": loaded,
                    "reports": reports,
                }
                st.success("Pipeline run complete.")
            except Exception as exc:  # noqa: BLE001 - surface any pipeline error to the user
                st.error(f"Pipeline failed: {exc}")

# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------

if st.session_state.last_run is None:
    st.info("Upload your CSVs and click **Run ETL Pipeline** to see results here.")
else:
    validation_results = st.session_state.last_run["validation_results"]
    loaded = st.session_state.last_run["loaded"]
    reports = st.session_state.last_run["reports"]

    st.header("Validation Summary")
    cols = st.columns(len(validation_results))
    for col, (entity, data) in zip(cols, validation_results.items()):
        valid_count = len(data["valid"])
        rejected_count = len(data["rejected"])
        col.metric(
            label=entity.capitalize(),
            value=f"{valid_count} valid",
            delta=f"{rejected_count} rejected",
            delta_color="inverse",
        )

    any_rejected = any(not data["rejected"].empty for data in validation_results.values())
    if any_rejected:
        with st.expander("View rejected rows and reasons"):
            for entity, data in validation_results.items():
                if not data["rejected"].empty:
                    st.subheader(entity.capitalize())
                    st.dataframe(data["rejected"], use_container_width=True)
    else:
        st.success("No rows were rejected in this run.")

    st.header("Rows Loaded into Database")
    st.dataframe(
        pd.DataFrame(list(loaded.items()), columns=["table", "rows_loaded"]),
        use_container_width=True,
        hide_index=True,
    )

    st.header("Business Insights")

    top_products = reports["top_selling_products"]
    revenue_trends = reports["revenue_trends"]
    customer_stats = reports["customer_purchase_stats"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Selling Products")
        if top_products.empty:
            st.write("No order data available yet.")
        else:
            fig = px.bar(
                top_products.head(10),
                x="product_name",
                y="total_revenue",
                color="category",
                hover_data=["total_quantity_sold"],
                labels={"product_name": "Product", "total_revenue": "Revenue"},
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue Trend Over Time")
        if revenue_trends.empty:
            st.write("No order data available yet.")
        else:
            fig = px.line(
                revenue_trends,
                x="order_date",
                y="daily_revenue",
                markers=True,
                labels={"order_date": "Date", "daily_revenue": "Revenue"},
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer Purchase Stats")
    if customer_stats.empty:
        st.write("No customer order data available yet.")
    else:
        fig = px.scatter(
            customer_stats,
            x="order_frequency",
            y="total_spend",
            size="average_order_value",
            hover_name="name",
            labels={"order_frequency": "Number of Orders", "total_spend": "Total Spend"},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(customer_stats, use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------
# Run history (data quality trend across runs)
# --------------------------------------------------------------------------

st.header("Run History")
if RUN_HISTORY_PATH.exists():
    history_df = pd.read_csv(RUN_HISTORY_PATH)
    st.dataframe(history_df, use_container_width=True, hide_index=True)

    reject_cols = [c for c in history_df.columns if c.endswith("_rejected")]
    if len(history_df) > 1 and reject_cols:
        fig = px.line(
            history_df,
            x="timestamp",
            y=reject_cols,
            markers=True,
            labels={"value": "Rejected rows", "timestamp": "Run"},
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No runs yet. Run the pipeline at least once to build run history.")
