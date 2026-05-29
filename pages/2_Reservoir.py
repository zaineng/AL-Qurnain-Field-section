"""
pages/2_Reservoir.py — Advanced Reservoir Analytics Interface
"""
import streamlit as st
from pathlib import Path
import base64
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PLATFORM_NAME, GLOBAL_CSS, C, PRESS_DIR
from auth import require_auth, logout, get_display_name, is_admin
from modules.excel_loader import get_cached_data, refresh_data
from modules.reservoir_filters import render_sidebar_filters, apply_filters, get_dynamic_image_path, get_filter_badge
from modules.smart_kpis import calc_kpis, render_reservoir_summary_cards
from modules.charts import (fig_pressure_map, fig_fluid_contacts,
                             fig_production_trend, fig_production_by_layer,
                             fig_structural_map_plotly)
from modules.decline_analysis import fit_decline, decline_summary_html
from modules.charts import fig_decline_curve

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{PLATFORM_NAME} — Reservoir",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
require_auth()

data = get_cached_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div class="sidebar-logo">'
        f'<div style="font-size:28px">🛢️</div>'
        f'<div class="sidebar-logo-title">{PLATFORM_NAME}</div>'
        f'<div class="sidebar-logo-sub">RESERVOIR & DRILLING INTELLIGENCE</div>'
        f'</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">📄 NAVIGATION</div>', unsafe_allow_html=True)
    st.page_link("pages/1_Home_Dashboard.py", label="🏠 Home Dashboard")
    st.page_link("pages/2_Reservoir.py",      label="🧪 Reservoir")
    st.page_link("pages/3_Drilling.py",       label="⚙️ Drilling")
    st.divider()

    reservoir, well = render_sidebar_filters(data)
    st.divider()

    if is_admin():
        st.markdown('<div class="sidebar-section">📤 DATA</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload unified_database.xlsx", type=["xlsx"],
                                     key="res_upload", label_visibility="collapsed")
        if uploaded:
            refresh_data(uploaded)
            st.success("✅ Data refreshed")
            st.rerun()

        st.markdown('<div class="sidebar-section">🖼️ PRESSURE MAP</div>', unsafe_allow_html=True)
        rsv_tag = reservoir.replace(" ","_") if reservoir != "Show All" else "default"
        pm_up = st.file_uploader(f"Pressure Map ({rsv_tag})", type=["png","jpg","jpeg"],
                                  key="pm_up", label_visibility="collapsed")
        if pm_up:
            PRESS_DIR.mkdir(parents=True, exist_ok=True)
            (PRESS_DIR / f"{rsv_tag}.png").write_bytes(pm_up.read())
            st.success("Pressure map saved")
        st.divider()

    st.markdown(
        f'<div style="font-family:Share Tech Mono,monospace; font-size:8px; color:#1a4a6a;">'
        f'👤 {get_display_name()} &nbsp;·&nbsp; {st.session_state.get("role","").upper()}</div>',
        unsafe_allow_html=True)
    if st.button("⏻ Logout", key="logout_res"):
        logout()


# ── Page header ───────────────────────────────────────────────────────────────
badge = get_filter_badge(reservoir, well)
st.markdown(
    f'<div class="page-header">'
    f'<div class="page-header-icon">🧪</div>'
    f'<div><div class="page-header-title">RESERVOIR INTERFACE</div>'
    f'<div class="page-header-sub">ADVANCED RESERVOIR ANALYTICS &nbsp;·&nbsp; {badge}</div></div>'
    f'</div>', unsafe_allow_html=True)

# ── Filter data ───────────────────────────────────────────────────────────────
res_df, wells_df, prod_df, dec_df, contacts_df, layers_df, gas_df = apply_filters(data, reservoir, well)

# ── Reservoir KPI cards ───────────────────────────────────────────────────────
render_reservoir_summary_cards(res_df, wells_df)
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# ── Helper: load image ────────────────────────────────────────────────────────
def _img_src(path: Path) -> str | None:
    if path and Path(path).exists():
        ext = Path(path).suffix.lower().lstrip(".")
        mime = "image/jpeg" if ext in ("jpg","jpeg") else f"image/{ext}"
        b64  = base64.b64encode(Path(path).read_bytes()).decode()
        return f"data:{mime};base64,{b64}"
    return None


# ── Global fullscreen overlay (JS-based, no rerun needed) ────────────────────
st.markdown("""
<style>
.img-fs-overlay {
    display: none; position: fixed; inset: 0; z-index: 99999;
    background: rgba(4,12,24,0.96);
    align-items: center; justify-content: center;
    flex-direction: column; gap: 12px; cursor: zoom-out;
}
.img-fs-overlay.active { display: flex; }
.img-fs-overlay img {
    max-width: 92vw; max-height: 88vh; object-fit: contain;
    border-radius: 8px; border: 1px solid #0d2540;
    box-shadow: 0 0 60px rgba(0,0,0,0.8); cursor: default;
}
.img-fs-title {
    font-family: 'Share Tech Mono', monospace; font-size: 10px;
    color: #3a6a8a; letter-spacing: 2px; text-transform: uppercase;
}
.img-fs-close {
    position: fixed; top: 18px; right: 22px;
    background: #071526; border: 1px solid #0d2540; border-radius: 6px;
    color: #3aafff; font-family: 'Share Tech Mono', monospace;
    font-size: 11px; padding: 5px 12px; cursor: pointer;
    letter-spacing: 1px; z-index: 100000; transition: background 0.15s;
}
.img-fs-close:hover { background: #0d2540; color: #fff; }
.img-fs-hint {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px; color: #1a4a6a; letter-spacing: 1px;
}
.rsv-img-wrap { position: relative; }
.rsv-img-wrap img {
    width: 100%; border-radius: 6px; object-fit: contain;
    max-height: 260px; cursor: zoom-in; transition: opacity 0.15s;
    display: block;
}
.rsv-img-wrap img:hover { opacity: 0.88; }
.rsv-zoom-btn {
    position: absolute; bottom: 7px; right: 7px;
    background: rgba(7,21,38,0.85); border: 1px solid #0d2540;
    border-radius: 5px; color: #3aafff;
    font-family: 'Share Tech Mono', monospace; font-size: 9px;
    padding: 3px 8px; cursor: pointer; letter-spacing: 1px;
    transition: background 0.15s;
}
.rsv-zoom-btn:hover { background: #0d2540; }
</style>
<div class="img-fs-overlay" id="rsvFsOverlay" onclick="rsvCloseFs(event)">
    <button class="img-fs-close" onclick="rsvCloseFs(null,true)">✕ CLOSE</button>
    <div class="img-fs-title" id="rsvFsTitle"></div>
    <img id="rsvFsImg" src="" alt="fullscreen" onclick="event.stopPropagation()" />
    <div class="img-fs-hint">CLICK OUTSIDE IMAGE OR PRESS ESC TO CLOSE</div>
</div>
<script>
function rsvOpenFs(src, title) {
    document.getElementById('rsvFsImg').src = src;
    document.getElementById('rsvFsTitle').textContent = title;
    document.getElementById('rsvFsOverlay').classList.add('active');
}
function rsvCloseFs(e, force) {
    if (force || !e || e.target === document.getElementById('rsvFsOverlay')) {
        document.getElementById('rsvFsOverlay').classList.remove('active');
        document.getElementById('rsvFsImg').src = '';
    }
}
document.addEventListener('keydown', function(e){
    if (e.key === 'Escape') rsvCloseFs(null, true);
});
</script>
""", unsafe_allow_html=True)

# ── ROW 1: Pressure Distribution Map | Fluid Contacts ────────────────────────
c1, c2 = st.columns([1, 1], gap="small")

with c1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">A ── Reservoir Pressure Distribution</div>', unsafe_allow_html=True)

    rsv_tag = reservoir.replace(" ","_") if reservoir != "Show All" else "default"
    pm_path = PRESS_DIR / f"{rsv_tag}.png"
    dyn_pm  = get_dynamic_image_path(data.maps, reservoir, "Pressure_Map_Path")
    if dyn_pm and Path(dyn_pm).exists():
        pm_path = Path(dyn_pm)

    pm_src = _img_src(pm_path)
    if pm_src:
        _pm_title = f"RESERVOIR PRESSURE MAP — {reservoir.upper()}"
        st.markdown(
            f'<div class="rsv-img-wrap">'
            f'<img src="{pm_src}" alt="pressure-map" '
            f'onclick="rsvOpenFs(this.src,\'{_pm_title}\')" />'
            f'<button class="rsv-zoom-btn" '
            f'onclick="rsvOpenFs(document.querySelector(\'[alt=\\\"pressure-map\\\"]\').src,\'{_pm_title}\')">⛶ FULLSCREEN</button>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.plotly_chart(fig_pressure_map(res_df, reservoir),
                        use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">B ── Fluid Contacts (GOC / OWC / GWC)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_fluid_contacts(contacts_df),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── ROW 2: Smart Decline Curve Analysis (full width) ──────────────────────────
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="sec-title">C ── Smart Decline Curve Analysis (Auto-Fit)</div>', unsafe_allow_html=True)

# Determine best data source for decline: decline_data sheet OR production
_dec_source = dec_df if not dec_df.empty and "Rate" in dec_df.columns else prod_df
_rate_col   = "Rate" if "Rate" in _dec_source.columns else (
              "Oil_Rate" if "Oil_Rate" in _dec_source.columns else None)
_date_col   = "Date" if "Date" in _dec_source.columns else None

if _rate_col and _date_col and not _dec_source.empty:
    with st.spinner("Fitting decline curves…"):
        decline_res = fit_decline(_dec_source, rate_col=_rate_col,
                                  date_col=_date_col, forecast_months=60)

    col_a, col_b = st.columns([2, 1], gap="small")
    with col_a:
        st.plotly_chart(fig_decline_curve(decline_res),
                        use_container_width=True, config={"displayModeBar": False})
    with col_b:
        st.markdown(decline_summary_html(decline_res), unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        # Fit comparison table
        if decline_res.all_fits:
            rows = ""
            for dtype in ["Exponential", "Harmonic", "Hyperbolic"]:
                if dtype in decline_res.all_fits:
                    r2 = decline_res.all_fits[dtype]["r2"]
                    best_mark = "★" if dtype == decline_res.decline_type else ""
                    color = C["blue"] if dtype == decline_res.decline_type else C["txt3"]
                    rows += (f'<tr><td style="color:{color}">{best_mark} {dtype}</td>'
                             f'<td style="color:{color};text-align:right">{r2:.4f}</td></tr>')
            if rows:
                st.markdown(
                    f'<table class="styled-table" style="width:100%">'
                    f'<thead><tr><th>Decline Type</th><th style="text-align:right">R²</th></tr></thead>'
                    f'<tbody>{rows}</tbody></table>',
                    unsafe_allow_html=True)
else:
    st.markdown(
        f'<div style="padding:40px;text-align:center;color:{C["txt3"]};'
        f'font-family:Share Tech Mono,monospace;font-size:10px;">'
        f'⚠ No decline/production data available.<br>'
        f'<small>Upload Excel with Decline_Data or Production_Data sheet.</small></div>',
        unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── ROW 3: Production Trend | Production by Layer ─────────────────────────────
c3, c4 = st.columns([1.2, 1], gap="small")

with c3:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">D ── Production Trend (Oil / Gas / Water)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_production_trend(prod_df),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">E ── Production by Layer</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_production_by_layer(layers_df),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── ROW 4: Reservoir / Well Data Table ───────────────────────────────────────
with st.expander("📋  Reservoir & Well Data Table", expanded=False):
    tab1, tab2, tab3 = st.tabs(["Reservoir Master", "Wells", "Production Data"])
    with tab1:
        if not res_df.empty:
            st.dataframe(res_df, use_container_width=True, hide_index=True)
        else:
            st.info("No reservoir data for current filter.")
    with tab2:
        if not wells_df.empty:
            st.dataframe(wells_df, use_container_width=True, hide_index=True)
        else:
            st.info("No well data for current filter.")
    with tab3:
        if not prod_df.empty:
            st.dataframe(prod_df.tail(200), use_container_width=True, hide_index=True)
        else:
            st.info("No production data for current filter.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="text-align:center;padding:8px 0 0 0;font-family:Share Tech Mono,monospace;'
    f'font-size:8px;color:{C["txt4"]}">AL-QURNAYN FIELD PLATFORM v2.0 &nbsp;·&nbsp; '
    f'DATA SOURCE: {data.source.upper()}</div>',
    unsafe_allow_html=True)
