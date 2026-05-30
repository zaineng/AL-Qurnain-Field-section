"""
modules/smart_kpis.py — Calculate field KPIs from filtered DataFrames
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import streamlit as st


def calc_kpis(res_df: pd.DataFrame, wells_df: pd.DataFrame,
              prod_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all platform KPIs from filtered dataframes.
    Returns dict of KPI name → value.
    """
    kpis: Dict[str, Any] = {}

    # ── Production KPIs ────────────────────────────────────────────────────
    if not prod_df.empty:
        latest = prod_df.sort_values("Date").tail(30) if "Date" in prod_df.columns else prod_df.tail(30)

        kpis["oil_rate"] = (
            latest["Oil_Rate"].sum() if "Oil_Rate" in latest.columns else 0
        )
        kpis["gas_rate"] = (
            latest["Gas_Rate"].sum() if "Gas_Rate" in latest.columns else 0
        )
        kpis["water_rate"] = (
            latest["Water_Rate"].sum() if "Water_Rate" in latest.columns else 0
        )
        kpis["cum_oil"] = (
            prod_df["Cum_Oil"].max() if "Cum_Oil" in prod_df.columns else
            prod_df["Oil_Rate"].sum() if "Oil_Rate" in prod_df.columns else 0
        )
        kpis["cum_gas"] = (
            prod_df["Cum_Gas"].max() if "Cum_Gas" in prod_df.columns else
            prod_df["Gas_Rate"].sum() if "Gas_Rate" in prod_df.columns else 0
        )
        total_liq = kpis["oil_rate"] + kpis["water_rate"]
        kpis["wor"] = (
            round(kpis["water_rate"] / kpis["oil_rate"], 2)
            if kpis["oil_rate"] > 0 else 0
        )
        kpis["gor"] = (
            round(kpis["gas_rate"] / kpis["oil_rate"], 0)
            if kpis["oil_rate"] > 0 else 0
        )
        kpis["water_cut"] = (
            round(kpis["water_rate"] / total_liq * 100, 1)
            if total_liq > 0 else 0
        )
    else:
        for k in ["oil_rate","gas_rate","water_rate","cum_oil","cum_gas","wor","gor","water_cut"]:
            kpis[k] = 0

    # ── Well KPIs ──────────────────────────────────────────────────────────
    if not wells_df.empty and "Well_Status" in wells_df.columns:
        status = wells_df["Well_Status"].astype(str).str.lower()
        kpis["producing_wells"] = int((status == "producing").sum())
        kpis["shutin_wells"]    = int(status.str.contains("shut").sum())
        kpis["testing_wells"]   = int(status.str.contains("test").sum())
        kpis["total_wells"]     = len(wells_df)
    else:
        kpis["producing_wells"] = 0
        kpis["shutin_wells"]    = 0
        kpis["testing_wells"]   = 0
        kpis["total_wells"]     = len(wells_df) if not wells_df.empty else 0

    # ── Reservoir KPIs ────────────────────────────────────────────────────
    if not res_df.empty:
        kpis["avg_pressure"] = (
            res_df["Pressure_psi"].mean() if "Pressure_psi" in res_df.columns else 0
        )
        kpis["avg_porosity"] = (
            res_df["Porosity_pct"].mean() if "Porosity_pct" in res_df.columns else 0
        )
        kpis["avg_permeability"] = (
            res_df["Permeability_mD"].mean() if "Permeability_mD" in res_df.columns else 0
        )
        kpis["avg_pressure_depletion"] = (
            res_df["Pressure_Depletion_pct"].mean()
            if "Pressure_Depletion_pct" in res_df.columns else None
        )
    else:
        kpis["avg_pressure"] = 0
        kpis["avg_porosity"] = 0
        kpis["avg_permeability"] = 0
        kpis["avg_pressure_depletion"] = None

    # ── Performance indicator (0–100) ─────────────────────────────────────
    total = kpis["producing_wells"] + kpis["shutin_wells"]
    prod_eff = (kpis["producing_wells"] / total * 100) if total > 0 else 100
    kpis["field_performance"] = round(prod_eff, 1)

    return kpis


def fmt(val, decimals=0, suffix=""):
    """Format a number nicely, returning '—' for None/NaN."""
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return "—"
        if decimals == 0:
            return f"{int(round(val)):,}{suffix}"
        return f"{val:,.{decimals}f}{suffix}"
    except Exception:
        return str(val)


def render_kpi_cards(kpis: Dict[str, Any]):
    """Render 4-column KPI card row in Streamlit."""
    cards = [
        ("OIL RATE",         fmt(kpis["oil_rate"],   0, " bbl/d"),   "blue",   "🛢️"),
        ("GAS RATE",         fmt(kpis["gas_rate"],   1, " MMscfd"),  "green",  "🔥"),
        ("PRODUCING WELLS",  fmt(kpis["producing_wells"]),            "orange", "⚙️"),
        ("AVG. PRESSURE",    fmt(kpis["avg_pressure"], 0, " psi"),    "purple", "📊"),
        ("CUM. OIL",         fmt(kpis["cum_oil"],    0, " MBO"),      "blue",   "📦"),
        ("SHUT-IN WELLS",    fmt(kpis["shutin_wells"]),               "red",    "🔴"),
        ("WATER CUT",        fmt(kpis["water_cut"],  1, "%"),         "orange", "💧"),
        ("FIELD EFF.",       fmt(kpis["field_performance"], 1, "%"),  "green",  "📈"),
    ]
    cols = st.columns(4)
    for i, (lbl, val, accent, icon) in enumerate(cards[:4]):
        with cols[i]:
            st.markdown(
                f'<div class="kpi-card kpi-accent-{accent}">'
                f'<div class="kpi-label">{icon} {lbl}</div>'
                f'<div class="kpi-value">{val}</div>'
                f'</div>',
                unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    cols2 = st.columns(4)
    for i, (lbl, val, accent, icon) in enumerate(cards[4:]):
        with cols2[i]:
            st.markdown(
                f'<div class="kpi-card kpi-accent-{accent}">'
                f'<div class="kpi-label">{icon} {lbl}</div>'
                f'<div class="kpi-value">{val}</div>'
                f'</div>',
                unsafe_allow_html=True)


def render_reservoir_summary_cards(res_df: pd.DataFrame, wells_df: pd.DataFrame):
    """Render reservoir-specific KPI cards for the Reservoir page."""
    def v(df, col, agg="mean"):
        if df.empty or col not in df.columns:
            return "—"
        val = df[col].mean() if agg == "mean" else df[col].sum()
        return fmt(val, 1)

    well_status = wells_df["Well_Status"].astype(str).str.lower() if not wells_df.empty and "Well_Status" in wells_df.columns else pd.Series([])
    producing   = int((well_status == "producing").sum())
    shutin      = int(well_status.str.contains("shut").sum())

    cards = [
        ("RESERVOIR PRESSURE",   v(res_df, "Pressure_psi", "mean") + " psi",  "blue"),
        ("AVG POROSITY",         v(res_df, "Porosity_pct",  "mean") + " %",   "green"),
        ("AVG PERMEABILITY",     v(res_df, "Permeability_mD","mean") + " mD", "orange"),
        ("CURRENT PRODUCTION",   v(res_df, "Production_bopd","sum") + " bpd", "purple"),
        ("CUM. PRODUCTION",      v(res_df, "Cum_Production_MBO","sum") + " MBO","blue"),
        ("PRODUCING WELLS",      str(producing),                                "green"),
        ("SHUT-IN WELLS",        str(shutin),                                   "red"),
        ("TOTAL WELLS",          str(len(wells_df)),                            "orange"),
    ]

    cols = st.columns(4)
    for i, (lbl, val, accent) in enumerate(cards[:4]):
        with cols[i]:
            st.markdown(
                f'<div class="kpi-card kpi-accent-{accent}">'
                f'<div class="kpi-label">{lbl}</div>'
                f'<div class="kpi-value">{val}</div>'
                f'</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    cols2 = st.columns(4)
    for i, (lbl, val, accent) in enumerate(cards[4:]):
        with cols2[i]:
            st.markdown(
                f'<div class="kpi-card kpi-accent-{accent}">'
                f'<div class="kpi-label">{lbl}</div>'
                f'<div class="kpi-value">{val}</div>'
                f'</div>',
                unsafe_allow_html=True)
