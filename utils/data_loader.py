import pandas as pd
import streamlit as st
from config import REQUIRED_COLUMNS, LIFECYCLE_STAGES # Importing necessary libraries and configuration constants

# This module handles loading and processing the application portfolio data.
def load_portfolio(uploaded_file) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(uploaded_file) # Attempt to read the uploaded CSV file into a DataFrame
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return None
    
    # Standardize column names: strip whitespace, lowercase, replace spaces with underscores
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns] # Check for missing required columns in the uploaded data
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.info("Expected: " + ", ".join(REQUIRED_COLUMNS))
        return None

    df = _clean(df) # Clean the data by converting types, handling missing values, and standardizing formats
    df = _enrich(df) # Enrich the data by adding calculated fields such as age, rationalization quadrant, cost per value point, and risk score
    return df

# Additional helper functions for cleaning and enriching the data
def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df["tech_debt_score"] = pd.to_numeric(df["tech_debt_score"], errors="coerce").clip(0, 10)
    df["business_value_score"] = pd.to_numeric(df["business_value_score"], errors="coerce").clip(0, 10)
    df["annual_cost_usd"] = pd.to_numeric(df["annual_cost_usd"], errors="coerce").fillna(0)
    df["last_updated_year"] = pd.to_numeric(df["last_updated_year"], errors="coerce").fillna(2020)
    df["lifecycle_stage"] = df["lifecycle_stage"].str.strip()
    df["app_name"] = df["app_name"].str.strip()
    df = df.dropna(subset=["tech_debt_score", "business_value_score"])
    return df

# Enrich the data with additional calculated fields for analysis and visualization
def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    df["age_years"] = 2025 - df["last_updated_year"].astype(int)

    df["rationalization_quadrant"] = df.apply(_quadrant, axis=1)

    df["cost_per_value_point"] = (
        df["annual_cost_usd"] / df["business_value_score"].replace(0, 0.1)
    ).round(0)
    
# Calculate a composite risk score based on tech debt, age, and inverse business value
    df["risk_score"] = (
        (df["tech_debt_score"] * 0.5) +
        (df["age_years"].clip(0, 10) * 0.3) +
        ((10 - df["business_value_score"]) * 0.2)
    ).round(2)

    return df

# Determine the rationalization quadrant for each application based on tech debt and business value scores
def _quadrant(row) -> str:
    td = row["tech_debt_score"]
    bv = row["business_value_score"]
    if td <= 5 and bv >= 5:
        return "Invest"
    elif td > 5 and bv >= 5:
        return "Modernize"
    elif td <= 5 and bv < 5:
        return "Monitor"
    else:
        return "Retire"

# Generate a summary of the portfolio for dashboard display, including totals, counts, and groupings by various dimensions
def portfolio_summary(df: pd.DataFrame) -> dict:
    return {
        "total_apps": len(df),
        "total_cost": int(df["annual_cost_usd"].sum()),
        "high_debt_count": int((df["tech_debt_score"] >= 7).sum()),
        "retire_candidates": int(
            df["lifecycle_stage"].isin(["End of Life", "Phase Out"]).sum()
        ),
        "quadrant_counts": df["rationalization_quadrant"].value_counts().to_dict(),
        "lifecycle_counts": df["lifecycle_stage"].value_counts().to_dict(),
        "hosting_cost": df.groupby("hosting_type")["annual_cost_usd"].sum().to_dict(),
        "capability_debt": df.groupby("business_capability")["tech_debt_score"].mean().round(1).to_dict(),
    }