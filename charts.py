"""
modules/charts.py — All Plotly chart generators for the platform
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import C, CHART_BG, CHART_H

# ── Shared layout helper ────────────────────────────────────────────────────────
def _base_layout(title="", h=CHART_H, **kwargs) -> dict:
    return dict(
        template="plotly_dark",
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        height=h,
        title=dict(text=title, font=dict(size=11, color=C["txt2"],
                   family="Rajdhani, sans-serif"), x=0.5, xanchor="center"),
        margin=dict(l=45, r=15, t=30 if title else 12, b=40),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
            font=dict(size=9, color=C["txt2"]),
            bgcolor="rgba(0,0,0,0)", bordercolor=C["border"], borderwidth=0,
        ),
        xaxis=dict(gridcolor=C["bdr2"], gridwidth=0.5, linecolor=C["border"],
                   tickfont=dict(size=8, color=C["txt3"]), zeroline=False),
        yaxis=dict(gridcolor=C["bdr2"], gridwidth=0.5, linecolor=C["border"],
                   tickfont=dict(size=8, color=C["txt3"]), zeroline=False),
        **kwargs,
    )


# ── Gas Supply LINE Chart (received / used / remaining) ───────────────────────

def fig_gas_supply_lines(gas_df: pd.DataFrame) -> go.Figure:
    """
    Line chart for gas supply: Received, Used, Remaining.
    Mirrors the fuel consumption chart style from the Drilling page.
    """
    fig = go.Figure()

    if gas_df.empty:
        fig.update_layout(**_base_layout("Gas Supply — No Data"))
        return fig

    gas_df = gas_df.copy()
    if "Date" in gas_df.columns:
        gas_df["Date"] = pd.to_datetime(gas_df["Date"], errors="coerce")
        gas_df = gas_df.sort_values("Date")
        x = gas_df["Date"]
    else:
        x = gas_df.index

    recv_col = next((c for c in gas_df.columns if "receiv" in c.lower()), None)
    used_col = next((c for c in gas_df.columns if "used"   in c.lower() or "daily" in c.lower()), None)
    rem_col  = next((c for c in gas_df.columns if "remain" in c.lower()), None)

    if recv_col:
        fig.add_trace(go.Scatter(
            x=x, y=gas_df[recv_col], name="مستلم (Received)",
            mode="lines", line=dict(color=C["green"], width=2.5),
            fill="tozeroy", fillcolor="rgba(46,204,113,0.06)",
            hovertemplate="<b>%{x|%b %Y}</b><br>Received: %{y:,.1f} MMscfd<extra></extra>",
        ))
    if used_col:
        fig.add_trace(go.Scatter(
            x=x, y=gas_df[used_col], name="مستخدم (Used)",
            mode="lines", line=dict(color=C["orange"], width=2.5),
            fill="tozeroy", fillcolor="rgba(255,144,64,0.06)",
            hovertemplate="<b>%{x|%b %Y}</b><br>Used: %{y:,.1f} MMscfd<extra></extra>",
        ))
    if rem_col:
        fig.add_trace(go.Scatter(
            x=x, y=gas_df[rem_col], name="متبقي (Remaining)",
            mode="lines+markers", yaxis="y2",
            line=dict(color=C["blue"], width=2.5, dash="dot"),
            marker=dict(size=4, color=C["blue"]),
            hovertemplate="<b>%{x|%b %Y}</b><br>Remaining: %{y:,.1f} MMscfd<extra></extra>",
        ))

    layout = _base_layout("Gas Supply Overview", h=CHART_H)
    if rem_col:
        layout["yaxis2"] = dict(
            overlaying="y", side="right",
            gridcolor=C["bdr2"], tickfont=dict(size=8, color=C["blue"]),
            showgrid=False, zeroline=False,
        )
    fig.update_layout(**layout)
    return fig


# ── Gas Supply Chart ────────────────────────────────────────────────────────────

def fig_gas_supply(gas_df: pd.DataFrame) -> go.Figure:
    """Daily + monthly + cumulative gas supply combo chart."""
    fig = go.Figure()

    if gas_df.empty:
        fig.update_layout(**_base_layout("Gas Supply — No Data"))
        return fig

    gas_df = gas_df.copy()
    if "Date" in gas_df.columns:
        gas_df["Date"] = pd.to_datetime(gas_df["Date"], errors="coerce")
        gas_df = gas_df.sort_values("Date")
        x = gas_df["Date"]
    elif "Month" in gas_df.columns:
        x = gas_df["Month"].astype(str)
    else:
        x = gas_df.index

    daily_col  = next((c for c in gas_df.columns if "daily" in c.lower() or "rate" in c.lower()), None)
    month_col  = next((c for c in gas_df.columns if "monthly" in c.lower() or "month" in c.lower() and c != "Month"), None)
    cum_col    = next((c for c in gas_df.columns if "cum" in c.lower()), None)

    if daily_col:
        fig.add_trace(go.Bar(
            x=x, y=gas_df[daily_col], name="Daily Gas (MMscfd)",
            marker_color=C["blue"], opacity=0.75,
            hovertemplate="<b>%{x}</b><br>Daily: %{y:,.1f} MMscfd<extra></extra>",
        ))
    if month_col:
        fig.add_trace(go.Bar(
            x=x, y=gas_df[month_col], name="Monthly Gas (Bscf)",
            marker_color=C["blue2"], opacity=0.65,
            hovertemplate="<b>%{x}</b><br>Monthly: %{y:,.2f} Bscf<extra></extra>",
        ))
    if cum_col:
        fig.add_trace(go.Scatter(
            x=x, y=gas_df[cum_col], name="Cumulative (Bscf)",
            mode="lines+markers", yaxis="y2",
            line=dict(color=C["green"], width=2.5),
            marker=dict(size=5, color=C["green"]),
            hovertemplate="<b>%{x}</b><br>Cum: %{y:,.1f} Bscf<extra></extra>",
        ))

    layout = _base_layout("Gas Supply Overview", h=CHART_H)
    layout["barmode"] = "group"
    if cum_col:
        layout["yaxis2"] = dict(
            overlaying="y", side="right",
            gridcolor=C["bdr2"], tickfont=dict(size=8, color=C["green"]),
            showgrid=False, zeroline=False,
        )
    fig.update_layout(**layout)
    return fig


# ── Well Test / Production Results ─────────────────────────────────────────────

def fig_well_tests(prod_df: pd.DataFrame) -> go.Figure:
    """Well test results — oil/gas/water by well, interactive."""
    fig = go.Figure()

    if prod_df.empty or "Well_Name" not in prod_df.columns:
        fig.update_layout(**_base_layout("Well Testing Results — No Data"))
        return fig

    # Aggregate latest test per well
    agg = (prod_df.groupby("Well_Name", as_index=False)
           .agg({c: "mean" for c in ["Oil_Rate", "Gas_Rate", "Water_Rate"]
                 if c in prod_df.columns}))

    wells = agg["Well_Name"].tolist()

    for col, name, color in [
        ("Oil_Rate",   "Oil Rate (bbl/d)",    C["orange"]),
        ("Gas_Rate",   "Gas Rate (MMscfd)",   C["blue"]),
        ("Water_Rate", "Water Rate (bbl/d)",  C["blue2"]),
    ]:
        if col in agg.columns:
            fig.add_trace(go.Bar(
                x=wells, y=agg[col], name=name,
                marker_color=color, opacity=0.85,
                hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y:,.1f}}<extra></extra>",
            ))

    layout = _base_layout("Well Testing Results", h=CHART_H)
    layout["barmode"] = "group"
    layout["xaxis"]["tickangle"] = -35
    fig.update_layout(**layout)
    return fig


# ── Production Trend ───────────────────────────────────────────────────────────

def fig_production_trend(prod_df: pd.DataFrame) -> go.Figure:
    """Multi-line production trend (oil, gas, water) over time."""
    fig = go.Figure()

    if prod_df.empty or "Date" not in prod_df.columns:
        fig.update_layout(**_base_layout("Production Trend — No Data"))
        return fig

    trend = (prod_df.groupby("Date", as_index=False)
             .agg({c: "sum" for c in ["Oil_Rate","Gas_Rate","Water_Rate","Cum_Oil"]
                   if c in prod_df.columns})
             .sort_values("Date"))

    traces = [
        ("Oil_Rate",   "Oil Rate (bbl/d)",   C["orange"], "y"),
        ("Gas_Rate",   "Gas Rate (MMscfd)",  C["blue"],   "y2"),
        ("Water_Rate", "Water Rate (bbl/d)", C["blue2"],  "y"),
    ]
    for col, name, color, yax in traces:
        if col in trend.columns:
            fig.add_trace(go.Scatter(
                x=trend["Date"], y=trend[col],
                name=name, mode="lines", yaxis=yax,
                line=dict(color=color, width=2),
                hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{name}: %{{y:,.1f}}<extra></extra>",
                fill="tozeroy" if col == "Oil_Rate" else "none",
                fillcolor="rgba(255,144,64,0.07)" if col == "Oil_Rate" else None,
            ))

    layout = _base_layout("Production Trend & History", h=CHART_H)
    layout["yaxis2"] = dict(
        overlaying="y", side="right",
        gridcolor=C["bdr2"], tickfont=dict(size=8, color=C["blue"]),
        showgrid=False, zeroline=False,
    )
    fig.update_layout(**layout)
    return fig


# ── Production by Layer ────────────────────────────────────────────────────────

def fig_production_by_layer(layers_df: pd.DataFrame) -> go.Figure:
    """Donut + bar combo showing production contribution by layer."""
    if layers_df.empty:
        fig = go.Figure()
        fig.update_layout(**_base_layout("Production by Layer — No Data"))
        return fig

    layer_col = next((c for c in layers_df.columns if "layer" in c.lower() or "zone" in c.lower()), None)
    rate_col  = next((c for c in layers_df.columns if "rate" in c.lower() or "contribution" in c.lower() or "oil" in c.lower()), None)
    pct_col   = next((c for c in layers_df.columns if "pct" in c.lower() or "percent" in c.lower()), None)

    if not layer_col or not (rate_col or pct_col):
        fig = go.Figure()
        fig.update_layout(**_base_layout("Production by Layer — Missing Columns"))
        return fig

    val_col = pct_col or rate_col
    layers  = layers_df[layer_col].astype(str).tolist()
    values  = pd.to_numeric(layers_df[val_col], errors="coerce").fillna(0).tolist()
    colors  = [C["blue"], C["orange"], C["green"], C["purple"], C["yellow"], C["red"]]

    fig = make_subplots(rows=1, cols=2,
                        specs=[[{"type":"pie"}, {"type":"xy"}]],
                        subplot_titles=["Share (%)", "Rate by Layer"])

    fig.add_trace(go.Pie(
        labels=layers, values=values,
        hole=0.55, name="",
        marker=dict(colors=colors[:len(layers)]),
        textfont=dict(size=9), showlegend=False,
        hovertemplate="<b>%{label}</b><br>%{value:.1f}<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=layers, y=values, name="Production",
        marker=dict(color=colors[:len(layers)]),
        hovertemplate="<b>%{x}</b><br>%{y:.1f}<extra></extra>",
    ), row=1, col=2)

    layout = _base_layout("Production by Layer", h=CHART_H)
    layout.pop("xaxis", None); layout.pop("yaxis", None)
    fig.update_layout(**layout)
    fig.update_annotations(font_size=9, font_color=C["txt2"])
    return fig


# ── Fluid Contacts ─────────────────────────────────────────────────────────────

def fig_fluid_contacts(contacts_df: pd.DataFrame) -> go.Figure:
    """Depth vs Sw with fluid contact markers (GOC, OWC, GWC)."""
    fig = go.Figure()

    if contacts_df.empty:
        fig.update_layout(**_base_layout("Fluid Contacts — No Data"))
        return fig

    depth_col = next((c for c in contacts_df.columns if "depth" in c.lower()), None)
    sw_col    = next((c for c in contacts_df.columns if "sw" in c.lower() or "water_sat" in c.lower()), None)

    if depth_col and sw_col:
        depths = pd.to_numeric(contacts_df[depth_col], errors="coerce").dropna()
        sw     = pd.to_numeric(contacts_df[sw_col], errors="coerce").reindex(depths.index)

        fig.add_trace(go.Scatter(
            x=sw, y=depths,
            mode="lines+markers",
            name="Sw (Water Saturation)",
            line=dict(color=C["blue"], width=2),
            marker=dict(size=4, color=C["blue"]),
            hovertemplate="Depth: %{y:,.0f} ft<br>Sw: %{x:.3f}<extra></extra>",
        ))

        contact_cols = {
            "GOC_ft": (C["green"],  "GOC"),
            "OWC_ft": (C["orange"], "OWC"),
            "GWC_ft": (C["purple"], "GWC"),
        }
        for col, (color, lbl) in contact_cols.items():
            if col in contacts_df.columns:
                val = pd.to_numeric(contacts_df[col], errors="coerce").dropna()
                if not val.empty:
                    contact_depth = float(val.iloc[0])
                    fig.add_hline(
                        y=contact_depth, line_dash="dash",
                        line_color=color, line_width=1.5,
                        annotation_text=f"  {lbl}: {contact_depth:,.0f} ft",
                        annotation_font=dict(size=8, color=color),
                    )

    layout = _base_layout("Fluid Contacts", h=CHART_H)
    layout["yaxis"]["autorange"] = "reversed"
    layout["yaxis"]["title"] = dict(text="Depth (ft)", font=dict(size=9, color=C["txt3"]))
    layout["xaxis"]["title"] = dict(text="Sw", font=dict(size=9, color=C["txt3"]))
    fig.update_layout(**layout)
    return fig


# ── Pressure Distribution Map ──────────────────────────────────────────────────

def fig_pressure_map(res_df: pd.DataFrame, reservoir: str) -> go.Figure:
    """Reservoir pressure visualization — scatter bubble or bar by reservoir."""
    fig = go.Figure()

    if res_df.empty:
        fig.update_layout(**_base_layout("Pressure Distribution — No Data"))
        return fig

    has_xy = "X" in res_df.columns and "Y" in res_df.columns
    has_p  = "Pressure_psi" in res_df.columns

    if not has_p:
        fig.update_layout(**_base_layout("Pressure Distribution — No Pressure Column"))
        return fig

    if has_xy:
        fig.add_trace(go.Scatter(
            x=pd.to_numeric(res_df["X"], errors="coerce"),
            y=pd.to_numeric(res_df["Y"], errors="coerce"),
            mode="markers+text",
            marker=dict(
                size=pd.to_numeric(res_df["Pressure_psi"], errors="coerce") / 200,
                color=pd.to_numeric(res_df["Pressure_psi"], errors="coerce"),
                colorscale=[[0,"#0a3060"],[0.5,"#1a8aff"],[1,"#ffffff"]],
                showscale=True,
                colorbar=dict(thickness=10, len=0.7,
                              tickfont=dict(size=8, color=C["txt3"]),
                              title=dict(text="psi", font=dict(size=8, color=C["txt3"]))),
                line=dict(color=C["border"], width=1),
            ),
            text=res_df.get("Reservoir_Name", pd.Series()),
            textfont=dict(size=8, color=C["txt2"]),
            hovertemplate="<b>%{text}</b><br>Pressure: %{marker.color:,.0f} psi<extra></extra>",
        ))
    else:
        # Bar chart fallback
        names = res_df.get("Reservoir_Name", pd.RangeIndex(len(res_df)).astype(str))
        pressures = pd.to_numeric(res_df["Pressure_psi"], errors="coerce").fillna(0)
        fig.add_trace(go.Bar(
            x=names, y=pressures,
            marker=dict(
                color=pressures,
                colorscale=[[0,"#0a3060"],[0.5,"#1a8aff"],[1,"#aaddff"]],
            ),
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} psi<extra></extra>",
        ))

    fig.update_layout(**_base_layout(
        f"Reservoir Pressure Distribution {'— ' + reservoir if reservoir != 'Show All' else ''}",
        h=CHART_H
    ))
    return fig


# ── Structural Map placeholder ─────────────────────────────────────────────────

def fig_structural_map_plotly(wells_df: pd.DataFrame) -> go.Figure:
    """Interactive well location map when no image is available."""
    fig = go.Figure()

    if wells_df.empty or "X" not in wells_df.columns or "Y" not in wells_df.columns:
        fig.add_annotation(text="No spatial data available<br><sup>Upload Excel with X, Y columns</sup>",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           font=dict(size=13, color=C["txt3"]), showarrow=False)
        fig.update_layout(**_base_layout("Field Structural Map", h=CHART_H))
        return fig

    status_colors = {
        "producing": C["green"], "shut-in": C["red"],
        "testing": C["yellow"], "suspended": C["orange"],
    }
    wells_df = wells_df.copy()
    wells_df["X"] = pd.to_numeric(wells_df["X"], errors="coerce")
    wells_df["Y"] = pd.to_numeric(wells_df["Y"], errors="coerce")
    wells_df["_color"] = wells_df.get("Well_Status", pd.Series()).astype(str).str.lower().map(
        lambda s: next((v for k, v in status_colors.items() if k in s), C["blue2"])
    )

    for status, grp in wells_df.groupby("_color"):
        fig.add_trace(go.Scatter(
            x=grp["X"], y=grp["Y"],
            mode="markers+text",
            marker=dict(size=12, color=status, symbol="diamond",
                        line=dict(color=C["border"], width=1)),
            text=grp.get("Well_Name", ""),
            textposition="top center",
            textfont=dict(size=8, color=C["txt2"]),
            hovertemplate="<b>%{text}</b><br>X:%{x:.0f}  Y:%{y:.0f}<extra></extra>",
        ))

    fig.update_layout(**_base_layout("Field Structural Map — Well Locations", h=CHART_H))
    return fig


# ── Decline Curve ──────────────────────────────────────────────────────────────

def fig_decline_curve(res: "DeclineResult", date_col="Date", rate_col="Rate") -> go.Figure:
    """Full decline curve chart: actual data + best fit + P10/P50/P90 forecast."""
    from modules.decline_analysis import DeclineResult
    fig = go.Figure()

    if res.error:
        fig.add_annotation(text=f"Decline analysis failed:<br>{res.error}",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           font=dict(size=11, color=C["red"]), showarrow=False)
        fig.update_layout(**_base_layout("Decline Curve Analysis", h=CHART_H))
        return fig

    af  = res.all_fits
    t   = af.get("_t_actual", np.array([]))
    q   = af.get("_q_actual", np.array([]))
    t_fc = af.get("_t_fc", res.forecast_t)
    q_p10 = af.get("_q_fc_p10", res.forecast_q * 1.15)
    q_p90 = af.get("_q_fc_p90", res.forecast_q * 0.85)

    last_t = t[-1] if len(t) > 0 else 0

    # Actual production (solid dots)
    fig.add_trace(go.Scatter(
        x=t, y=q, mode="markers",
        name="Actual Production",
        marker=dict(color=C["orange"], size=6, symbol="circle",
                    line=dict(color=C["bg1"], width=1)),
        hovertemplate="Month %{x:.0f}<br>Rate: %{y:,.1f}<extra></extra>",
    ))

    # Best-fit forecast
    mask_hist = t_fc <= last_t
    mask_fore = t_fc > last_t

    fig.add_trace(go.Scatter(
        x=t_fc[mask_hist], y=res.forecast_q[mask_hist],
        mode="lines", name=f"Best Fit ({res.decline_type})",
        line=dict(color=C["blue"], width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=t_fc[mask_fore], y=res.forecast_q[mask_fore],
        mode="lines", name="P50 Forecast",
        line=dict(color=C["blue"], width=2.5),
    ))

    # P10 / P90 shaded area
    fig.add_trace(go.Scatter(
        x=np.concatenate([t_fc[mask_fore], t_fc[mask_fore][::-1]]),
        y=np.concatenate([q_p10[mask_fore], q_p90[mask_fore][::-1]]),
        fill="toself",
        fillcolor="rgba(58,175,255,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        name="P10–P90 Range",
        showlegend=True,
    ))

    # Vertical "today" line
    if last_t > 0:
        fig.add_vline(x=last_t, line_dash="dash", line_color=C["txt3"],
                      line_width=1, annotation_text=" Last Data",
                      annotation_font=dict(size=8, color=C["txt3"]))

    layout = _base_layout(
        f"Decline Curve Analysis — {res.decline_type}  (R²={res.r2:.4f})",
        h=CHART_H
    )
    layout["xaxis"]["title"] = dict(text="Month", font=dict(size=9, color=C["txt3"]))
    layout["yaxis"]["title"] = dict(text="Rate", font=dict(size=9, color=C["txt3"]))
    fig.update_layout(**layout)
    return fig
