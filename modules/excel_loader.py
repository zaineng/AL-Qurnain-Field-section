"""
modules/excel_loader.py — Load and cache the unified Excel workbook
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import sys, os
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import UNIFIED_DB


# ── Sheet names ────────────────────────────────────────────────────────────────
SHEET_RESERVOIR  = "Reservoir_Master"
SHEET_WELLS      = "Wells"
SHEET_PRODUCTION = "Production_Data"
SHEET_DECLINE    = "Decline_Data"
SHEET_MAPS       = "Reservoir_Maps"
SHEET_CONTACTS   = "Fluid_Contacts"
SHEET_DRILLING   = "Drilling_Data"
SHEET_LAYERS     = "Layer_Production"
SHEET_GAS_SUPPLY = "Gas_Supply"
SHEET_DAILY_RPT  = "Daily_Report"
SHEET_WELL_TESTS = "Well_Test_Results"


class PlatformData:
    """Container for all loaded dataframes."""
    def __init__(self):
        self.reservoirs:   pd.DataFrame = pd.DataFrame()
        self.wells:        pd.DataFrame = pd.DataFrame()
        self.production:   pd.DataFrame = pd.DataFrame()
        self.decline:      pd.DataFrame = pd.DataFrame()
        self.maps:         pd.DataFrame = pd.DataFrame()
        self.contacts:     pd.DataFrame = pd.DataFrame()
        self.drilling:     pd.DataFrame = pd.DataFrame()
        self.layers:       pd.DataFrame = pd.DataFrame()
        self.gas_supply:   pd.DataFrame = pd.DataFrame()
        self.daily_report: pd.DataFrame = pd.DataFrame()
        self.well_tests:   pd.DataFrame = pd.DataFrame()
        self.source:       str = "demo"

    @property
    def reservoir_names(self) -> list:
        if self.reservoirs.empty or "Reservoir_Name" not in self.reservoirs.columns:
            return []
        return sorted(self.reservoirs["Reservoir_Name"].dropna().unique().tolist())

    def wells_for_reservoir(self, reservoir: str) -> list:
        if self.wells.empty or "Well_Name" not in self.wells.columns:
            return []
        if reservoir == "Show All":
            return sorted(self.wells["Well_Name"].dropna().unique().tolist())
        if "Reservoir_Name" not in self.wells.columns:
            return sorted(self.wells["Well_Name"].dropna().unique().tolist())
        return sorted(
            self.wells[self.wells["Reservoir_Name"] == reservoir]["Well_Name"]
            .dropna().unique().tolist()
        )


@st.cache_data(ttl=30, show_spinner=False)
def _load_from_path(path: str) -> PlatformData:
    data = PlatformData()
    try:
        xl = pd.ExcelFile(path)
        sn = xl.sheet_names

        def safe_parse(sheet):
            if sheet in sn:
                df = xl.parse(sheet)
                df.columns = [str(c).strip() for c in df.columns]
                return df
            return pd.DataFrame()

        data.reservoirs   = safe_parse(SHEET_RESERVOIR)
        data.wells        = safe_parse(SHEET_WELLS)
        data.contacts     = safe_parse(SHEET_CONTACTS)
        data.maps         = safe_parse(SHEET_MAPS)
        data.drilling     = safe_parse(SHEET_DRILLING)
        data.layers       = safe_parse(SHEET_LAYERS)
        data.gas_supply   = safe_parse(SHEET_GAS_SUPPLY)
        data.daily_report = safe_parse(SHEET_DAILY_RPT)
        data.well_tests   = safe_parse(SHEET_WELL_TESTS)

        # Production — parse Date column
        prod = safe_parse(SHEET_PRODUCTION)
        if not prod.empty and "Date" in prod.columns:
            prod["Date"] = pd.to_datetime(prod["Date"], errors="coerce")
        data.production = prod

        # Decline — parse Date column
        dec = safe_parse(SHEET_DECLINE)
        if not dec.empty and "Date" in dec.columns:
            dec["Date"] = pd.to_datetime(dec["Date"], errors="coerce")
        data.decline = dec

        data.source = "uploaded"
    except Exception as e:
        print(f"[excel_loader] error loading {path}: {e}")
    return data


def load_data(uploaded_file=None) -> PlatformData:
    """
    Load platform data.
    Priority: uploaded_file > UNIFIED_DB > empty PlatformData
    """
    if uploaded_file is not None:
        # Save to temp and load
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        data = _load_from_path(tmp_path)
        data.source = "uploaded"
        return data

    if UNIFIED_DB.exists():
        return _load_from_path(str(UNIFIED_DB))

    # Return empty data object
    return PlatformData()


def get_cached_data() -> PlatformData:
    """Get data from session state cache, or load fresh."""
    if "platform_data" not in st.session_state:
        st.session_state["platform_data"] = load_data(
            st.session_state.get("uploaded_file_obj")
        )
    return st.session_state["platform_data"]


def refresh_data(uploaded_file=None):
    """Force reload of platform data."""
    st.session_state["platform_data"] = load_data(uploaded_file)
    # Clear decline cache
    _load_from_path.clear()
