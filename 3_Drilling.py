"""
pages/3_Drilling.py — Drilling Operations Interface
Original design preserved exactly. Integrated into unified platform.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PLATFORM_NAME, GLOBAL_CSS, C
from auth import require_auth, logout, get_display_name, is_admin

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=f"{PLATFORM_NAME} — Drilling",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
require_auth()

# ── Helpers ───────────────────────────────────────────────────────────────────
def _pct(current, target):
    if not target or target == 0:
        return 0
    return min(100, round(current / target * 100, 1))

def _depth_bar(pct: float, color: str = "#3aafff") -> str:
    return (
        f'<div class="depth-bar-bg"><div class="depth-bar-fill" '
        f'style="width:{pct}%;background:linear-gradient(90deg,#1a5a9a,{color})"></div></div>'
    )

def _kpi(label, value, sub="", accent="blue") -> str:
    return (
        f'<div class="kpi-card kpi-accent-{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>'
    )

STATUS_COLORS = {
    "Drilling":    C["green"],
    "Tripping In": C["blue"],
    "Tripping Out":C["blue2"],
    "Circulating": C["yellow"],
    "WOC":         C["orange"],
    "Casing":      C["purple"],
    "Testing":     C["yellow"],
    "POOH":        C["orange"],
    "Standby":     C["txt3"],
    "Shut-in":     C["red"],
}

# ── Default drilling state ────────────────────────────────────────────────────
DEFAULT_INFO = {
    "dashTitle":       "Al-Qurnayn Field Dashboard",
    "date":            "—",
    "time":            "—",
    "well":            "—",
    "field":           "Al-Qurnayn",
    "operation":       "Rotary Drilling",
    "rop":             "—",
    "targetFormation": "Mishrif",
    "currentIssue":    "None",
    "org":             "—",
    "division":        "—",
    "contract":        "—",
    "prepared":        "—",
    "supervised":      "—",
    "approved":        "—",
    "depth":           2640,
    "targetDepth":     3200,
    "layer":           "Mishrif",
}

# ── Session state init ────────────────────────────────────────────────────────
if "drilling_data" not in st.session_state:
    st.session_state.drilling_data = {
        "info": DEFAULT_INFO.copy(),
        "tasks": [
            {"task": "Run 9⅝\" casing to 2640m", "status": "Completed"},
            {"task": "Drill to 3200m TD",         "status": "In Progress"},
            {"task": "Run DST #1",                 "status": "Planned"},
            {"task": "Wireline logging",           "status": "Planned"},
            {"task": "Cement & complete",          "status": "Planned"},
        ],
        "fuel": [
            {"date": "Day-5", "received": 4000, "used": 3800, "remaining": 200},
            {"date": "Day-4", "received": 0,    "used": 3650, "remaining": 4550},
            {"date": "Day-3", "received": 5000, "used": 3900, "remaining": 5650},
            {"date": "Day-2", "received": 0,    "used": 3700, "remaining": 1950},
            {"date": "Day-1", "received": 4500, "used": 3750, "remaining": 2700},
        ],
        "rig_params": {
            "wob": "18 klbs",  "rpm": "120",   "spp": "2850 psi",
            "flow": "650 gpm", "tor": "14 kft·lbf", "ecd": "11.2 ppg",
            "mw":  "10.8 ppg", "temp": "72°C",
        },
    }

dd = st.session_state.drilling_data
info = dd["info"]

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

    if is_admin():
        st.markdown('<div class="sidebar-section">📤 UPLOAD RIG DATA</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("rig_data_template.xlsx", type=["xlsx"],
                                     key="drill_upload", label_visibility="collapsed")
        if uploaded:
            try:
                xl = pd.ExcelFile(uploaded)
                if "Info" in xl.sheet_names:
                    df_info = xl.parse("Info")
                    df_info.columns = [str(c).strip() for c in df_info.columns]
                    key_col = next((c for c in df_info.columns if c.lower() in ("key","parameter","field")), None)
                    val_col = next((c for c in df_info.columns if c.lower() == "value"), None)
                    if key_col and val_col:
                        for _, row in df_info.iterrows():
                            k = str(row[key_col]).strip()
                            v = row[val_col]
                            if k and k.lower() != "nan" and k in info:
                                import pandas as _pd
                                info[k] = v if not _pd.isna(v) else "—"
                if "Tasks" in xl.sheet_names:
                    df_tasks = xl.parse("Tasks")
                    df_tasks.columns = [str(c).strip().lower() for c in df_tasks.columns]
                    if "task" in df_tasks.columns:
                        if "status" not in df_tasks.columns:
                            df_tasks["status"] = "Planned"
                        dd["tasks"] = df_tasks[["task","status"]].fillna("—").to_dict(orient="records")
                if "Fuel" in xl.sheet_names:
                    df_fuel = xl.parse("Fuel")
                    df_fuel.columns = [str(c).strip().lower() for c in df_fuel.columns]
                    for col in ("date","received","used","remaining"):
                        if col not in df_fuel.columns:
                            df_fuel[col] = 0
                    df_fuel["date"] = df_fuel["date"].astype(str)
                    dd["fuel"] = df_fuel[["date","received","used","remaining"]].to_dict(orient="records")
                st.success("✅ Rig data loaded")
                st.rerun()
            except Exception as e:
                st.error(f"Parse error: {e}")

        st.divider()
        with st.expander("✏️ Edit Well Info", expanded=False):
            info["well"]      = st.text_input("Well",       value=str(info.get("well","—")))
            info["field"]     = st.text_input("Field",      value=str(info.get("field","—")))
            info["operation"] = st.text_input("Operation",  value=str(info.get("operation","—")))
            info["depth"]     = st.number_input("Current Depth (m)", value=int(info.get("depth",0)), step=1)
            info["targetDepth"] = st.number_input("Target Depth (m)", value=int(info.get("targetDepth",3200)), step=1)
            info["rop"]       = st.text_input("ROP (m/hr)", value=str(info.get("rop","—")))
            info["layer"]     = st.text_input("Current Layer", value=str(info.get("layer","—")))
            info["currentIssue"] = st.text_input("Current Issue", value=str(info.get("currentIssue","None")))

    st.markdown(
        f'<div style="font-family:Share Tech Mono,monospace; font-size:8px; color:#1a4a6a;">'
        f'👤 {get_display_name()} &nbsp;·&nbsp; {st.session_state.get("role","").upper()}</div>',
        unsafe_allow_html=True)
    if st.button("⏻ Logout", key="logout_drill"):
        logout()


# ── Page header ───────────────────────────────────────────────────────────────
depth       = int(info.get("depth", 0))
target_depth = int(info.get("targetDepth", 3200))
depth_pct   = _pct(depth, target_depth)

st.markdown(f"""
<div class="page-header">
  <div class="page-header-icon">⚙️</div>
  <div style="flex:1">
    <div class="page-header-title">DRILLING OPERATIONS</div>
    <div class="page-header-sub">
      WELL: <span style="color:#3aafff">{info.get("well","—")}</span> &nbsp;·&nbsp;
      FIELD: {info.get("field","—")} &nbsp;·&nbsp;
      OPERATION: {info.get("operation","—")} &nbsp;·&nbsp;
      <span class="live-badge"><span class="live-dot"></span>LIVE</span>
    </div>
  </div>
  <div style="text-align:right;min-width:140px;">
    <div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:#3aafff">{depth:,} m</div>
    <div style="font-family:Share Tech Mono,monospace;font-size:8px;color:#1a4a6a">
      TARGET: {target_depth:,} m &nbsp;·&nbsp; {depth_pct:.0f}%
    </div>
    {_depth_bar(depth_pct)}
  </div>
</div>
""", unsafe_allow_html=True)

# ── ROW 1: Header KPIs ────────────────────────────────────────────────────────
kpi_cols = st.columns(5, gap="small")
kpi_data = [
    ("CURRENT DEPTH",   f"{depth:,} m",                        "RKB reference",            "blue"),
    ("TARGET DEPTH",    f"{target_depth:,} m",                  f"Remaining: {target_depth - depth:,} m", "orange"),
    ("ROP",             str(info.get("rop","—")) + " m/hr",    "Instantaneous rate",       "green"),
    ("FORMATION",       str(info.get("layer","—")),             str(info.get("targetFormation","—")), "purple"),
    ("CURRENT ISSUE",   str(info.get("currentIssue","None")),   info.get("operation","—"),  "red" if str(info.get("currentIssue","")).lower() not in ("none","—","") else "green"),
]
for i, (lbl, val, sub, acc) in enumerate(kpi_data):
    with kpi_cols[i]:
        st.markdown(_kpi(lbl, val, sub, acc), unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── ROW 2: Rig Parameters | Wellbore Schematic | Operations Log ───────────────
c1, c2, c3 = st.columns([1, 0.9, 1.1], gap="small")

# ── Rig Parameters ────────────────────────────────────────────────────────────
with c1:
    rp = dd.get("rig_params", {})
    params = [
        ("WOB",          rp.get("wob","—"),   C["orange"]),
        ("RPM",          rp.get("rpm","—"),   C["blue"]),
        ("SPP",          rp.get("spp","—"),   C["blue2"]),
        ("FLOW RATE",    rp.get("flow","—"),  C["green"]),
        ("TORQUE",       rp.get("tor","—"),   C["yellow"]),
        ("ECD",          rp.get("ecd","—"),   C["orange"]),
        ("MUD WEIGHT",   rp.get("mw","—"),    C["purple"]),
        ("MUD TEMP",     rp.get("temp","—"),  C["red"]),
    ]
    rows = "".join(
        f'<tr>'
        f'<td style="color:{C["txt3"]};padding:5px 8px;font-size:9px;font-family:Share Tech Mono,monospace;'
        f'border-bottom:1px solid {C["bdr2"]}">{lbl}</td>'
        f'<td style="color:{col};padding:5px 8px;font-size:13px;font-family:Rajdhani,sans-serif;'
        f'font-weight:600;text-align:right;border-bottom:1px solid {C["bdr2"]}">{val}</td>'
        f'</tr>'
        for lbl, val, col in params
    )
    st.markdown(
        f'<div class="panel" style="min-height:280px;">'
        f'<div class="sec-title">⚙️ Rig Parameters</div>'
        f'<table style="width:100%;border-collapse:collapse">{rows}</table>'
        f'</div>', unsafe_allow_html=True)

    if is_admin():
        with st.expander("✏️ Edit Rig Parameters"):
            for key, label in [("wob","WOB"),("rpm","RPM"),("spp","SPP"),("flow","Flow Rate"),
                                ("tor","Torque"),("ecd","ECD"),("mw","Mud Weight"),("temp","Mud Temp")]:
                rp[key] = st.text_input(label, value=rp.get(key,"—"), key=f"rp_{key}")

# ── Wellbore Schematic (Plotly) ───────────────────────────────────────────────
with c2:
    def _wellbore_fig(depth_m: int, target_m: int) -> go.Figure:
        fig = go.Figure()
        formations = [
            (0,    400,  "#1a3a1a", "Surface"),
            (400,  900,  "#2a1a00", "Dammam"),
            (900,  1500, "#1a0a00", "Kirkuk"),
            (1500, 2200, "#0a1530", "Faris"),
            (2200, 2800, "#0a2030", "Tanuma"),
            (2800, 3200, "#00102a", "Mishrif"),
        ]
        for top, bot, col, name in formations:
            fig.add_shape(type="rect", x0=-1, x1=1, y0=-bot, y1=-top,
                          fillcolor=col, line=dict(color="#0d2540", width=0.5))
            fig.add_annotation(x=0.85, y=-(top + bot)/2, text=name, showarrow=False,
                                font=dict(size=7, color="#3a6a8a"),
                                xref="x", yref="y")

        # Casing strings
        casing_data = [(8.625/2, 0, 800, C["txt3"], "13⅜\""),
                       (6.625/2, 0, 2640, C["blue2"], "9⅝\"")]
        for r, top, bot, col, label in casing_data:
            scale = 0.12
            for sign in [-1, 1]:
                fig.add_shape(type="rect", x0=sign*(r-0.5)*scale, x1=sign*r*scale,
                              y0=-bot, y1=-top,
                              fillcolor=col, opacity=0.5,
                              line=dict(color=col, width=0.8))

        # Open hole + bit
        oh_r = 0.5 * 0.12
        fig.add_shape(type="rect", x0=-oh_r, x1=oh_r, y0=-depth_m, y1=-2640,
                      fillcolor=C["orange"], opacity=0.3,
                      line=dict(color=C["orange"], width=0.5))

        # Drill string
        fig.add_trace(go.Scatter(
            x=[0, 0], y=[0, -depth_m],
            mode="lines", line=dict(color=C["green"], width=2),
            name="Drill String", showlegend=False,
        ))

        # Current depth marker
        fig.add_hline(y=-depth_m, line_color=C["blue"],
                      line_dash="dot", line_width=1.5,
                      annotation_text=f" {depth_m}m",
                      annotation_font=dict(size=8, color=C["blue"]))

        # Target depth marker
        fig.add_hline(y=-target_m, line_color=C["yellow"],
                      line_dash="dash", line_width=1,
                      annotation_text=f" TD {target_m}m",
                      annotation_font=dict(size=8, color=C["yellow"]))

        fig.update_layout(
            template="plotly_dark", paper_bgcolor=C["bg1"], plot_bgcolor=C["bg1"],
            height=310, margin=dict(l=5, r=55, t=5, b=5),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-1.2, 1.2]),
            yaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(size=7, color=C["txt3"]),
                       range=[-(target_m + 100), 50]),
            showlegend=False,
        )
        return fig

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🕳️ Wellbore Schematic</div>', unsafe_allow_html=True)
    st.plotly_chart(_wellbore_fig(depth, target_depth),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── Operations Log / Task Tracker ─────────────────────────────────────────────
with c3:
    STATUS_ICON = {"Completed":"✅","In Progress":"🔄","Planned":"🕐","On Hold":"⏸️","Cancelled":"❌"}
    STATUS_CLR  = {"Completed":C["green"],"In Progress":C["blue"],"Planned":C["txt3"],
                   "On Hold":C["orange"],"Cancelled":C["red"]}
    tasks = dd.get("tasks", [])
    rows_html = "".join(
        f'<tr>'
        f'<td style="padding:5px 8px;font-size:10px;color:{C["txt2"]};'
        f'border-bottom:1px solid {C["bdr2"]};font-family:Inter,sans-serif">'
        f'{t.get("task","")}</td>'
        f'<td style="padding:5px 8px;font-size:9px;white-space:nowrap;'
        f'color:{STATUS_CLR.get(t.get("status",""),C["txt3"])};'
        f'border-bottom:1px solid {C["bdr2"]};font-family:Share Tech Mono,monospace">'
        f'{STATUS_ICON.get(t.get("status",""),"·")} {t.get("status","")}</td>'
        f'</tr>'
        for t in tasks
    )
    st.markdown(
        f'<div class="panel" style="min-height:200px;">'
        f'<div class="sec-title">📋 Operations Log</div>'
        f'<table class="styled-table" style="width:100%">'
        f'<thead><tr><th>Task / Operation</th><th>Status</th></tr></thead>'
        f'<tbody>{rows_html}</tbody></table>'
        f'</div>', unsafe_allow_html=True)

    if is_admin():
        with st.expander("➕ Add Task"):
            new_task   = st.text_input("Task description", key="new_task_input")
            new_status = st.selectbox("Status", ["Planned","In Progress","Completed","On Hold","Cancelled"], key="new_task_status")
            if st.button("Add", key="add_task_btn"):
                if new_task:
                    tasks.append({"task": new_task, "status": new_status})
                    st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── ROW 3: Fuel Consumption | Daily Summary ────────────────────────────────────
c4, c5 = st.columns([1.2, 1], gap="small")

with c4:
    fuel = dd.get("fuel", [])
    if fuel:
        df_fuel = pd.DataFrame(fuel)
        fig_fuel = go.Figure()
        if "received" in df_fuel.columns:
            fig_fuel.add_trace(go.Bar(
                x=df_fuel["date"], y=df_fuel["received"],
                name="Received", marker_color=C["green"], opacity=0.8,
                hovertemplate="<b>%{x}</b><br>Received: %{y:,.0f} L<extra></extra>",
            ))
        if "used" in df_fuel.columns:
            fig_fuel.add_trace(go.Bar(
                x=df_fuel["date"], y=df_fuel["used"],
                name="Used", marker_color=C["orange"], opacity=0.8,
                hovertemplate="<b>%{x}</b><br>Used: %{y:,.0f} L<extra></extra>",
            ))
        if "remaining" in df_fuel.columns:
            fig_fuel.add_trace(go.Scatter(
                x=df_fuel["date"], y=df_fuel["remaining"],
                name="Remaining", mode="lines+markers",
                line=dict(color=C["blue"], width=2.5),
                marker=dict(size=6), yaxis="y2",
                hovertemplate="<b>%{x}</b><br>Remaining: %{y:,.0f} L<extra></extra>",
            ))
        fig_fuel.update_layout(
            template="plotly_dark", paper_bgcolor=C["bg1"], plot_bgcolor=C["bg1"],
            height=240, barmode="group", margin=dict(l=40,r=45,t=8,b=35),
            legend=dict(orientation="h", y=1.05, font=dict(size=8, color=C["txt2"]),
                        bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor=C["bdr2"], tickfont=dict(size=8, color=C["txt3"])),
            yaxis=dict(gridcolor=C["bdr2"], tickfont=dict(size=8, color=C["txt3"]), zeroline=False),
            yaxis2=dict(overlaying="y", side="right",
                        tickfont=dict(size=8, color=C["blue"]), showgrid=False),
        )
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">⛽ Fuel Consumption</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_fuel, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

with c5:
    # ── Daily Report Summary — Well / Daily Activity (from Excel Daily_Report sheet) ──
    # Load from session state if uploaded, else from unified_database
    daily_df = pd.DataFrame()

    # Check if uploaded rig file has Daily_Report sheet
    if "rig_daily_report" in st.session_state and not st.session_state.rig_daily_report.empty:
        daily_df = st.session_state.rig_daily_report
    else:
        # Try to load from unified_database
        try:
            from modules.excel_loader import get_cached_data as _gcd
            _d = _gcd()
            if not _d.daily_report.empty:
                daily_df = _d.daily_report
        except Exception:
            pass

    # Fallback demo rows
    if daily_df.empty:
        daily_df = pd.DataFrame([
            {"Well_Name": "AQ-21",
             "Daily_Activity": "Drill 8½\" hole 2620→2655m. ROP 8.5 m/hr. MW 10.8 ppg."},
            {"Well_Name": "AQ-21",
             "Daily_Activity": "Circulate & condition mud. Survey at 2655m — inc 2.3°."},
            {"Well_Name": "AQ-20",
             "Daily_Activity": "POOH for bit change. New PDC 8½\" IADC M332 RIH."},
            {"Well_Name": "AQ-19",
             "Daily_Activity": "Run 7\" liner to 3195m. Cement job — 420 sacks + 40% excess."},
            {"Well_Name": "AQ-18",
             "Daily_Activity": "DST #2 Mishrif — FWHP 1450 psi, 5200 BOPD. PBU ongoing."},
        ])

    # Normalize column names
    daily_df.columns = [str(c).strip() for c in daily_df.columns]
    well_col = next((c for c in daily_df.columns
                     if "well" in c.lower()), daily_df.columns[0] if len(daily_df.columns) > 0 else None)
    act_col  = next((c for c in daily_df.columns
                     if "activ" in c.lower() or "daily" in c.lower() or "desc" in c.lower()),
                    daily_df.columns[1] if len(daily_df.columns) > 1 else None)

    if well_col and act_col:
        rows_dr = "".join(
            f'<tr>'
            f'<td style="color:{C["blue3"]};padding:5px 8px;font-size:9.5px;'
            f'font-family:Share Tech Mono,monospace;border-bottom:1px solid {C["bdr2"]};'
            f'white-space:nowrap;font-weight:600;vertical-align:top">{row[well_col]}</td>'
            f'<td style="color:{C["txt2"]};padding:5px 8px;font-size:9px;'
            f'font-family:Inter,sans-serif;border-bottom:1px solid {C["bdr2"]};'
            f'line-height:1.5">{row[act_col]}</td>'
            f'</tr>'
            for _, row in daily_df.iterrows()
        )
        table_dr = (
            f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr>'
            f'<th style="background:#0a1d35;color:#3a8abf;font-family:Share Tech Mono,monospace;'
            f'font-size:8px;padding:5px 8px;border-bottom:1px solid #0d2540;'
            f'text-transform:uppercase;letter-spacing:.8px;text-align:left;white-space:nowrap">Well</th>'
            f'<th style="background:#0a1d35;color:#3a8abf;font-family:Share Tech Mono,monospace;'
            f'font-size:8px;padding:5px 8px;border-bottom:1px solid #0d2540;'
            f'text-transform:uppercase;letter-spacing:.8px;text-align:left">Daily Activity</th>'
            f'</tr></thead><tbody>{rows_dr}</tbody></table>'
        )
    else:
        table_dr = (
            f'<div style="padding:20px;text-align:center;color:{C["txt3"]};'
            f'font-family:Share Tech Mono,monospace;font-size:9px;">'
            f'No daily report data.<br><small>Add Daily_Report sheet (Well_Name, Daily_Activity).</small></div>'
        )

    st.markdown(
        f'<div class="panel" style="min-height:200px;">'
        f'<div class="sec-title">📄 Daily Report Summary</div>'
        f'{table_dr}'
        f'</div>', unsafe_allow_html=True)

    # ── Admin: allow uploading daily report separately ─────────────────────
    if is_admin():
        with st.expander("📤 Upload Daily Report (Excel)", expanded=False):
            dr_up = st.file_uploader(
                "Sheet: Daily_Report — columns: Well_Name, Daily_Activity",
                type=["xlsx"], key="dr_upload", label_visibility="visible")
            if dr_up:
                try:
                    xl2 = pd.ExcelFile(dr_up)
                    sheet = "Daily_Report" if "Daily_Report" in xl2.sheet_names else xl2.sheet_names[0]
                    df_dr = xl2.parse(sheet)
                    df_dr.columns = [str(c).strip() for c in df_dr.columns]
                    st.session_state.rig_daily_report = df_dr
                    st.success(f"✅ Loaded {len(df_dr)} rows from '{sheet}'")
                    st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="text-align:center;padding:8px 0 0 0;font-family:Share Tech Mono,monospace;'
    f'font-size:8px;color:{C["txt4"]}">AL-QURNAYN FIELD PLATFORM v2.0 &nbsp;·&nbsp; DRILLING INTERFACE</div>',
    unsafe_allow_html=True)
