"""
config.py — Platform-wide constants, paths, color palette, CSS theme
Optimized for widescreen 1920×1080 / ultrawide — zero wasted vertical space.
"""
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
DATA_DIR      = BASE_DIR / "data"
ASSETS_DIR    = BASE_DIR / "assets"
MAPS_DIR      = ASSETS_DIR / "maps"
CORR_DIR      = ASSETS_DIR / "correlations"
PRESS_DIR     = ASSETS_DIR / "pressure_maps"
LOGOS_DIR     = ASSETS_DIR / "logos"
UNIFIED_DB    = DATA_DIR / "unified_database.xlsx"

# ── Authentication ─────────────────────────────────────────────────────────────
USERS = {
    "admin":    {"password": "admin123",  "role": "admin",    "name": "Administrator"},
    "engineer": {"password": "eng123",    "role": "engineer", "name": "Field Engineer"},
    "viewer":   {"password": "view123",   "role": "viewer",   "name": "Viewer"},
}

# ── Platform meta ──────────────────────────────────────────────────────────────
PLATFORM_NAME     = "Al-Qurnayn Field"
PLATFORM_SUBTITLE = "Reservoir & Drilling Intelligence"
VERSION           = "v2.0"

# ── Color palette ──────────────────────────────────────────────────────────────
C = {
    "bg0":    "#040c18",
    "bg1":    "#071526",
    "bg2":    "#0a1d2e",
    "bg3":    "#0d2540",
    "border": "#0d2540",
    "bdr2":   "#0a1d35",
    "blue":   "#3aafff",
    "blue2":  "#1a8aff",
    "blue3":  "#82cfff",
    "green":  "#2ecc71",
    "orange": "#ff9040",
    "red":    "#ff4545",
    "yellow": "#f5c542",
    "purple": "#a87fff",
    "txt1":   "#e8f4ff",
    "txt2":   "#8ab8d8",
    "txt3":   "#3a6a8a",
    "txt4":   "#1a4a6a",
}

# ── Chart defaults ─────────────────────────────────────────────────────────────
CHART_BG = C["bg1"]
CHART_H  = 260   # Reduced from 310 — fits tighter panels

# ── Decline forecast horizon ───────────────────────────────────────────────────
FORECAST_MONTHS = 60

# ── Global CSS (injected on every page) ───────────────────────────────────────
# DESIGN PRINCIPLE: Every pixel of vertical space must earn its place.
# Layout strategy: 8px base unit, 4px micro-gap, 0 wasted containers.
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Inter:wght@400;500;600&display=swap');

/* ═══════════════════════════════════════════════
   RESET — eliminate ALL Streamlit default bloat
   ═══════════════════════════════════════════════ */
html, body {
    background: #040c18 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Kill ALL Streamlit spacing injection points */
[data-testid="stAppViewContainer"] {
    background: #040c18 !important;
    padding: 0 !important;
}
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"] {
    padding-top: 0.3rem !important;
    padding-bottom: 0.3rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
    max-width: 100% !important;
}
.block-container {
    padding: 0.3rem 0.8rem 0.5rem 0.8rem !important;
    max-width: 100% !important;
}

/* Nuke the toolbar ghost space */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
}
#MainMenu, footer { visibility: hidden; height: 0 !important; }

/* ═══════════════════════════════════════════════
   VERTICAL RHYTHM — The core fix
   All st.element wrappers that add ghost padding
   ═══════════════════════════════════════════════ */
div[data-testid="stVerticalBlock"] {
    gap: 0 !important;           /* Kills inter-element gaps inside columns */
}
div[data-testid="stHorizontalBlock"] {
    gap: 6px !important;         /* Tight column gutters */
    align-items: stretch !important;
}

/* Kill every default Streamlit element wrapper gap */
div[data-testid="element-container"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* The ghost padding on stMarkdown that creates blank lines */
div[data-testid="stMarkdown"] {
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stMarkdown"] p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}

/* Empty markdown divs — full erasure */
div[data-testid="stMarkdown"]:empty,
div[data-testid="stMarkdown"] > div:empty {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
}

/* Plotly chart containers — no extra bottom margin */
div[data-testid="stPlotlyChart"] {
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stPlotlyChart"] > div {
    margin: 0 !important;
}

/* st.metric built-in — kill its padding */
div[data-testid="stMetric"] {
    background: #071526 !important;
    border: 1px solid #0d2540 !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
    margin: 0 !important;
}
div[data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #e8f4ff !important;
}
div[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 9px !important;
    color: #3a6a8a !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
div[data-testid="stMetricDelta"] {
    font-size: 11px !important;
}

/* Column padding — minimal */
div[data-testid="column"] {
    padding: 0 3px !important;
}
div[data-testid="column"]:first-child { padding-left: 0 !important; }
div[data-testid="column"]:last-child  { padding-right: 0 !important; }

/* ═══════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060e1c 0%, #071526 100%) !important;
    border-right: 1px solid #0d2540 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * { color: #c0d8f0 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #3aafff !important;
    font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}
[data-testid="stSidebar"] div[data-testid="element-container"] {
    margin-bottom: 2px !important;
}

/* ═══════════════════════════════════════════════
   KPI CARDS — Ultra-compact, zero dead space
   ═══════════════════════════════════════════════ */
.kpi-card {
    background: linear-gradient(160deg, #0d2040 0%, #071526 100%);
    border: 1px solid #0d2540;
    border-top: 2px solid #1a5a9a;
    border-radius: 10px;
    padding: 10px 13px 9px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.35);
    position: relative;
    overflow: hidden;
    height: 100%;
    box-sizing: border-box;
}
.kpi-card::after {
    content: "";
    position: absolute;
    top: 0; left: 20%; right: 20%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(58,175,255,0.3), transparent);
}
.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8.5px;
    color: #3a6a8a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #e8f4ff;
    line-height: 1;
    margin-bottom: 2px;
    white-space: nowrap;
}
.kpi-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #1a4a6a;
    white-space: nowrap;
}
.kpi-delta-up   { color: #2ecc71; font-size: 9px; }
.kpi-delta-down { color: #ff4545; font-size: 9px; }
.kpi-delta-flat { color: #f5c542; font-size: 9px; }

/* Accent color variants — top border override only */
.kpi-accent-blue   { border-top-color: #3aafff !important; }
.kpi-accent-green  { border-top-color: #2ecc71 !important; }
.kpi-accent-orange { border-top-color: #ff9040 !important; }
.kpi-accent-red    { border-top-color: #ff4545 !important; }
.kpi-accent-purple { border-top-color: #a87fff !important; }
.kpi-accent-yellow { border-top-color: #f5c542 !important; }

/* ═══════════════════════════════════════════════
   SECTION TITLE — 0-margin version
   ═══════════════════════════════════════════════ */
.sec-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: #3a8abf;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-bottom: 1px solid #0d2540;
    padding-bottom: 3px;
    margin: 0 0 6px 0;        /* Zero top margin — panels butt up tight */
}

/* ═══════════════════════════════════════════════
   PANEL / CARD — Adaptive height, no fixed min-height
   ═══════════════════════════════════════════════ */
.panel {
    background: #071526;
    border: 1px solid #0d2540;
    border-radius: 9px;
    padding: 10px 12px;
    position: relative;
    box-sizing: border-box;
    /* NO min-height — panels shrink to their content */
}
.panel::before {
    content: "";
    position: absolute;
    top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(26,90,154,0.6), transparent);
    border-radius: 9px 9px 0 0;
}

/* Tall panel variant — for charts that need fixed height */
.panel-chart {
    background: #071526;
    border: 1px solid #0d2540;
    border-radius: 9px;
    padding: 8px 10px 4px;
    position: relative;
    box-sizing: border-box;
}
.panel-chart::before {
    content: "";
    position: absolute;
    top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(26,90,154,0.6), transparent);
}

/* ═══════════════════════════════════════════════
   PAGE HEADER BANNER — Slimmed
   ═══════════════════════════════════════════════ */
.page-header {
    background: linear-gradient(90deg, #071526 0%, #0a1d30 50%, #071526 100%);
    border: 1px solid #0d2540;
    border-radius: 8px;
    padding: 7px 16px;
    margin-bottom: 8px;        /* Tight gap before KPI row */
    display: flex;
    align-items: center;
    gap: 10px;
}
.page-header-icon { font-size: 18px; line-height: 1; }
.page-header-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #3aafff;
    letter-spacing: 1.5px;
    line-height: 1;
}
.page-header-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8.5px;
    color: #1a4a6a;
    margin-top: 1px;
    letter-spacing: 1px;
}
.page-header-right {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ═══════════════════════════════════════════════
   KPI ROW WRAPPER — Eliminates the "gap zone"
   Use this div immediately after page-header,
   before any st.columns() call for KPI cards.
   ═══════════════════════════════════════════════ */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 6px;
    margin-bottom: 8px;        /* Tight 8px before panels */
}

/* ═══════════════════════════════════════════════
   GRID LAYOUTS — Dashboard panel grids
   ═══════════════════════════════════════════════ */
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    align-items: start;
}
.grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
    align-items: start;
}
.grid-main-side {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 6px;
    align-items: start;
}
.grid-side-main {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 6px;
    align-items: start;
}
/* Full-width row inside a panel grid */
.grid-span-full { grid-column: 1 / -1; }

/* ═══════════════════════════════════════════════
   ALERT ITEMS
   ═══════════════════════════════════════════════ */
.alert-item {
    padding: 5px 9px;
    border-radius: 5px;
    margin-bottom: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    line-height: 1.4;
}
.alert-warn  { background: #1a1000; border-left: 3px solid #ff9040; color: #ffb86c; }
.alert-info  { background: #00101a; border-left: 3px solid #3aafff; color: #82cfff; }
.alert-ok    { background: #001a0a; border-left: 3px solid #2ecc71; color: #7dff9a; }
.alert-crit  { background: #1a0000; border-left: 3px solid #ff4545; color: #ff8888; }

/* ═══════════════════════════════════════════════
   TABLE
   ═══════════════════════════════════════════════ */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 9.5px;
}
.styled-table th {
    background: #0a1d35;
    color: #3a8abf;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 5px 7px;
    border-bottom: 1px solid #0d2540;
    text-align: left;
    white-space: nowrap;
}
.styled-table td {
    padding: 4px 7px;
    border-bottom: 1px solid #060e1a;
    color: #8ab8d8;
}
.styled-table tr:hover td { background: #0a1d2e; color: #c0d8f0; }
.styled-table tr:last-child td { border-bottom: none; }

/* ═══════════════════════════════════════════════
   LIVE BADGE
   ═══════════════════════════════════════════════ */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #001a08;
    border: 1px solid #0a3a1a;
    border-radius: 20px;
    padding: 2px 8px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #2ecc71;
}
.live-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #2ecc71;
    flex-shrink: 0;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(46,204,113,0.5); }
    50%       { opacity: .7; box-shadow: 0 0 0 3px rgba(46,204,113,0); }
}

/* ═══════════════════════════════════════════════
   SIDEBAR NAV
   ═══════════════════════════════════════════════ */
.sidebar-logo {
    text-align: center;
    padding: 10px 4px 10px 4px;
    border-bottom: 1px solid #0d2540;
    margin-bottom: 8px;
}
.sidebar-logo-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
    font-weight: 700;
    color: #3aafff !important;
    letter-spacing: 2px;
}
.sidebar-logo-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 7.5px;
    color: #1a4a6a !important;
    letter-spacing: 1px;
    margin-top: 2px;
}
.sidebar-section {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #1a4a6a !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 8px 0 3px 0;
    padding-left: 2px;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid #0d2540;
    margin: 6px 0;
}

/* ═══════════════════════════════════════════════
   STREAMLIT WIDGET OVERRIDES
   ═══════════════════════════════════════════════ */
[data-testid="stSelectbox"] label {
    color: #3a6a8a !important;
    font-size: 9.5px !important;
    font-family: 'Share Tech Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    margin-bottom: 2px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #0a1d2e !important;
    border: 1px solid #0d2540 !important;
    color: #c0d8f0 !important;
    min-height: 32px !important;
    font-size: 12px !important;
}

/* Multiselect */
[data-testid="stMultiSelect"] label {
    color: #3a6a8a !important;
    font-size: 9.5px !important;
    font-family: 'Share Tech Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="stMultiSelect"] > div > div {
    background: #0a1d2e !important;
    border: 1px solid #0d2540 !important;
    min-height: 32px !important;
}

/* Radio buttons */
[data-testid="stRadio"] label {
    color: #8ab8d8 !important;
    font-size: 11px !important;
}

/* Sliders */
[data-testid="stSlider"] label {
    color: #3a6a8a !important;
    font-size: 9.5px !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* Buttons */
.stButton > button {
    border-radius: 7px !important;
    border: 1px solid #0d2540 !important;
    background: linear-gradient(90deg, #0a2540, #0d3560) !important;
    color: #3aafff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.8px !important;
    padding: 4px 12px !important;
    height: 30px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    border-color: #3aafff !important;
    box-shadow: 0 0 8px rgba(58,175,255,0.2) !important;
    color: #82cfff !important;
}

/* Expander — tighter */
[data-testid="stExpander"] {
    background: #071526 !important;
    border: 1px solid #0d2540 !important;
    border-radius: 8px !important;
}
[data-testid="stExpanderToggleIcon"] { color: #3aafff !important; }

/* Dataframe / table */
[data-testid="stDataFrame"] {
    border: 1px solid #0d2540 !important;
    border-radius: 8px !important;
}

/* Text input */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #0a1d2e !important;
    border: 1px solid #0d2540 !important;
    color: #c0d8f0 !important;
    border-radius: 7px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    height: 30px !important;
    padding: 0 8px !important;
}

/* Progress bar */
[data-testid="stProgress"] > div > div {
    background: #0a1d2e !important;
    border-radius: 4px !important;
    height: 5px !important;
}
[data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, #1a5a9a, #3aafff) !important;
    border-radius: 4px !important;
}

/* Caption / small text */
[data-testid="stCaptionContainer"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 8.5px !important;
    color: #1a4a6a !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid #0d2540 !important;
    margin: 6px 0 !important;
}

/* ═══════════════════════════════════════════════
   INSIGHT BOX
   ═══════════════════════════════════════════════ */
.insight-item {
    padding: 6px 9px;
    border-radius: 6px;
    margin-bottom: 4px;
    background: #060e1c;
    border-left: 3px solid #1a5a9a;
    font-family: 'Inter', sans-serif;
    font-size: 10.5px;
    color: #8ab8d8;
    line-height: 1.45;
}
.insight-item b { color: #3aafff; }
.insight-item:last-child { margin-bottom: 0; }

/* ═══════════════════════════════════════════════
   DEPTH / PROGRESS BARS
   ═══════════════════════════════════════════════ */
.depth-bar-bg {
    height: 5px;
    background: #040c18;
    border-radius: 3px;
    margin-top: 4px;
    overflow: hidden;
}
.depth-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #1a5a9a, #3aafff);
    border-radius: 3px;
}

/* Mini bar (for tables / inline metrics) */
.mini-bar-bg {
    height: 3px;
    background: #0a1d2e;
    border-radius: 2px;
    overflow: hidden;
    margin-top: 2px;
}
.mini-bar-fill {
    height: 100%;
    border-radius: 2px;
}

/* ═══════════════════════════════════════════════
   STATUS BADGES
   ═══════════════════════════════════════════════ */
.badge {
    display: inline-block;
    border-radius: 4px;
    padding: 1px 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    vertical-align: middle;
}
.badge-green  { background: #001a0a; border: 1px solid #0a3a1a; color: #2ecc71; }
.badge-blue   { background: #00101a; border: 1px solid #0a2a40; color: #3aafff; }
.badge-orange { background: #1a0e00; border: 1px solid #3a1e00; color: #ff9040; }
.badge-red    { background: #1a0000; border: 1px solid #3a0000; color: #ff4545; }
.badge-purple { background: #0f0a1a; border: 1px solid #2a1a4a; color: #a87fff; }
.badge-gray   { background: #0a0e14; border: 1px solid #1a2030; color: #3a6a8a; }

/* ═══════════════════════════════════════════════
   SCROLLBAR — Custom slim scrollbar
   ═══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #040c18; }
::-webkit-scrollbar-thumb { background: #0d2540; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #1a4a6a; }

/* ═══════════════════════════════════════════════
   UTILITY CLASSES
   ═══════════════════════════════════════════════ */
.txt-blue   { color: #3aafff !important; }
.txt-green  { color: #2ecc71 !important; }
.txt-orange { color: #ff9040 !important; }
.txt-red    { color: #ff4545 !important; }
.txt-yellow { color: #f5c542 !important; }
.txt-purple { color: #a87fff !important; }
.txt-muted  { color: #3a6a8a !important; }
.txt-dim    { color: #1a4a6a !important; }
.txt-mono   { font-family: 'Share Tech Mono', monospace !important; }
.txt-rajdhani { font-family: 'Rajdhani', sans-serif !important; }

/* Flex utilities */
.flex-center { display: flex; align-items: center; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }
.flex-gap-4  { gap: 4px; }
.flex-gap-8  { gap: 8px; }

/* Spacers — use SPARINGLY and only these fixed sizes */
.sp2  { height: 2px;  display: block; }
.sp4  { height: 4px;  display: block; }
.sp8  { height: 8px;  display: block; }

/* ═══════════════════════════════════════════════
   PLOTLY CHART OVERRIDES (applied via config)
   These match what you pass into fig.update_layout()
   — kept here as reference for modules/charts.py
   ═══════════════════════════════════════════════ */
/*
  Standard plotly layout kwargs to use in charts.py:

  CHART_LAYOUT = dict(
      paper_bgcolor="#071526",
      plot_bgcolor="#071526",
      font=dict(family="Share Tech Mono", color="#8ab8d8", size=10),
      margin=dict(l=42, r=8, t=24, b=32),
      height=CHART_H,
      legend=dict(
          bgcolor="rgba(7,21,38,0.8)",
          bordercolor="#0d2540",
          borderwidth=1,
          font=dict(size=9),
          x=0.01, y=0.99,
          xanchor="left", yanchor="top",
      ),
      xaxis=dict(
          gridcolor="#0a1d2e",
          linecolor="#0d2540",
          tickfont=dict(size=8.5),
          tickcolor="#0d2540",
      ),
      yaxis=dict(
          gridcolor="#0a1d2e",
          linecolor="#0d2540",
          tickfont=dict(size=8.5),
          tickcolor="#0d2540",
      ),
  )
*/

/* ═══════════════════════════════════════════════
   STREAMLIT SPACING NUCLEAR OPTION
   Eliminates the empty div rows Streamlit injects
   between st.columns() calls.
   ═══════════════════════════════════════════════ */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Row gaps between successive st.columns() rows */
[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0 !important;
    margin: 0 !important;
}

/* The div Streamlit wraps each "row" of columns in */
div.stColumns {
    gap: 6px !important;
    margin-bottom: 6px !important;    /* uniform row gap */
}
div.stColumns:last-child {
    margin-bottom: 0 !important;
}

/* ═══════════════════════════════════════════════
   RESPONSIVE — Ultrawide (>1600px)
   ═══════════════════════════════════════════════ */
@media (min-width: 1600px) {
    .kpi-value { font-size: 26px; }
    .panel, .panel-chart { border-radius: 10px; }
}

/* ═══════════════════════════════════════════════
   GLOBAL GAP ANNIHILATOR v2 — covers all ST versions
   ═══════════════════════════════════════════════ */

/* Every vertical stack: zero gap */
section.main > div,
section.main > div > div,
[data-testid="stMainBlockContainer"] > div,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlock"] > div {
    gap: 0 !important;
    row-gap: 0 !important;
}

/* Every element wrapper: zero margin */
[data-testid="element-container"],
[data-testid="stMarkdown"],
[data-testid="stMarkdown"] > div {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Paragraph inside markdown: zero margin */
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] div {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}

/* Plotly wrapper: zero margin */
[data-testid="stPlotlyChart"],
[data-testid="stPlotlyChart"] > div,
[data-testid="stPlotlyChart"] iframe {
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}

/* Column rows: tight uniform 6px gap */
div.stColumns {
    gap: 6px !important;
    margin-top: 0 !important;
    margin-bottom: 6px !important;
    align-items: stretch !important;
}
div.stColumns:last-child { margin-bottom: 0 !important; }

/* Column cells: minimal side padding only */
[data-testid="column"] {
    padding: 0 3px !important;
    margin: 0 !important;
}
[data-testid="column"]:first-child { padding-left: 0 !important; }
[data-testid="column"]:last-child  { padding-right: 0 !important; }

/* Panels fill column height */
.panel, .panel-chart {
    height: 100%;
    box-sizing: border-box;
}

/* KPI cards — fixed readable height */
.kpi-card { min-height: 72px; box-sizing: border-box; }
.kpi-value { font-size: 22px !important; white-space: nowrap; }
.kpi-label { font-size: 8px  !important; }
</style>
"""

# ── Page layout helper — call at top of every page ────────────────────────────
def page_setup(title: str, icon: str, subtitle: str = "") -> None:
    """
    Inject CSS + render the compact page header.
    Replace st.set_page_config() title prefix and call this once per page.
    """
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    sub_html = f'<div class="page-header-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-icon">{icon}</div>
        <div>
            <div class="page-header-title">{title}</div>
            {sub_html}
        </div>
        <div class="page-header-right">
            <span class="live-badge">
                <span class="live-dot"></span>LIVE
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── KPI card HTML helper ──────────────────────────────────────────────────────
def kpi_card(label: str, value: str, sub: str = "",
             accent: str = "blue", delta: str = "", delta_dir: str = "") -> str:
    """
    Return HTML for a KPI card.
    accent: blue | green | orange | red | purple | yellow
    delta_dir: up | down | flat
    """
    delta_html = ""
    if delta:
        cls = {"up": "kpi-delta-up", "down": "kpi-delta-down"}.get(delta_dir, "kpi-delta-flat")
        arrow = {"up": "▲", "down": "▼"}.get(delta_dir, "—")
        delta_html = f'<span class="{cls}">{arrow} {delta}</span>'

    return f"""
    <div class="kpi-card kpi-accent-{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub} {delta_html}</div>
    </div>
    """


# ── Plotly layout base dict — import in charts.py ─────────────────────────────
def chart_layout(height: int = CHART_H, title: str = "", margin_l: int = 44) -> dict:
    """Base Plotly layout dict matching the dark theme."""
    base = dict(
        paper_bgcolor="#071526",
        plot_bgcolor="#071526",
        font=dict(family="Share Tech Mono, monospace", color="#8ab8d8", size=10),
        margin=dict(l=margin_l, r=8, t=28 if title else 14, b=32),
        height=height,
        legend=dict(
            bgcolor="rgba(4,12,24,0.85)",
            bordercolor="#0d2540",
            borderwidth=1,
            font=dict(size=8.5, color="#8ab8d8"),
            x=0.01, y=0.99,
            xanchor="left", yanchor="top",
        ),
        xaxis=dict(
            gridcolor="#0a1d2e",
            linecolor="#0d2540",
            zerolinecolor="#0d2540",
            tickfont=dict(size=8.5, color="#3a6a8a"),
            tickcolor="#0d2540",
            title_font=dict(size=9, color="#3a6a8a"),
        ),
        yaxis=dict(
            gridcolor="#0a1d2e",
            linecolor="#0d2540",
            zerolinecolor="#0d2540",
            tickfont=dict(size=8.5, color="#3a6a8a"),
            tickcolor="#0d2540",
            title_font=dict(size=9, color="#3a6a8a"),
        ),
        hoverlabel=dict(
            bgcolor="#0a1d2e",
            bordercolor="#0d2540",
            font=dict(family="Share Tech Mono", size=10, color="#c0d8f0"),
        ),
        modebar=dict(
            bgcolor="rgba(4,12,24,0)",
            color="#1a4a6a",
            activecolor="#3aafff",
        ),
    )
    if title:
        base["title"] = dict(
            text=title,
            font=dict(family="Rajdhani, sans-serif", size=12, color="#3a8abf"),
            x=0.01, xanchor="left", y=0.97, yanchor="top",
        )
    return base
