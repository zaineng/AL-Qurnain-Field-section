"""
modules/insights_engine.py — Generates smart operational insights & alerts
"""
import pandas as pd
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Alert:
    level: str    # "crit" | "warn" | "info" | "ok"
    title: str
    message: str


@dataclass
class Insight:
    text: str
    icon: str = "💡"


def generate_alerts(kpis: dict, prod_df: pd.DataFrame,
                    wells_df: pd.DataFrame) -> List[Alert]:
    """Generate operational alerts from KPIs and data."""
    alerts = []

    # Well availability
    total = kpis.get("total_wells", 0)
    producing = kpis.get("producing_wells", 0)
    shutin = kpis.get("shutin_wells", 0)

    if total > 0:
        efficiency = producing / total * 100
        if efficiency < 50:
            alerts.append(Alert("crit", "⚠ LOW WELL EFFICIENCY",
                f"Only {producing}/{total} wells producing ({efficiency:.0f}%). Investigate shut-in causes."))
        elif efficiency < 75:
            alerts.append(Alert("warn", "⚡ REDUCED EFFICIENCY",
                f"{shutin} well(s) shut-in. Field efficiency at {efficiency:.0f}%."))
        else:
            alerts.append(Alert("ok", "✓ WELLS OPERATIONAL",
                f"{producing}/{total} wells producing — field efficiency {efficiency:.0f}%."))

    # Pressure depletion
    pressure = kpis.get("avg_pressure", 0)
    if pressure > 0:
        if pressure < 2500:
            alerts.append(Alert("crit", "⚠ CRITICAL PRESSURE",
                f"Average reservoir pressure at {pressure:,.0f} psi — consider pressure maintenance."))
        elif pressure < 3200:
            alerts.append(Alert("warn", "⚡ PRESSURE DECLINING",
                f"Reservoir pressure at {pressure:,.0f} psi — monitor depletion trend."))
        else:
            alerts.append(Alert("ok", "✓ PRESSURE NORMAL",
                f"Average reservoir pressure maintained at {pressure:,.0f} psi."))

    # Water cut
    wc = kpis.get("water_cut", 0)
    if wc > 60:
        alerts.append(Alert("crit", "⚠ HIGH WATER CUT",
            f"Water cut at {wc:.1f}% — review water handling and injection strategy."))
    elif wc > 35:
        alerts.append(Alert("warn", "⚡ ELEVATED WATER CUT",
            f"Water cut trending at {wc:.1f}% — monitor for breakthrough."))

    # Production trend (check if declining)
    if not prod_df.empty and "Date" in prod_df.columns and "Oil_Rate" in prod_df.columns:
        recent = (prod_df.sort_values("Date").tail(6)
                  .groupby("Date")["Oil_Rate"].sum().values)
        if len(recent) >= 4:
            trend = np.polyfit(range(len(recent)), recent, 1)[0]
            if trend < -50:
                alerts.append(Alert("warn", "📉 DECLINING PRODUCTION",
                    f"Oil rate declining ~{abs(trend):.0f} bbl/d per period. Assess workover candidates."))
            elif trend > 50:
                alerts.append(Alert("ok", "📈 PRODUCTION INCREASING",
                    f"Positive production trend: +{trend:.0f} bbl/d per period."))

    return alerts[:6]  # max 6 alerts


def generate_insights(kpis: dict, prod_df: pd.DataFrame,
                       res_df: pd.DataFrame, wells_df: pd.DataFrame,
                       reservoir: str, well: str) -> List[Insight]:
    """Generate AI-like operational insights."""
    insights = []

    scope = reservoir if reservoir != "Show All" else "field-wide"

    # Production rate insight
    oil = kpis.get("oil_rate", 0)
    gas = kpis.get("gas_rate", 0)
    if oil > 0 or gas > 0:
        insights.append(Insight(
            f"Current {scope} production: "
            f"<b>{oil:,.0f} bbl/d</b> oil, <b>{gas:,.1f} MMscfd</b> gas. "
            f"{'Gas production dominant — verify separator efficiency.' if gas > oil*0.5 else 'Oil-dominated production profile.'}", "🛢️"))

    # Well status insight
    producing = kpis.get("producing_wells", 0)
    shutin = kpis.get("shutin_wells", 0)
    total = kpis.get("total_wells", 0)
    if total > 0:
        insights.append(Insight(
            f"<b>{producing}</b> active well(s), <b>{shutin}</b> shut-in. "
            f"{'Recommend workover assessment for shut-in wells.' if shutin > 0 else 'All wells operational — no immediate workover required.'}",
            "⚙️"))

    # Reservoir pressure insight
    pressure = kpis.get("avg_pressure", 0)
    porosity = kpis.get("avg_porosity", 0)
    if pressure > 0:
        insights.append(Insight(
            f"Reservoir pressure at <b>{pressure:,.0f} psi</b>"
            + (f" with avg porosity <b>{porosity:.1f}%</b>" if porosity > 0 else "")
            + ". " + ("Pressure maintenance program may be required." if pressure < 3000 else "Reservoir energy is adequate for natural flow."),
            "📊"))

    # Water/gas ratio trend
    wc = kpis.get("water_cut", 0)
    gor = kpis.get("gor", 0)
    if wc > 0 or gor > 0:
        insights.append(Insight(
            f"Water cut <b>{wc:.1f}%</b>"
            + (f", GOR <b>{gor:,.0f} scf/bbl</b>" if gor > 0 else "")
            + ". " + ("Review water injection pattern — high WC may indicate channeling." if wc > 40 else "Fluid ratios within acceptable range."),
            "💧"))

    # Cumulative production context
    cum_oil = kpis.get("cum_oil", 0)
    if cum_oil > 0:
        insights.append(Insight(
            f"Cumulative oil production: <b>{cum_oil:,.0f} MBO</b>. "
            f"{'Strong field history — consider mature field redevelopment strategies.' if cum_oil > 50000 else 'Field in early-to-mid production life.'}",
            "📦"))

    # Well selection context
    if well != "Show All Wells":
        insights.append(Insight(
            f"Analysis scoped to well <b>{well}</b>. Field-wide performance may differ. "
            f"Compare against offset wells for diagnostic insight.",
            "🔩"))

    return insights[:5]


def render_alerts_html(alerts: List[Alert]) -> str:
    """Convert alerts list to HTML."""
    if not alerts:
        return '<div class="alert-item alert-info">No active alerts.</div>'
    return "\n".join(
        f'<div class="alert-item alert-{a.level}"><b>{a.title}</b><br>{a.message}</div>'
        for a in alerts
    )


def render_insights_html(insights: List[Insight]) -> str:
    """Convert insights list to HTML."""
    if not insights:
        return '<div class="insight-item">No insights available — upload data to generate analysis.</div>'
    return "\n".join(
        f'<div class="insight-item">{i.icon} {i.text}</div>'
        for i in insights
    )
