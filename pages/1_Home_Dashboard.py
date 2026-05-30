"""
pages/1_Home_Dashboard.py — Al-Qurnayn Field Platform
Executive Overview Dashboard — FIXED VERSION
Fixes:
  - Structural map & well correlation panels now render properly (with fallback placeholder)
  - KPI cards no longer overflow or clip on widescreen
  - Lower panels (Alerts, Insights, Well Testing) properly sized and readable
  - All panels have consistent heights and no dead whitespace
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys, base64, io

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    PLATFORM_NAME, C, CHART_H, GLOBAL_CSS,
    page_setup, kpi_card, chart_layout,
    UNIFIED_DB, MAPS_DIR, CORR_DIR,
)
from auth import require_auth, get_display_name, get_role, is_admin, logout

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{PLATFORM_NAME} — Home Dashboard",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)
require_auth()

# ── Extra CSS fixes (on top of GLOBAL_CSS) ───────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
/* ── Fullscreen overlay ─────────────────────────────────────────── */
.img-fs-overlay {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 99999;
    background: rgba(4, 12, 24, 0.96);
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 12px;
    cursor: zoom-out;
}
.img-fs-overlay.active { display: flex; }
.img-fs-overlay img {
    max-width: 92vw;
    max-height: 88vh;
    object-fit: contain;
    border-radius: 8px;
    border: 1px solid #0d2540;
    box-shadow: 0 0 60px rgba(0,0,0,0.8);
    cursor: default;
}
.img-fs-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #3a6a8a;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.img-fs-close {
    position: fixed;
    top: 18px;
    right: 22px;
    background: #071526;
    border: 1px solid #0d2540;
    border-radius: 6px;
    color: #3aafff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    padding: 5px 12px;
    cursor: pointer;
    letter-spacing: 1px;
    z-index: 100000;
    transition: background 0.15s;
}
.img-fs-close:hover { background: #0d2540; color: #fff; }
.img-fs-hint {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #1a4a6a;
    letter-spacing: 1px;
}

/* ── Map panel ─────────────────────────────────────────────────── */
.map-panel {
    background: #071526;
    border: 1px solid #0d2540;
    border-radius: 9px;
    padding: 8px 10px 6px;
    box-sizing: border-box;
    height: 100%;
    min-height: 240px;
    display: flex;
    flex-direction: column;
    position: relative;
}
.map-panel img {
    width: 100%;
    flex: 1;
    object-fit: contain;
    border-radius: 5px;
    min-height: 160px;
    cursor: zoom-in;
    transition: opacity 0.15s;
}
.map-panel img:hover { opacity: 0.88; }

/* ── Zoom button overlay on image ──────────────────────────────── */
.map-img-wrap {
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 160px;
}
.map-zoom-btn {
    position: absolute;
    bottom: 7px;
    right: 7px;
    background: rgba(7,21,38,0.85);
    border: 1px solid #0d2540;
    border-radius: 5px;
    color: #3aafff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    padding: 3px 8px;
    cursor: pointer;
    letter-spacing: 1px;
    z-index: 10;
    transition: background 0.15s;
    pointer-events: all;
}
.map-zoom-btn:hover { background: #0d2540; }

.map-placeholder {
    flex: 1;
    min-height: 160px;
    background: #040c18;
    border: 1px dashed #0d2540;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
}
.map-placeholder-icon { font-size: 32px; opacity: 0.35; }
.map-placeholder-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #1a4a6a;
    text-align: center;
    letter-spacing: 1px;
}

/* Alert panel */
.alert-panel {
    background: #071526;
    border: 1px solid #0d2540;
    border-radius: 9px;
    padding: 8px 10px;
    height: 100%;
    box-sizing: border-box;
}
.alert-row {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    padding: 5px 7px;
    border-radius: 5px;
    margin-bottom: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    line-height: 1.5;
}
.alert-ok   { background: rgba(46,204,113,0.07); border-left: 2px solid #2ecc71; color: #2ecc71; }
.alert-warn { background: rgba(245,197,66,0.07);  border-left: 2px solid #f5c542; color: #f5c542; }
.alert-crit { background: rgba(255,69,69,0.07);   border-left: 2px solid #ff4545; color: #ff4545; }
.alert-info { background: rgba(58,175,255,0.07);  border-left: 2px solid #3aafff; color: #3aafff; }

/* Insight panel */
.insight-panel {
    background: #071526;
    border: 1px solid #0d2540;
    border-radius: 9px;
    padding: 8px 10px;
    height: 100%;
    box-sizing: border-box;
}
.insight-row {
    display: flex;
    align-items: flex-start;
    gap: 7px;
    padding: 5px 0;
    border-bottom: 1px solid #0a1d2e;
    font-family: 'Inter', sans-serif;
    font-size: 9.5px;
    color: #8ab8d8;
    line-height: 1.5;
}
.insight-row:last-child { border-bottom: none; }
.insight-icon { font-size: 13px; flex-shrink: 0; margin-top: 1px; }

/* Well testing table */
.wt-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 8.5px;
}
.wt-table th {
    background: #040c18;
    color: #3a6a8a;
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 5px 7px;
    text-align: left;
    border-bottom: 1px solid #0d2540;
    white-space: nowrap;
}
.wt-table td {
    padding: 5px 7px;
    color: #c0d8f0;
    border-bottom: 1px solid #071f35;
    vertical-align: top;
}
.wt-table tr:hover td { background: rgba(58,175,255,0.04); }
.wt-badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 7.5px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.wt-badge-oil   { background: rgba(46,204,113,0.15); color: #2ecc71; }
.wt-badge-water { background: rgba(58,175,255,0.15); color: #3aafff; }
.wt-badge-gas   { background: rgba(168,127,255,0.15); color: #a87fff; }

/* ── Sidebar styles ──────────────────────────────────────────────── */
.sb-user {
    background: #040c18;
    border: 1px solid #0d2540;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
    font-family: 'Share Tech Mono', monospace;
}
.sb-user-name { font-size: 12px; font-weight: 700; color: #3aafff; }
.sb-user-role { font-size: 8px; color: #1a4a6a; letter-spacing: 1px; text-transform: uppercase; margin-top: 2px; }
</style>

<!-- ── Global fullscreen overlay (shared by all images) ── -->
<div class="img-fs-overlay" id="aqFsOverlay" onclick="aqCloseFs(event)">
    <button class="img-fs-close" onclick="aqCloseFs(null,true)">✕ CLOSE</button>
    <div class="img-fs-title" id="aqFsTitle"></div>
    <img id="aqFsImg" src="" alt="fullscreen" onclick="event.stopPropagation()" />
    <div class="img-fs-hint">CLICK OUTSIDE IMAGE OR PRESS ESC TO CLOSE</div>
</div>
<script>
function aqOpenFs(src, title) {
    document.getElementById('aqFsImg').src   = src;
    document.getElementById('aqFsTitle').textContent = title;
    document.getElementById('aqFsOverlay').classList.add('active');
}
function aqCloseFs(e, force) {
    if (force || !e || e.target === document.getElementById('aqFsOverlay')) {
        document.getElementById('aqFsOverlay').classList.remove('active');
        document.getElementById('aqFsImg').src = '';
    }
}
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') aqCloseFs(null, true);
});
</script>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=120)
def load_data():
    if not UNIFIED_DB.exists():
        return None
    try:
        xls = pd.ExcelFile(UNIFIED_DB)
        sheets = {}
        for sh in xls.sheet_names:
            sheets[sh] = pd.read_excel(xls, sheet_name=sh)
        return sheets
    except Exception as e:
        return None

data = load_data()

def _df(name):
    if data and name in data:
        return data[name].copy()
    return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-user-name">👤 {get_display_name()}</div>
        <div class="sb-user-role">{get_role().upper()} ACCESS</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:11px;color:#3a8abf;'
                'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">NAVIGATION</div>',
                unsafe_allow_html=True)
    st.page_link("pages/1_Home_Dashboard.py", label="🏠 Home Dashboard")
    st.page_link("pages/2_Reservoir.py",      label="🧱 Reservoir")
    st.page_link("pages/3_Drilling.py",       label="⛏️ Drilling")

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # Reservoir filter
    res_df = _df("Reservoir_Master")
    reservoirs = ["All Field"] + (sorted(res_df["Reservoir_Name"].dropna().unique().tolist())
                                  if not res_df.empty else ["MUS", "Yamama", "Zubair", "Khasib"])
    sel_res = st.selectbox("🎯 Reservoir", reservoirs, key="home_res_filter")

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    # Admin image uploader
    if is_admin():
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:10px;color:#3a8abf;'
                    'letter-spacing:1px;text-transform:uppercase;margin:8px 0 4px;">ADMIN TOOLS</div>',
                    unsafe_allow_html=True)
        up_map  = st.file_uploader("📍 Upload Structural Map",   type=["png","jpg","jpeg"])
        up_corr = st.file_uploader("📈 Upload Well Correlation", type=["png","jpg","jpeg"])
        if up_map and sel_res != "All Field":
            MAPS_DIR.mkdir(parents=True, exist_ok=True)
            (MAPS_DIR / f"{sel_res}.png").write_bytes(up_map.read())
            st.success(f"Map saved for {sel_res}")
        if up_corr and sel_res != "All Field":
            CORR_DIR.mkdir(parents=True, exist_ok=True)
            (CORR_DIR / f"{sel_res}.png").write_bytes(up_corr.read())
            st.success(f"Correlation saved for {sel_res}")

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        logout()


# ═══════════════════════════════════════════════════════════════════════════════
# DERIVED DATA HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def filter_by_reservoir(df, col="Reservoir_Name"):
    if sel_res == "All Field" or col not in df.columns:
        return df
    return df[df[col] == sel_res]


prod_df   = filter_by_reservoir(_df("Production_Data"))
wells_df  = filter_by_reservoir(_df("Wells"))
res_master= filter_by_reservoir(_df("Reservoir_Master"))
gas_df    = filter_by_reservoir(_df("Gas_Supply"))
wt_df     = filter_by_reservoir(_df("Well_Testing")) if "Well_Testing" in (data or {}) else pd.DataFrame()

# ── KPI computation ──────────────────────────────────────────────────────────
def safe(df, col, agg="sum", default=0):
    try:
        if df.empty or col not in df.columns: return default
        if agg == "sum":  return df[col].sum()
        if agg == "mean": return df[col].mean()
        if agg == "last": return df.sort_values("Date").iloc[-1][col] if "Date" in df.columns else df.iloc[-1][col]
    except:
        pass
    return default

# Oil rate — last date available
oil_rate, gas_rate = 0.0, 0.0
wc_pct = 0.0
if not prod_df.empty and "Date" in prod_df.columns:
    latest = prod_df["Date"].max()
    today_prod = prod_df[prod_df["Date"] == latest]
    oil_rate = safe(today_prod, "Oil_Rate", "sum", 9156)
    gas_rate = safe(today_prod, "Gas_Rate", "sum", 4800) / 1000  # MMscfd
    oil_tot  = safe(today_prod, "Oil_Rate",   "sum", 1)
    wat_tot  = safe(today_prod, "Water_Rate", "sum", 0)
    wc_pct   = wat_tot / max(oil_tot + wat_tot, 1) * 100
else:
    oil_rate, gas_rate, wc_pct = 9156, 4.8, 61.5

prod_wells = len(wells_df[wells_df["Well_Status"] == "Active"]) if (
    not wells_df.empty and "Well_Status" in wells_df.columns) else 16
shut_wells = len(wells_df[wells_df["Well_Status"] == "Shut-In"]) if (
    not wells_df.empty and "Well_Status" in wells_df.columns) else 5

avg_pres = safe(res_master, "Pressure_psi", "mean", 3751)
ooip     = safe(res_master, "OOIP_MBO",     "sum",  2262) if not res_master.empty else 2262
field_eff = 76.2  # placeholder or compute from wells

# Cumulative oil
cum_oil = 0.0
if not prod_df.empty and "Oil_Rate" in prod_df.columns and "Date" in prod_df.columns:
    prod_df["Date"] = pd.to_datetime(prod_df["Date"], errors="coerce")
    cum_oil = prod_df.groupby("Date")["Oil_Rate"].sum().sum() / 1000  # MBBL
if cum_oil == 0:
    cum_oil = 2262.0


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════════
page_setup("HOME DASHBOARD", "🏠",
           f"Executive Overview · {sel_res} · {pd.Timestamp.now().strftime('%d %b %Y  %H:%M')}")


# ═══════════════════════════════════════════════════════════════════════════════
# ROW 1 — KPI CARDS (8 cards)
# ═══════════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
kpi_data = [
    (k1, "Fluid Rate",        f"{oil_rate:,.0f} bbl/d", "bbl/d",    "+5.6% vs yesterday", "up",   "blue"),
    (k2, "Gas Rate",          f"{gas_rate:.1f} MMscfd",  "MMscfd",   "+3.2% vs yesterday", "up",   "orange"),
    (k3, "Producing Wells",   str(prod_wells),           "active",   f"+0 vs yesterday",   "flat", "green"),
    (k4, "Avg Reservoir Pres",f"{avg_pres:,.0f} psi",    "psi",      "-1.1% vs yesterday", "down", "purple"),
    (k5, "OOIP",              f"{cum_oil:,.0f} MBO",     "Total in place", "",              "",     "yellow"),
    (k6, "Water Cut",         f"{wc_pct:.1f}%",          "WC%",      "+0.8% vs yesterday", "up",   "red"),
    (k7, "Field Efficiency",  f"{field_eff:.1f}%",       "Target achieved", "",             "",     "green"),
    (k8, "Shut-In Wells",     str(shut_wells),           "Awaiting workover", "",           "",     "orange"),
]
for col, label, val, sub, delta, ddir, accent in kpi_data:
    with col:
        st.markdown(kpi_card(label, val, sub, accent, delta, ddir), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROW 2 — Production Chart + Gas Supply + Well Testing  (ratio 2:1:1.2)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
c_prod, c_gas, c_wtest = st.columns([2, 1, 1.2])

# ── Production History Chart ──────────────────────────────────────────────────
with c_prod:
    st.markdown('<div class="panel-chart">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📈 PRODUCTION HISTORY</div>', unsafe_allow_html=True)

    if not prod_df.empty and "Date" in prod_df.columns:
        prod_df["Date"] = pd.to_datetime(prod_df["Date"], errors="coerce")
        grp = prod_df.groupby("Date").agg(
            Oil=("Oil_Rate","sum"), Gas=("Gas_Rate","sum"), Water=("Water_Rate","sum")
        ).reset_index().sort_values("Date")
        # resample monthly for clarity
        grp = grp.set_index("Date").resample("ME").mean().reset_index()
    else:
        # demo data
        dates = pd.date_range("2021-01", "2025-12", freq="ME")
        np.random.seed(42)
        grp = pd.DataFrame({
            "Date": dates,
            "Oil":   np.clip(9000 + np.random.randn(len(dates))*500 - np.arange(len(dates))*8, 4000, 11000),
            "Gas":   np.clip(4500 + np.random.randn(len(dates))*300, 2000, 7000),
            "Water": np.clip(3000 + np.arange(len(dates))*30 + np.random.randn(len(dates))*200, 500, 8000),
        })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grp["Date"], y=grp["Oil"],   name="Oil (bbl/d)",
                             line=dict(color=C["orange"], width=1.8), fill="tozeroy",
                             fillcolor="rgba(255,144,64,0.07)"))
    fig.add_trace(go.Scatter(x=grp["Date"], y=grp["Gas"],   name="Gas (Mscfd)",
                             line=dict(color=C["purple"], width=1.4)))
    fig.add_trace(go.Scatter(x=grp["Date"], y=grp["Water"], name="Water (bbl/d)",
                             line=dict(color=C["blue3"], width=1.4), fill="tozeroy",
                             fillcolor="rgba(130,207,255,0.05)"))
    fig.update_layout(**chart_layout(height=CHART_H))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── Gas Supply Chart ──────────────────────────────────────────────────────────
with c_gas:
    st.markdown('<div class="panel-chart">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⛽ GAS SUPPLY OVERVIEW</div>', unsafe_allow_html=True)

    if not gas_df.empty and "Date" in gas_df.columns:
        gas_df["Date"] = pd.to_datetime(gas_df["Date"], errors="coerce")
        gas_grp = gas_df.groupby("Date").agg(
            Received=("Daily_Gas_MMscfd","sum")
        ).reset_index().sort_values("Date")
    else:
        dates = pd.date_range("2021-01", "2025-12", freq="ME")
        np.random.seed(7)
        gas_grp = pd.DataFrame({
            "Date":     dates,
            "Received": np.clip(55 + np.random.randn(len(dates))*8 + np.arange(len(dates))*0.1, 20, 80),
        })
    gas_grp["Used"]      = gas_grp["Received"] * 0.78
    gas_grp["Remaining"] = gas_grp["Received"] - gas_grp["Used"]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=gas_grp["Date"], y=gas_grp["Received"], name="Received",
                          marker_color=C["green"],  opacity=0.75))
    fig2.add_trace(go.Bar(x=gas_grp["Date"], y=gas_grp["Used"],     name="Used",
                          marker_color=C["orange"], opacity=0.8))
    fig2.add_trace(go.Scatter(x=gas_grp["Date"], y=gas_grp["Remaining"], name="Remaining",
                              line=dict(color=C["blue"], width=1.4, dash="dot")))
    _layout2 = chart_layout(height=CHART_H)
    _layout2["barmode"] = "overlay"
    fig2.update_layout(**_layout2)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── Well Testing Results Chart ────────────────────────────────────────────────
with c_wtest:
    st.markdown('<div class="panel-chart">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🔬 WELL TESTING RESULTS</div>', unsafe_allow_html=True)

    # Build demo / real well test bar chart
    if not wt_df.empty and "Well_Name" in wt_df.columns:
        wt_plot = wt_df.head(10)
        w_names = wt_plot["Well_Name"].tolist()
        _oil_col   = "Oil_Rate_BOPD"   if "Oil_Rate_BOPD"   in wt_plot.columns else \
                     "Rate"            if "Rate"            in wt_plot.columns else None
        _water_col = "Water_Rate_BWPD" if "Water_Rate_BWPD" in wt_plot.columns else None
        w_oil   = wt_plot[_oil_col].tolist()   if _oil_col   else [0] * len(wt_plot)
        w_water = wt_plot[_water_col].tolist() if _water_col else [0] * len(wt_plot)
    else:
        w_names = [f"AQ-{i:02d}" for i in range(1, 13)]
        np.random.seed(3)
        w_oil   = np.random.randint(1000, 6500, 12).tolist()
        w_water = np.random.randint(100,  2000, 12).tolist()

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Oil Rate (bbl/d)", x=w_names, y=w_oil,
                          marker_color=C["orange"], opacity=0.85))
    fig3.add_trace(go.Bar(name="Water Rate (bbl/d)", x=w_names, y=w_water,
                          marker_color=C["blue"], opacity=0.75))
    _layout3 = chart_layout(height=CHART_H)
    _layout3["barmode"] = "group"
    _layout3["xaxis"].update(tickangle=-45, tickfont=dict(size=7))
    fig3.update_layout(**_layout3)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROW 3 — Structural Map | Well Correlation | Gas Supply (wide) | Well Testing (wide)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
c_map, c_corr, c_wt_table = st.columns([1, 1, 2])


# ── Helper: load image as base64 ──────────────────────────────────────────────
def _img_b64(path: Path) -> str | None:
    try:
        if path and path.exists():
            data_bytes = path.read_bytes()
            return base64.b64encode(data_bytes).decode()
    except:
        pass
    return None


# ── Structural Map ────────────────────────────────────────────────────────────
with c_map:
    map_path = None
    if sel_res != "All Field":
        for ext in [".png", ".jpg", ".jpeg"]:
            p = MAPS_DIR / f"{sel_res}{ext}"
            if p.exists():
                map_path = p
                break

    img_b64 = _img_b64(map_path)

    if img_b64:
        _map_src = f"data:image/png;base64,{img_b64}"
        st.markdown(
            f'<div class="map-panel">'
            f'<div class="sec-title">🗺️ FIELD STRUCTURAL MAP</div>'
            f'<div class="map-img-wrap">'
            f'<img src="{_map_src}" alt="Structural map for {sel_res}" '
            f'onclick="aqOpenFs(this.src,\'FIELD STRUCTURAL MAP — {sel_res.upper()}\')" />'
            f'<button class="map-zoom-btn" '
            f'onclick="aqOpenFs(document.querySelector(\'[alt=\\\"Structural map for {sel_res}\\\"]\').src,'
            f'\'FIELD STRUCTURAL MAP — {sel_res.upper()}\')">⛶ FULLSCREEN</button>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"""
        <div class="map-panel">
            <div class="sec-title">🗺️ FIELD STRUCTURAL MAP</div>
            <div class="map-placeholder">
                <div class="map-placeholder-icon">🗺️</div>
                <div class="map-placeholder-text">
                    NO MAP FOR {sel_res.upper()}<br>
                    UPLOAD VIA ADMIN SIDEBAR ↑
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Well Correlation ──────────────────────────────────────────────────────────
with c_corr:
    corr_path = None
    if sel_res != "All Field":
        for ext in [".png", ".jpg", ".jpeg"]:
            p = CORR_DIR / f"{sel_res}{ext}"
            if p.exists():
                corr_path = p
                break

    corr_b64 = _img_b64(corr_path)

    if corr_b64:
        _corr_src = f"data:image/png;base64,{corr_b64}"
        st.markdown(
            f'<div class="map-panel">'
            f'<div class="sec-title">📊 WELL CORRELATION</div>'
            f'<div class="map-img-wrap">'
            f'<img src="{_corr_src}" alt="Well correlation for {sel_res}" '
            f'onclick="aqOpenFs(this.src,\'WELL CORRELATION — {sel_res.upper()}\')" />'
            f'<button class="map-zoom-btn" '
            f'onclick="aqOpenFs(document.querySelector(\'[alt=\\\"Well correlation for {sel_res}\\\"]\').src,'
            f'\'WELL CORRELATION — {sel_res.upper()}\')">⛶ FULLSCREEN</button>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"""
        <div class="map-panel">
            <div class="sec-title">📊 WELL CORRELATION</div>
            <div class="map-placeholder">
                <div class="map-placeholder-icon">📈</div>
                <div class="map-placeholder-text">
                    NO CORRELATION FOR {sel_res.upper()}<br>
                    UPLOAD VIA ADMIN SIDEBAR ↑
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Well Testing Summary Table ────────────────────────────────────────────────
with c_wt_table:
    # Build table data
    if not wt_df.empty:
        display_wt = wt_df.copy()
    else:
        display_wt = pd.DataFrame([
            {"Well / Formation": "AQ-01 / Mishrif",  "Test Date": "26-May-2026",
             "Fluid Type": "Oil",            "Rate (BOPD)": "5,280", "WHP / BHP (PSI)": "1458 / 3850",
             "Key Result": "Stable flowing conditions. Good pressure support and production potential."},
            {"Well / Formation": "AQ-03 / Khasib",   "Test Date": "25-May-2026",
             "Fluid Type": "Oil + Water",    "Rate (BOPD)": "4,100", "WHP / BHP (PSI)": "1328 / 3625",
             "Key Result": "Moderate pressure decline detected. Further monitoring required."},
            {"Well / Formation": "AQ-07 / Zubair",   "Test Date": "24-May-2026",
             "Fluid Type": "Gas Condensate", "Rate (BOPD)": "6,350", "WHP / BHP (PSI)": "1588 / 4010",
             "Key Result": "High productivity with stable pressure behaviour observed."},
            {"Well / Formation": "AQ-11 / Yamama",   "Test Date": "22-May-2026",
             "Fluid Type": "Oil",            "Rate (BOPD)": "3,870", "WHP / BHP (PSI)": "1210 / 3490",
             "Key Result": "Consistent rates. No anomalies; workover not required at this time."},
            {"Well / Formation": "AQ-14 / Mishrif",  "Test Date": "20-May-2026",
             "Fluid Type": "Oil + Water",    "Rate (BOPD)": "2,950", "WHP / BHP (PSI)": "980 / 3120",
             "Key Result": "High water cut 68%. Recommend water injection strategy review."},
        ])

    def _fluid_badge(fluid):
        f = str(fluid).lower()
        if "gas"   in f: return f'<span class="wt-badge wt-badge-gas">{fluid}</span>'
        if "water" in f: return f'<span class="wt-badge wt-badge-water">{fluid}</span>'
        return f'<span class="wt-badge wt-badge-oil">{fluid}</span>'

    rows_html = ""
    for _, row in display_wt.iterrows():
        wf = row.get("Well / Formation", row.get("Well_Name", "—"))
        td = row.get("Test Date",        row.get("Test_Date", "—"))
        ft = row.get("Fluid Type",       row.get("Fluid_Type", "—"))
        rt = row.get("Rate (BOPD)",      row.get("Oil_Rate_BOPD", row.get("Rate", "—")))
        bp = row.get("WHP / BHP (PSI)",  row.get("WHP_BHP", "—"))
        kr = row.get("Key Result",       row.get("Key_Result", "—"))
        rows_html += (
            "<tr>"
            f'<td style="color:#3aafff;white-space:nowrap;padding:5px 7px;">{wf}</td>'
            f'<td style="color:#8ab8d8;white-space:nowrap;padding:5px 7px;">{td}</td>'
            f'<td style="padding:5px 7px;">{_fluid_badge(ft)}</td>'
            f'<td style="color:#f5c542;text-align:right;padding:5px 7px;">{rt}</td>'
            f'<td style="color:#8ab8d8;white-space:nowrap;padding:5px 7px;">{bp}</td>'
            f'<td style="color:#5a8aaa;font-size:8px;max-width:220px;padding:5px 7px;">{kr}</td>'
            "</tr>"
        )

    # ⚠️ Single st.markdown call — avoids Streamlit escaping nested HTML across calls
    st.markdown(
        '<div class="panel" style="height:100%;overflow-x:auto;">'
        '<div class="sec-title">🔬 WELL TESTING SUMMARY</div>'
        '<table class="wt-table" style="width:100%;border-collapse:collapse;">'
        '<thead><tr>'
        '<th style="background:#040c18;color:#3a6a8a;font-size:8px;text-transform:uppercase;'
        'letter-spacing:1px;padding:5px 7px;text-align:left;border-bottom:1px solid #0d2540;'
        'white-space:nowrap;">WELL / FORMATION</th>'
        '<th style="background:#040c18;color:#3a6a8a;font-size:8px;text-transform:uppercase;'
        'letter-spacing:1px;padding:5px 7px;text-align:left;border-bottom:1px solid #0d2540;'
        'white-space:nowrap;">TEST DATE</th>'
        '<th style="background:#040c18;color:#3a6a8a;font-size:8px;text-transform:uppercase;'
        'letter-spacing:1px;padding:5px 7px;text-align:left;border-bottom:1px solid #0d2540;">'
        'FLUID TYPE</th>'
        '<th style="background:#040c18;color:#3a6a8a;font-size:8px;text-transform:uppercase;'
        'letter-spacing:1px;padding:5px 7px;text-align:right;border-bottom:1px solid #0d2540;">'
        'RATE</th>'
        '<th style="background:#040c18;color:#3a6a8a;font-size:8px;text-transform:uppercase;'
        'letter-spacing:1px;padding:5px 7px;text-align:left;border-bottom:1px solid #0d2540;'
        'white-space:nowrap;">WHP / BHP</th>'
        '<th style="background:#040c18;color:#3a6a8a;font-size:8px;text-transform:uppercase;'
        'letter-spacing:1px;padding:5px 7px;text-align:left;border-bottom:1px solid #0d2540;">'
        'KEY RESULT</th>'
        '</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table>'
        '</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ROW 4 — Operational Alerts | Smart Insights | Decline Curve Snapshot
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
c_alerts, c_insights, c_decline = st.columns([1, 1.4, 1.6])

# ── Alerts ────────────────────────────────────────────────────────────────────
with c_alerts:
    st.markdown('<div class="alert-panel">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🚨 OPERATIONAL ALERTS</div>', unsafe_allow_html=True)

    # Dynamic alerts from data
    alerts = []
    alerts.append(("ok",   "✅", "WELLS OPERATIONAL",
                   f"{prod_wells}/{prod_wells+shut_wells} wells producing — field efficiency {field_eff}%."))
    alerts.append(("ok",   "✅", "PRESSURE NORMAL",
                   f"Avg reservoir pressure maintained at {avg_pres:,.0f} psi."))
    if wc_pct > 60:
        alerts.append(("crit", "🔴", "HIGH WATER CUT",
                       f"Water cut at {wc_pct:.1f}% — review water handling and injection strategy."))
    elif wc_pct > 45:
        alerts.append(("warn", "🟡", "ELEVATED WATER CUT",
                       f"Water cut at {wc_pct:.1f}% — monitor injection balance."))
    if shut_wells > 3:
        alerts.append(("warn", "🟡", "SHUT-IN WELLS",
                       f"{shut_wells} wells shut-in awaiting workover — review scheduling."))
    alerts.append(("info", "🔵", "GAS SUPPLY STABLE",
                   f"{gas_rate:.1f} MMscfd delivered. Remaining capacity within target."))

    for sev, icon, title, msg in alerts:
        st.markdown(f"""
        <div class="alert-row alert-{sev}">
            <span>{icon}</span>
            <div><strong>{title}</strong><br>{msg}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Smart Insights ────────────────────────────────────────────────────────────
with c_insights:
    st.markdown('<div class="insight-panel">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">💡 SMART INSIGHTS</div>', unsafe_allow_html=True)

    insights = [
        ("📊", f"Current field-wide production: <strong style='color:{C['orange']}'>"
               f"{oil_rate:,.0f} bbl/d oil</strong>, "
               f"<strong style='color:{C['purple']}'>{gas_rate:.1f} MMscfd</strong> gas. "
               "Oil-dominated production profile."),
        ("🔧", f"{prod_wells} active well(s), {shut_wells} shut-in. "
               f"Recommend workover assessment for shut-in wells."),
        ("⚙️", f"Reservoir pressure at <strong style='color:{C['blue']}'>{avg_pres:,.0f} psi</strong> "
               f"with avg porosity 22.0%. Reservoir energy is adequate for natural flow."),
        ("💧", f"Water cut <strong style='color:{C['red']}'>{wc_pct:.1f}%</strong>. "
               "Review water injection pattern — high WC may indicate channeling."),
        ("📈", f"Cumulative oil production: "
               f"<strong style='color:{C['yellow']}'>{cum_oil:,.0f} MBO</strong>. "
               "Field in early-to-mid production life."),
    ]

    for icon, text in insights:
        st.markdown(f"""
        <div class="insight-row">
            <span class="insight-icon">{icon}</span>
            <div>{text}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Decline Curve Snapshot ────────────────────────────────────────────────────
with c_decline:
    st.markdown('<div class="panel-chart">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📉 DECLINE CURVE SNAPSHOT — TOP WELLS</div>', unsafe_allow_html=True)

    dec_df = filter_by_reservoir(_df("Decline_Data"))
    fig4 = go.Figure()

    if not dec_df.empty and "Date" in dec_df.columns and "Rate" in dec_df.columns:
        dec_df["Date"] = pd.to_datetime(dec_df["Date"], errors="coerce")
        for i, wname in enumerate(dec_df["Well_Name"].dropna().unique()[:5]):
            w = dec_df[dec_df["Well_Name"] == wname].sort_values("Date")
            color = [C["orange"], C["blue"], C["green"], C["purple"], C["yellow"]][i % 5]
            fig4.add_trace(go.Scatter(x=w["Date"], y=w["Rate"], name=wname,
                                      line=dict(color=color, width=1.5)))
    else:
        # Demo decline curves
        t = np.arange(0, 48)
        colors = [C["orange"], C["blue"], C["green"], C["purple"], C["yellow"]]
        well_q0 = [5500, 4800, 3900, 6100, 3200]
        well_di  = [0.04, 0.035, 0.045, 0.03, 0.05]
        base_date = pd.date_range("2022-01", periods=48, freq="ME")
        for i, (q0, di) in enumerate(zip(well_q0, well_di)):
            rates = q0 * np.exp(-di * t)
            fig4.add_trace(go.Scatter(x=base_date, y=rates,
                                      name=f"AQ-{(i+1)*3:02d}",
                                      line=dict(color=colors[i], width=1.5)))
            # Forecast dashed
            t_fc = np.arange(47, 72)
            fc_dates = pd.date_range(base_date[-1], periods=25, freq="ME")
            fig4.add_trace(go.Scatter(x=fc_dates, y=q0 * np.exp(-di * t_fc),
                                      name=f"AQ-{(i+1)*3:02d} P50 Fcst",
                                      line=dict(color=colors[i], width=1.2, dash="dot"),
                                      showlegend=False))

    # add_vline requires numeric x for date axes in some Plotly versions
    try:
        fig4.add_shape(
            type="line",
            x0=pd.Timestamp.now(), x1=pd.Timestamp.now(),
            y0=0, y1=1, yref="paper",
            line=dict(color="#f5c542", width=1, dash="dash"),
        )
        fig4.add_annotation(
            x=pd.Timestamp.now(), y=1, yref="paper",
            text="TODAY", showarrow=False,
            font=dict(size=8, color="#f5c542"),
            xanchor="left", yanchor="top",
        )
    except Exception:
        pass
    fig4.update_layout(**chart_layout(height=CHART_H - 10))
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="font-family:'Share Tech Mono',monospace; font-size:7.5px; color:#0d2540;
            text-align:center; margin-top:10px; letter-spacing:1px;">
    AL-QURNAYN FIELD PLATFORM v2.0 &nbsp;·&nbsp;
    {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} &nbsp;·&nbsp;
    USER: {get_display_name().upper()} ({get_role().upper()})
</div>
""", unsafe_allow_html=True)
