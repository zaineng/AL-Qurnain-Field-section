"""
modules/reservoir_filters.py — Global filtering system (Reservoir + Well)
"""
import streamlit as st
import pandas as pd
from typing import Tuple
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def render_sidebar_filters(data) -> Tuple[str, str]:
    """
    Render reservoir/well dropdowns in the sidebar.
    Returns (selected_reservoir, selected_well).
    Persists choices in session_state.
    """
    from config import C

    # ── Reservoir selector ─────────────────────────────────────────────────
    st.sidebar.markdown(
        '<div class="sidebar-section">🔭 FIELD FILTER</div>',
        unsafe_allow_html=True)

    reservoir_opts = ["Show All"] + (data.reservoir_names if data else [])
    if not st.session_state.get("sel_reservoir") in reservoir_opts:
        st.session_state["sel_reservoir"] = "Show All"

    reservoir = st.sidebar.selectbox(
        "Reservoir",
        options=reservoir_opts,
        index=reservoir_opts.index(st.session_state.get("sel_reservoir", "Show All")),
        key="_rsv_sel",
    )
    st.session_state["sel_reservoir"] = reservoir

    # ── Well selector — filtered by reservoir ─────────────────────────────
    well_opts = ["Show All Wells"]
    if data:
        well_opts += data.wells_for_reservoir(reservoir)

    if st.session_state.get("sel_well") not in well_opts:
        st.session_state["sel_well"] = "Show All Wells"

    well = st.sidebar.selectbox(
        "Well",
        options=well_opts,
        index=well_opts.index(st.session_state.get("sel_well", "Show All Wells")),
        key="_well_sel",
    )
    st.session_state["sel_well"] = well
    return reservoir, well


def apply_filters(data, reservoir: str, well: str):
    """
    Return filtered copies of each dataframe based on reservoir/well selection.
    Returns: (res_df, wells_df, prod_df, decline_df, contacts_df, layers_df, gas_df)
    """
    res_df      = data.reservoirs.copy()  if data else pd.DataFrame()
    wells_df    = data.wells.copy()       if data else pd.DataFrame()
    prod_df     = data.production.copy()  if data else pd.DataFrame()
    dec_df      = data.decline.copy()     if data else pd.DataFrame()
    contacts_df = data.contacts.copy()    if data else pd.DataFrame()
    layers_df   = data.layers.copy()      if data else pd.DataFrame()
    gas_df      = data.gas_supply.copy()  if data else pd.DataFrame()

    def _rsv_filter(df, col="Reservoir_Name"):
        if df.empty or col not in df.columns:
            return df
        return df[df[col] == reservoir] if reservoir != "Show All" else df

    def _well_filter(df, col="Well_Name"):
        if df.empty or col not in df.columns:
            return df
        return df[df[col] == well] if well != "Show All Wells" else df

    # Apply reservoir filter
    res_df      = _rsv_filter(res_df)
    wells_df    = _rsv_filter(wells_df)
    prod_df     = _rsv_filter(prod_df)
    dec_df      = _rsv_filter(dec_df)
    contacts_df = _rsv_filter(contacts_df)
    layers_df   = _rsv_filter(layers_df)
    gas_df      = _rsv_filter(gas_df, col="Reservoir_Name") if "Reservoir_Name" in gas_df.columns else gas_df

    # Apply well filter (on top of reservoir filter)
    if well != "Show All Wells":
        wells_df = _well_filter(wells_df)
        prod_df  = _well_filter(prod_df)
        dec_df   = _well_filter(dec_df)

    return res_df, wells_df, prod_df, dec_df, contacts_df, layers_df, gas_df


def get_dynamic_image_path(maps_df: pd.DataFrame, reservoir: str, img_type: str) -> str | None:
    """
    Look up the image path for a given reservoir and image type.
    img_type: 'Structural_Map_Path' | 'Correlation_Image_Path' | 'Pressure_Map_Path'
    """
    if maps_df.empty or reservoir == "Show All":
        return None
    if "Reservoir_Name" not in maps_df.columns or img_type not in maps_df.columns:
        return None
    row = maps_df[maps_df["Reservoir_Name"] == reservoir]
    if row.empty:
        return None
    val = str(row.iloc[0][img_type]).strip()
    return val if val and val.lower() not in ("nan", "—", "") else None


def get_filter_badge(reservoir: str, well: str) -> str:
    """Return HTML badge string showing active filters."""
    parts = []
    if reservoir != "Show All":
        parts.append(f'<span style="background:#0d2540;border:1px solid #1a5a9a;'
                     f'border-radius:20px;padding:2px 8px;font-size:9px;color:#3aafff;'
                     f'font-family:Share Tech Mono,monospace">📍 {reservoir}</span>')
    if well != "Show All Wells":
        parts.append(f'<span style="background:#0d2540;border:1px solid #1a5a9a;'
                     f'border-radius:20px;padding:2px 8px;font-size:9px;color:#3aafff;'
                     f'font-family:Share Tech Mono,monospace">🔩 {well}</span>')
    if not parts:
        parts.append(f'<span style="background:#0a1d2e;border:1px solid #0d2540;'
                     f'border-radius:20px;padding:2px 8px;font-size:9px;color:#3a6a8a;'
                     f'font-family:Share Tech Mono,monospace">🌐 All Field</span>')
    return " ".join(parts)
