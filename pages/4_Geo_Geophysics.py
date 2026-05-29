"""
pages/4_Geo_Geophysics.py  —  Al-Qurnayn  |  Geo / Geophysics
الحل الجذري للفراغات: نبني كل Row بـ st.columns مرة واحدة فقط
ونحقن chart_key فريد لكل plotly chart
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from auth import require_auth
from config import page_setup, kpi_card, chart_layout, CHART_H, C
from config import UNIFIED_DB, MAPS_DIR, CORR_DIR

st.set_page_config(
    page_title="Al-Qurnayn — Geo/Geophysics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)
require_auth()
page_setup("GEO / GEOPHYSICS", "🌍", "GEOSCIENCE & SEISMIC INTELLIGENCE")

# ─────────────────────────────────────────────
#  EXTRA CSS  —  القضاء الكامل على الفراغات
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ① حذف كل gap بين عناصر Streamlit داخل الأعمدة */
section.main > div { gap: 0 !important; }
div[data-testid="stVerticalBlock"]        { gap: 0 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { padding:0 !important; margin:0 !important; }
div[data-testid="element-container"]      { margin:0 !important; padding:0 !important; }
div[data-testid="stMarkdown"]             { margin:0 !important; padding:0 !important; }
div[data-testid="stMarkdown"] p           { margin:0 !important; line-height:1 !important; }

/* ② الصفوف المكونة من st.columns */
div.stColumns           { gap:6px !important; margin-bottom:6px !important; align-items:stretch !important; }
div.stColumns:last-child{ margin-bottom:0 !important; }
div[data-testid="column"]{ padding:0 2px !important; }
div[data-testid="column"]:first-child { padding-left:0 !important; }
div[data-testid="column"]:last-child  { padding-right:0 !important; }

/* ③ Plotly لا هامش تحته */
div[data-testid="stPlotlyChart"]     { margin:0 !important; padding:0 !important; }
div[data-testid="stPlotlyChart"] > * { margin:0 !important; }
iframe                               { display:block !important; margin:0 !important; }

/* ④ KPI cards ارتفاع موحد */
.kpi-card { min-height:74px; }
.kpi-value{ font-size:22px !important; white-space:nowrap; }
.kpi-label{ font-size:8px  !important; }

/* ⑤ Panel يملأ ارتفاع العمود كاملاً */
.panel, .panel-chart {
    height: 100%;
    box-sizing: border-box;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('''
    <div class="sidebar-logo">
        <div style="font-size:26px">🛢️</div>
        <div class="sidebar-logo-title">AL-QURNAYN</div>
        <div class="sidebar-logo-sub">FIELD INTELLIGENCE PLATFORM</div>
    </div>''', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)
    try:
        st.page_link("app.py",                      label="🏠  Home / Login")
        st.page_link("pages/1_Home_Dashboard.py",   label="📊  Main Dashboard")
        st.page_link("pages/2_Reservoir.py",        label="🗄️  Reservoir")
        st.page_link("pages/3_Drilling.py",         label="⛏️  Drilling")
        st.page_link("pages/4_Geo_Geophysics.py",   label="🌍  Geo / Geophysics")
    except Exception:
        pass

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Geo Filters</div>', unsafe_allow_html=True)
    show_faults   = st.checkbox("Show Fault Traces",    value=True)
    show_contacts = st.checkbox("Show Fluid Contacts",  value=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    from auth import get_display_name, logout
    st.markdown(f'<div class="sidebar-section">👤 {get_display_name()}</div>',
                unsafe_allow_html=True)
    if st.button("⏏  Logout", use_container_width=True):
        logout()

# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def _load():
    try:
        xl = pd.ExcelFile(UNIFIED_DB)
        sn = xl.sheet_names
        return {
            "res":  xl.parse("Reservoir_Master") if "Reservoir_Master" in sn else None,
            "wells":xl.parse("Wells")            if "Wells"            in sn else None,
            "ptl":  xl.parse("Pressure_TL")      if "Pressure_TL"      in sn else None,
            "rp":   xl.parse("Rock_Physics")      if "Rock_Physics"      in sn else None,
        }
    except Exception:
        return {}

_raw = _load()

# ── Demo fallback ────────────────────────────
_rng = np.random.default_rng(42)

def _demo_res():
    return pd.DataFrame({
        "Reservoir_Name":  ["Mishrif","Yamama","Nahr Umr","Zubair","Mauddud","Shuaiba","Ahmadi"],
        "Pressure_psi":    [3842,4120,3560,3980,3710,4250,3640],
        "Porosity_pct":    [0.22,0.18,0.28,0.15,0.20,0.16,0.24],
        "Permeability_mD": [245, 88, 410, 62,  158, 74,  320],
        "NTG":             [0.72,0.58,0.85,0.48,0.68,0.52,0.78],
        "Sw":              [0.28,0.35,0.22,0.40,0.31,0.38,0.25],
        "TVD_m":           [2500,3800,1800,3200,2900,4100,2200],
        "Vshale":          [0.18,0.28,0.12,0.35,0.22,0.30,0.15],
        "OOIP_MBO":        [4200,2800,6100,1900,3400,2100,5200],
    })

def _demo_wells():
    wn = [f"AQ-{i:02d}" for i in range(1,25)]
    r  = _demo_res()
    return pd.DataFrame({
        "Well_Name":      wn,
        "Reservoir_Name": _rng.choice(r["Reservoir_Name"],24),
        "Well_Status":    _rng.choice(["Producing","Producing","Producing",
                                       "Shut-in","Injector","P&A"],24),
        "X": _rng.uniform(10,90,24).round(1),
        "Y": _rng.uniform(10,90,24).round(1),
        "TVD_m": _rng.uniform(2000,4200,24).round(0),
    })

def _demo_ptl():
    m = pd.date_range("2021-01","2026-05",freq="MS")
    r = _rng
    return pd.DataFrame({
        "Date":     m,
        "Mishrif":  (3950-np.cumsum(r.uniform(0,15,len(m)))).round(0),
        "Yamama":   (4200-np.cumsum(r.uniform(0,8, len(m)))).round(0),
        "Nahr Umr": (3700-np.cumsum(r.uniform(0,12,len(m)))).round(0),
        "Zubair":   (4050-np.cumsum(r.uniform(0,10,len(m)))).round(0),
    })

def _demo_rp():
    p  = _rng.uniform(0.05,0.38,300)
    k  = np.clip(np.exp(_rng.normal(0,1.5,300)+8*p+1),0.1,12000)
    return pd.DataFrame({"Porosity":p,"Permeability":k,"Sw":_rng.uniform(0.1,0.9,300)})

def _or_demo(val, demo_fn):
    """Return val if it's a non-empty DataFrame, else call demo_fn()."""
    if isinstance(val, pd.DataFrame):
        return val if not val.empty else demo_fn()
    return demo_fn() if val is None else val

RES   = _or_demo(_raw.get("res"),   _demo_res)
WELLS = _or_demo(_raw.get("wells"), _demo_wells)
PTL   = _or_demo(_raw.get("ptl"),   _demo_ptl)
RP    = _or_demo(_raw.get("rp"),    _demo_rp)

# ── Aggregates ────────────────────────────────
def _cmean(df, col, default):
    return float(df[col].mean()) if col in df.columns and not df[col].isna().all() else default
def _csum(df, col, default):
    return float(df[col].sum())  if col in df.columns and not df[col].isna().all() else default

avg_poro   = _cmean(RES, "Porosity_pct",    0.20)
avg_perm   = _cmean(RES, "Permeability_mD", 150.0)
avg_sw     = _cmean(RES, "Sw",              0.30)
avg_ntg    = _cmean(RES, "NTG",             0.65)
avg_vsh    = _cmean(RES, "Vshale",          0.22)
total_ooip = _csum (RES, "OOIP_MBO",        0.0)
n_wells   = len(WELLS)

_CH  = 242   # chart height — tight but readable
_CH2 = 200   # bottom row charts

# ═══════════════════════════════════════════════
#  ROW 0 — KPI (8 cards)
# ═══════════════════════════════════════════════
kc = st.columns(8, gap="small")
_kpis = [
    ("TOTAL WELLS",     str(n_wells),              "DRILLED",       "blue",   "+5 7d","up"),
    ("SEISMIC SURVEYS", "3",                        "3D / 2D",       "green",  "",     ""),
    ("HORIZONS MAPPED", "7",                        "INTERPRETED",   "purple", "+3",   "up"),
    ("FAULTS MAPPED",   "12",                       "IDENTIFIED",    "orange", "+8 7d","up"),
    ("AVG POROSITY",    f"{avg_poro*100:.1f}%",     "FIELD AVG φ",   "blue",   "",     ""),
    ("AVG Sw",          f"{avg_sw*100:.1f}%",       "WATER SAT",     "orange", "-0.8%","down"),
    ("TOTAL OOIP",      f"{total_ooip/1000:.1f}B",  "BO IN-PLACE",   "green",  "",     ""),
    ("AVG PERM",        f"{avg_perm:.0f}mD",        "FIELD AVG k",   "purple", "",     ""),
]
for col,(lbl,val,sub,acc,dlt,ddr) in zip(kc,_kpis):
    with col:
        st.markdown(kpi_card(lbl,val,sub,acc,dlt,ddr), unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  CHART BUILDER HELPERS
# ═══════════════════════════════════════════════
_FT_COLORS = {"Producing":"#2ecc71","Shut-in":"#ff4545",
              "Injector":"#3aafff","P&A":"#3a6a8a","Pending":"#f5c542"}
_FT_SYM    = {"Producing":"circle","Shut-in":"circle-open",
              "Injector":"square","P&A":"x","Pending":"diamond"}

def _base(h=_CH, ml=38):
    L = chart_layout(height=h)
    L["margin"] = dict(l=ml, r=6, t=6, b=28)
    return L

def _struct_map():
    rn = np.random.RandomState(7)
    x = np.linspace(0,100,55); y = np.linspace(0,100,55)
    X,Y = np.meshgrid(x,y)
    Z = (2500
         -350*np.exp(-((X-45)**2+(Y-50)**2)/900)
         -120*np.exp(-((X-70)**2+(Y-30)**2)/400)
         +rn.normal(0,8,X.shape))
    L = _base(ml=28)
    L["xaxis"] = {**L["xaxis"],"title":"X (km)","showgrid":False}
    L["yaxis"] = {**L["yaxis"],"title":"Y (km)","showgrid":False}
    fig = go.Figure(layout=L)
    fig.add_trace(go.Contour(
        z=Z,x=x,y=y,
        colorscale=[[0,"#ff4545"],[.25,"#ff9040"],[.5,"#f5c542"],
                    [.75,"#2ecc71"],[1,"#3aafff"]],
        contours=dict(coloring="fill",showlabels=True,
                      labelfont=dict(size=6.5,color="white"),
                      start=int(Z.min()),end=int(Z.max()),size=40),
        colorbar=dict(thickness=7,len=0.75,
                      tickfont=dict(size=7,color="#3a6a8a"),
                      title=dict(text="TWT(ms)",font=dict(size=7,color="#3a6a8a"),side="right"),
                      bgcolor="rgba(7,21,38,.7)",bordercolor="#0d2540"),
        line=dict(width=.4,color="rgba(255,255,255,.2)"),
        hovertemplate="X:%{x:.0f} Y:%{y:.0f}<br>TWT:%{z:.0f}ms<extra></extra>",name="",
    ))
    if show_faults:
        for fx,fy in [([20,55],[80,35]),([60,85],[70,20]),([10,40],[40,15])]:
            fig.add_trace(go.Scatter(x=fx,y=fy,mode="lines",
                line=dict(color="#ff4545",width=1.5,dash="dash"),
                showlegend=False,hoverinfo="skip"))
    # wells
    for st_,grp in WELLS.groupby("Well_Status"):
        fig.add_trace(go.Scatter(
            x=grp["X"],y=grp["Y"],mode="markers",name=st_,
            marker=dict(color=_FT_COLORS.get(st_,"#8ab8d8"),size=6,
                        symbol=_FT_SYM.get(st_,"circle"),
                        line=dict(width=.8,color="white")),
            hovertemplate="<b>%{text}</b><extra></extra>",
            text=grp["Well_Name"]))
    fig.add_annotation(text="N↑",x=95,y=95,showarrow=False,
                       font=dict(size=11,color="white",family="Rajdhani"))
    return fig

def _seismic_inline():
    rn2 = np.random.RandomState(99)
    nt,ns = 80,120
    twt = np.linspace(1400,3800,ns)
    seis = rn2.normal(0,.02,(ns,nt))
    picks = [1640,2085,2295,2460,2680]
    for pt in picks:
        idx = np.argmin(np.abs(twt-pt))
        sl  = slice(max(0,idx-2),min(ns,idx+3))
        seis[sl,:] += .22*rn2.choice([-1,1])*(1+.05*rn2.normal(0,1,nt))
    L = _base(ml=36)
    L["yaxis"] = {**L["yaxis"],"title":"TWT (ms)","autorange":"reversed","tickformat":",.0f"}
    L["xaxis"] = {**L["xaxis"],"title":"CDP"}
    fig = go.Figure(layout=L)
    fig.add_trace(go.Heatmap(z=seis,x=np.arange(nt),y=twt,
        colorscale="RdBu_r",zmin=-.35,zmax=.35,showscale=False,
        hovertemplate="CDP:%{x} TWT:%{y:.0f}ms<extra></extra>"))
    pc = ["#f5c542","#3aafff","#2ecc71","#ff9040","#a87fff"]
    pn = ["Shuaiba","Top Mshrif","Base Mshrif","Mauddud","Nahr Umr"]
    for pt,pname,pcol in zip(picks,pn,pc):
        fig.add_hline(y=pt,line=dict(color=pcol,width=.8,dash="dot"),
                      annotation_text=pname,
                      annotation_font_size=7,annotation_font_color=pcol,
                      annotation_position="right")
    for wcdp,wlbl in [(15,"A-06"),(38,"A-03"),(60,"A-01")]:
        fig.add_vline(x=wcdp,line=dict(color="#f5c542",width=.8,dash="dot"))
        fig.add_annotation(x=wcdp,y=1420,text=f"<b>{wlbl}</b>",
                           showarrow=False,font=dict(size=7.5,color="#f5c542"),
                           yanchor="bottom")
    return fig

def _well_map():
    L = _base(ml=28)
    L["xaxis"] = {**L["xaxis"],"title":"Easting (km)"}
    L["yaxis"] = {**L["yaxis"],"title":"Northing (km)"}
    L["legend"]= {**L["legend"],"x":1.0,"y":1.0,"xanchor":"left","font":dict(size=7.5)}
    L["margin"]["r"] = 70
    fig = go.Figure(layout=L)
    fig.add_trace(go.Scatter(x=[5,5,95,95,5],y=[5,95,95,5,5],
        mode="lines",name="3D Seismic",
        line=dict(color="#3aafff",width=.8,dash="dot"),
        fill="toself",fillcolor="rgba(58,175,255,.03)"))
    for st_,grp in WELLS.groupby("Well_Status"):
        fig.add_trace(go.Scatter(
            x=grp["X"],y=grp["Y"],mode="markers",name=st_,
            marker=dict(color=_FT_COLORS.get(st_,"#8ab8d8"),size=7,
                        symbol=_FT_SYM.get(st_,"circle"),
                        line=dict(width=.8,color="white")),
            text=grp["Well_Name"],
            hovertemplate="<b>%{text}</b><br>"+st_+"<extra></extra>"))
    fig.add_annotation(text="N↑",x=95,y=95,showarrow=False,
                       font=dict(size=11,color="white",family="Rajdhani"))
    return fig

def _well_corr():
    rn3 = np.random.RandomState(55)
    depth = np.linspace(2100,2750,200)
    wells_c = ["AQ-06","AQ-03","AQ-01","AQ-02"]
    xpos    = [1,3,5,7]
    L = _base(ml=18)
    L["xaxis"] = {**L["xaxis"],"showgrid":False,"showticklabels":False,"range":[0,8.5],"title":""}
    L["yaxis"] = {**L["yaxis"],"title":"Depth (m)","autorange":"reversed","dtick":100}
    L["legend"]= {**L["legend"],"x":.01,"y":.01,"yanchor":"bottom","font":dict(size=7.5)}
    fig = go.Figure(layout=L)
    pick_d = {"Top Mishrif":2500,"Base Mishrif":2710}
    pcols  = {"Top Mishrif":"#3aafff","Base Mishrif":"#2ecc71"}
    first  = True
    for xi,wn in zip(xpos,wells_c):
        gr  = np.convolve(rn3.uniform(20,120,len(depth)),np.ones(8)/8,mode="same")
        grn = (gr-gr.min())/(gr.max()-gr.min())*.7
        fig.add_trace(go.Scatter(x=xi+grn,y=depth,mode="lines",
            name="GR" if first else "",showlegend=first,
            line=dict(color="#f5c542",width=.8),hoverinfo="skip"))
        fig.add_annotation(x=xi+.35,y=2115,text=f"<b>{wn}</b>",
                           showarrow=False,font=dict(size=7.5,color="#8ab8d8"),yanchor="bottom")
        for pn,pd_ in pick_d.items():
            pd_w = pd_+rn3.uniform(-15,15)
            fig.add_trace(go.Scatter(x=[xi-.1,xi+.85],y=[pd_w,pd_w],mode="lines",
                name=pn if first else "",showlegend=first,
                line=dict(color=pcols[pn],width=1.2),
                hovertemplate=f"{pn}: %{{y:.0f}}m<extra></extra>"))
        first = False
    return fig

def _amplitude_map():
    rn4 = np.random.RandomState(33)
    x = np.linspace(0,100,80); y = np.linspace(0,100,80)
    X,Y = np.meshgrid(x,y)
    A = (.3*np.exp(-((X-40)**2+(Y-55)**2)/500)
         +.2*np.exp(-((X-65)**2+(Y-35)**2)/300)
         +.05*rn4.normal(0,1,X.shape))
    L = _base(ml=10)
    L["xaxis"] = {**L["xaxis"],"showgrid":False,"showticklabels":False,"title":""}
    L["yaxis"] = {**L["yaxis"],"showgrid":False,"showticklabels":False,"title":""}
    L["margin"]["r"] = 10
    fig = go.Figure(layout=L)
    fig.add_trace(go.Heatmap(z=A,x=x,y=y,
        colorscale=[[0,"#000080"],[.25,"#0000ff"],[.5,"#00ffff"],
                    [.75,"#ffff00"],[1,"#ff0000"]],
        colorbar=dict(thickness=7,len=.75,
                      tickfont=dict(size=7,color="#3a6a8a"),
                      title=dict(text="Amplitude",font=dict(size=7,color="#3a6a8a"),side="right"),
                      bgcolor="rgba(7,21,38,.7)",bordercolor="#0d2540"),
        hovertemplate="X:%{x:.0f} Y:%{y:.0f}<br>Amp:%{z:.3f}<extra></extra>"))
    if show_faults:
        for fx,fy in [([15,55],[75,30]),([58,80],[80,25])]:
            fig.add_trace(go.Scatter(x=fx,y=fy,mode="lines",
                line=dict(color="black",width=2),showlegend=False,hoverinfo="skip"))
    fig.add_annotation(text="N↑",x=95,y=95,showarrow=False,
                       font=dict(size=11,color="white",family="Rajdhani"))
    return fig

def _crossplot():
    L = _base(ml=42)
    L["xaxis"] = {**L["xaxis"],"title":"Porosity (v/v)","range":[0,.38],"dtick":.05}
    L["yaxis"] = {**L["yaxis"],"title":"Permeability (mD)","type":"log","range":[-1,4]}
    L["coloraxis"] = dict(
        colorscale=[[0,"#3aafff"],[.5,"#f5c542"],[1,"#ff4545"]],
        cmin=0,cmax=1,
        colorbar=dict(title=dict(text="Sw",font=dict(size=7,color="#3a6a8a"),side="right"),
                      thickness=7,len=.7,tickfont=dict(size=7,color="#3a6a8a"),
                      bgcolor="rgba(7,21,38,.7)",bordercolor="#0d2540"))
    fig = go.Figure(layout=L)
    fig.add_trace(go.Scatter(x=RP["Porosity"],y=RP["Permeability"],mode="markers",
        marker=dict(size=3.5,color=RP["Sw"],coloraxis="coloraxis",opacity=.7),
        hovertemplate="φ:%{x:.3f} k:%{y:.1f}mD<extra></extra>",name=""))
    for _,row in RES.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["Porosity_pct"]],y=[row["Permeability_mD"]],
            mode="markers+text",
            marker=dict(size=9,symbol="star",color="#f5c542",line=dict(width=.8,color="white")),
            text=[row["Reservoir_Name"][:5]],textposition="top right",
            textfont=dict(size=6.5,color="#f5c542"),showlegend=False,
            hovertemplate=f"<b>{row['Reservoir_Name']}</b><br>φ:{row['Porosity_pct']:.2f} k:{row['Permeability_mD']:.0f}mD<extra></extra>"))
    return fig

def _pressure_tl():
    L = _base(h=_CH2, ml=46)
    L["xaxis"] = {**L["xaxis"],"title":"Date"}
    L["yaxis"] = {**L["yaxis"],"title":"Pressure (psi)"}
    fig = go.Figure(layout=L)
    cols_ = [c for c in ["Mishrif","Yamama","Nahr Umr","Zubair"] if c in PTL.columns]
    clrs  = ["#3aafff","#2ecc71","#ff9040","#a87fff"]
    for c,cl in zip(cols_,clrs):
        fig.add_trace(go.Scatter(x=PTL["Date"],y=PTL[c],name=c,
            line=dict(color=cl,width=1.4),mode="lines",
            hovertemplate=f"<b>{c}</b><br>%{{x|%b %Y}}: %{{y:,.0f}}psi<extra></extra>"))
    return fig

def _avo():
    rn5 = np.random.default_rng(21)
    n   = 200
    cls = rn5.choice(["Class II","Class III","Background"],n,p=[.15,.2,.65])
    df  = pd.DataFrame({
        "I":rn5.normal(0,.04,n),"G":rn5.normal(0,.06,n),"C":cls})
    L = _base(h=_CH2, ml=40)
    L["xaxis"] = {**L["xaxis"],"title":"Intercept","zeroline":True,
                  "zerolinecolor":"#1a4a6a","zerolinewidth":1,"range":[-.15,.15]}
    L["yaxis"] = {**L["yaxis"],"title":"Gradient","zeroline":True,
                  "zerolinecolor":"#1a4a6a","zerolinewidth":1,"range":[-.25,.25]}
    L["legend"]= {**L["legend"],"x":.01,"y":.01,"yanchor":"bottom","font":dict(size=7.5)}
    fig = go.Figure(layout=L)
    for c,clr in [("Class III","#ff4545"),("Class II","#f5c542"),("Background","#3a6a8a")]:
        g = df[df["C"]==c]
        fig.add_trace(go.Scatter(x=g["I"],y=g["G"],mode="markers",name=c,
            marker=dict(color=clr,size=3.5,opacity=.75),
            hovertemplate=f"<b>{c}</b><br>I:%{{x:.3f}} G:%{{y:.3f}}<extra></extra>"))
    return fig

def _res_bars():
    rs = RES.sort_values("Porosity_pct")
    L = _base(h=_CH2, ml=68)
    L["xaxis"] = {**L["xaxis"],"title":"","range":[0,1]}
    L["yaxis"] = {**L["yaxis"],"title":"","autorange":"reversed","tickfont":dict(size=8.5)}
    L["barmode"] = "overlay"
    fig = go.Figure(layout=L)
    pn = rs["Porosity_pct"]/rs["Porosity_pct"].max()
    kn = rs["Permeability_mD"]/rs["Permeability_mD"].max()
    fig.add_trace(go.Bar(y=rs["Reservoir_Name"],x=pn,name="Porosity",orientation="h",
        marker=dict(color="#3aafff",opacity=.85),
        hovertemplate="%{y}: φ=%{customdata:.1%}<extra></extra>",
        customdata=rs["Porosity_pct"]))
    fig.add_trace(go.Bar(y=rs["Reservoir_Name"],x=kn,name="Perm",orientation="h",
        marker=dict(color="#2ecc71",opacity=.5),
        hovertemplate="%{y}: k=%{customdata:.0f}mD<extra></extra>",
        customdata=rs["Permeability_mD"]))
    return fig

_CFG = {"displayModeBar": False}

# ═══════════════════════════════════════════════
#  ROW 1 — Structural Map | Seismic Inline | Well Map
# ═══════════════════════════════════════════════
c1, c2, c3 = st.columns([1,1,1], gap="small")

with c1:
    st.markdown('<div class="panel-chart"><div class="sec-title">📐 Structural Map (Top Mishrif)</div>', unsafe_allow_html=True)
    st.plotly_chart(_struct_map(), use_container_width=True, config=_CFG, key="structural_map")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="panel-chart"><div class="sec-title">🔊 Seismic Inline Section</div>', unsafe_allow_html=True)
    st.plotly_chart(_seismic_inline(), use_container_width=True, config=_CFG, key="seismic_inline")
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="panel-chart"><div class="sec-title">📍 Well Location Map</div>', unsafe_allow_html=True)
    st.plotly_chart(_well_map(), use_container_width=True, config=_CFG, key="well_map")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  ROW 2 — Well Correlation | Amplitude Map | Cross Plot
# ═══════════════════════════════════════════════
c4, c5, c6 = st.columns([1,1,1], gap="small")

with c4:
    st.markdown('<div class="panel-chart"><div class="sec-title">🔗 Well Correlation (Mishrif)</div>', unsafe_allow_html=True)
    st.plotly_chart(_well_corr(), use_container_width=True, config=_CFG, key="well_corr")
    st.markdown('</div>', unsafe_allow_html=True)

with c5:
    st.markdown('<div class="panel-chart"><div class="sec-title">🌊 Amplitude Map (Top Reservoir)</div>', unsafe_allow_html=True)
    st.plotly_chart(_amplitude_map(), use_container_width=True, config=_CFG, key="amp_map")
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="panel-chart"><div class="sec-title">⚙️ Cross Plot — Porosity vs Permeability</div>', unsafe_allow_html=True)
    st.plotly_chart(_crossplot(), use_container_width=True, config=_CFG, key="crossplot")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  ROW 3 — Formation Tops | Rock Physics Gauges | AI Insights | Alerts
# ═══════════════════════════════════════════════
c7, c8, c9, c10 = st.columns([1.1, 1.3, 1.4, 0.9], gap="small")

with c7:
    _tops = [
        ("Shuaiba",      1640, 1975, 180),
        ("Top Mishrif",  2085, 2500, 210),
        ("Base Mishrif", 2295, 2710, 165),
        ("Mauddud",      2460, 2875, 220),
        ("Nahr Umr",     2680, 3095, "—"),
        ("Top Yamama",   3200, 3820, 280),
        ("Zubair",       3650, 4150, 195),
    ]
    rows = "".join(
        f"<tr><td style='color:#3aafff'>{f}</td><td style='color:#3a8abf'>{t}</td>"
        f"<td style='color:#8ab8d8'>{d}</td><td style='color:#ff9040'>{k}</td></tr>"
        for f,t,d,k in _tops)
    st.markdown(f'''
    <div class="panel">
      <div class="sec-title">📋 Formation Tops Summary</div>
      <table class="styled-table" style="width:100%">
        <thead><tr><th>Formation</th><th>TWT(ms)</th><th>Depth(m)</th><th>Thick(m)</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>''', unsafe_allow_html=True)

with c8:
    _params = [
        ("Vshale",   avg_vsh,  0,  0.6,  "#f5c542"),
        ("Porosity", avg_poro, 0,  0.40, "#3aafff"),
        ("Sw",       avg_sw,   0,  0.80, "#ff9040"),
        ("N/G",      avg_ntg,  0,  1.0,  "#2ecc71"),
    ]
    Lg = dict(paper_bgcolor="#071526",plot_bgcolor="#071526",
              font=dict(family="Share Tech Mono",color="#8ab8d8",size=9),
              margin=dict(l=4,r=4,t=8,b=4),height=190,
              grid=dict(rows=1,columns=4,pattern="independent"),showlegend=False)
    fg = go.Figure(layout=Lg)
    for i,(k,v,vn,vx,clr) in enumerate(_params):
        fg.add_trace(go.Indicator(
            mode="gauge+number",value=round(v,2),
            number=dict(font=dict(size=16,color=clr,family="Rajdhani")),
            title=dict(text=f"<b>{k}</b><br><span style='font-size:7px;color:#3a6a8a'>Avg</span>",
                       font=dict(size=8,color="#3a6a8a")),
            gauge=dict(
                axis=dict(range=[vn,vx],tickfont=dict(size=6.5,color="#3a6a8a"),
                          nticks=3,tickcolor="#0d2540"),
                bar=dict(color=clr,thickness=0.55),
                bgcolor="#040c18",borderwidth=1,bordercolor="#0d2540",
                steps=[dict(range=[vn,vx],color="#0a1d2e")]),
            domain=dict(row=0,column=i)))
    st.markdown('<div class="panel"><div class="sec-title">🪨 Rock Physics Overview</div>', unsafe_allow_html=True)
    st.plotly_chart(fg, use_container_width=True, config=_CFG, key="rock_gauges")
    st.markdown('</div>', unsafe_allow_html=True)

with c9:
    lp = RES.sort_values("Pressure_psi").iloc[0]
    hp = RES.sort_values("Porosity_pct",ascending=False).iloc[0]
    st.markdown(f'''
    <div class="panel">
      <div class="sec-title">🤖 AI / GEO INSIGHTS</div>
      <div class="insight-item">✅ <b>High amplitude anomaly</b> detected in Top Mishrif —
        probable hydrocarbon trap. AVO response consistent with Class III.</div>
      <div class="insight-item">✅ <b>{hp["Reservoir_Name"]}</b> best porosity
        ({hp["Porosity_pct"]*100:.1f}%) — primary development target.</div>
      <div class="insight-item">✅ <b>AVO analysis</b> indicates Class III in northern closure.
        Good reservoir quality predicted in AQ-01 and AQ-03.</div>
      <div class="insight-item">⚠️ <b>{lp["Reservoir_Name"]}</b> lowest pressure
        ({lp["Pressure_psi"]:,.0f} psi) — evaluate pressure support.</div>
      <div class="insight-item">✅ <b>Fault F-12</b> sealing potential confirmed.
        Additional well recommended in NE flank.</div>
    </div>''', unsafe_allow_html=True)

with c10:
    st.markdown('''
    <div class="panel">
      <div class="sec-title">🚨 ALERTS</div>
      <div class="alert-item alert-crit">▲ AQ-04: log missing<br>interval 2450–2600 m</div>
      <div class="alert-item alert-warn">⚠ Seismic issue<br>Inline 1100–1150</div>
      <div class="alert-item alert-info">ℹ Horizon picking<br>incomplete Block AQ</div>
      <div class="alert-item alert-warn">⚠ Low fold area<br>in 3D survey</div>
      <div class="alert-item alert-ok">✓ All checkshot<br>calibrations valid</div>
      <div style="margin-top:5px;text-align:right">
        <span style="font-family:Share Tech Mono,monospace;font-size:8px;color:#3aafff">
          View all alerts →</span>
      </div>
    </div>''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  ROW 4 — Res Properties | Pressure TL | AVO
# ═══════════════════════════════════════════════
c11, c12, c13 = st.columns([1, 1.3, 1], gap="small")

with c11:
    st.markdown('<div class="panel-chart"><div class="sec-title">📊 Reservoir Properties</div>', unsafe_allow_html=True)
    st.plotly_chart(_res_bars(), use_container_width=True, config=_CFG, key="res_bars")
    st.markdown('</div>', unsafe_allow_html=True)

with c12:
    st.markdown('<div class="panel-chart"><div class="sec-title">📈 Time-lapse Reservoir Pressure</div>', unsafe_allow_html=True)
    st.plotly_chart(_pressure_tl(), use_container_width=True, config=_CFG, key="pressure_tl")
    st.markdown('</div>', unsafe_allow_html=True)

with c13:
    st.markdown('<div class="panel-chart"><div class="sec-title">🔬 AVO Cross Plot</div>', unsafe_allow_html=True)
    st.plotly_chart(_avo(), use_container_width=True, config=_CFG, key="avo_plot")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:4px 2px 0 2px;border-top:1px solid #0d2540;margin-top:2px">
  <span style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#1a4a6a">
    GEO | GEOPHYSICS INTELLIGENCE PLATFORM v2.0</span>
  <span style="display:flex;align-items:center;gap:5px">
    <span style="width:5px;height:5px;border-radius:50%;background:#2ecc71;display:inline-block"></span>
    <span style="font-family:'Share Tech Mono',monospace;font-size:8px;color:#2ecc71">
      All data is up to date as of 26-May-2026 09:30</span>
  </span>
</div>
""", unsafe_allow_html=True)
