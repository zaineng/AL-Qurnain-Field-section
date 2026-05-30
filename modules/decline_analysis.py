"""
modules/decline_analysis.py — Automatic decline curve fitting & forecasting
Supports: Exponential, Harmonic, Hyperbolic
Auto-selects best fit by R²
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings("ignore")

try:
    from scipy.optimize import curve_fit
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# ── Decline model functions ────────────────────────────────────────────────────

def _exp(t, qi, Di):
    """Exponential: q = qi * e^(-Di*t)"""
    return qi * np.exp(-Di * t)

def _harm(t, qi, Di):
    """Harmonic: q = qi / (1 + Di*t)"""
    return qi / (1.0 + Di * t)

def _hyp(t, qi, Di, b):
    """Hyperbolic: q = qi*(1+b*Di*t)^(-1/b)"""
    b = np.clip(b, 1e-4, 0.9999)
    return qi * (1.0 + b * Di * t) ** (-1.0 / b)


def _r_squared(y_actual, y_pred) -> float:
    ss_res = np.sum((y_actual - y_pred) ** 2)
    ss_tot = np.sum((y_actual - np.mean(y_actual)) ** 2)
    if ss_tot == 0:
        return 0.0
    return float(1.0 - ss_res / ss_tot)


# ── EUR integration ────────────────────────────────────────────────────────────

def _eur_exp(qi, Di, t_life=60):
    if Di <= 0:
        return qi * t_life
    return qi / Di * (1 - np.exp(-Di * t_life))

def _eur_harm(qi, Di, t_life=60):
    if Di <= 0:
        return qi * t_life
    return qi / Di * np.log(1 + Di * t_life)

def _eur_hyp(qi, Di, b, t_life=60):
    b = np.clip(b, 1e-4, 0.9999)
    if Di <= 0:
        return qi * t_life
    return (qi / ((1 - b) * Di)) * (1 - (1 + b * Di * t_life) ** (-(1 - b) / b))


# ── Main fitting engine ────────────────────────────────────────────────────────

@dataclass
class DeclineResult:
    decline_type:    str    = "Unknown"
    qi:              float  = 0.0
    Di:              float  = 0.0
    b:               float  = 0.0          # hyperbolic only
    r2:              float  = 0.0
    eur:             float  = 0.0          # months of forecast
    remaining_res:   float  = 0.0
    cum_actual:      float  = 0.0
    forecast_t:      np.ndarray = field(default_factory=lambda: np.array([]))
    forecast_q:      np.ndarray = field(default_factory=lambda: np.array([]))
    all_fits:        Dict[str, Any] = field(default_factory=dict)
    error:           str    = ""


def fit_decline(df: pd.DataFrame, rate_col: str = "Rate",
                date_col: str = "Date",
                forecast_months: int = 60) -> DeclineResult:
    """
    Fit decline curves to production data.

    Parameters
    ----------
    df : DataFrame with date and rate columns
    rate_col : column name for production rate
    date_col : column name for dates
    forecast_months : how many months ahead to forecast

    Returns
    -------
    DeclineResult with best fit and forecast arrays
    """
    result = DeclineResult()

    if df.empty:
        result.error = "No data available"
        return result

    # Prepare data
    work = df[[date_col, rate_col]].copy().dropna()
    if len(work) < 4:
        result.error = "Insufficient data (< 4 points)"
        return result

    work = work.sort_values(date_col)
    work[rate_col] = pd.to_numeric(work[rate_col], errors="coerce")
    work = work[work[rate_col] > 0].dropna()

    if len(work) < 4:
        result.error = "Insufficient positive-rate data"
        return result

    # Convert dates → months from first point
    first_date = work[date_col].iloc[0]
    work["_t"] = ((work[date_col] - first_date).dt.days / 30.44).astype(float)

    t = work["_t"].values
    q = work[rate_col].values
    qi_guess = float(q[0])
    _trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz", None)
    result.cum_actual = float(_trapz(q, t))

    if not SCIPY_AVAILABLE:
        # Fallback: simple exponential via log-linear regression
        log_q = np.log(q + 1e-10)
        poly = np.polyfit(t, log_q, 1)
        Di_est = max(-poly[0], 1e-6)
        qi_est = np.exp(poly[1])
        result.decline_type = "Exponential"
        result.qi = qi_est
        result.Di = Di_est
        result.r2 = _r_squared(q, _exp(t, qi_est, Di_est))
        t_fc = np.arange(0, t[-1] + forecast_months + 1)
        result.forecast_t = t_fc
        result.forecast_q = _exp(t_fc, qi_est, Di_est)
        result.eur = _eur_exp(qi_est, Di_est, t[-1] + forecast_months)
        result.remaining_res = result.eur - result.cum_actual
        return result

    fits = {}

    # ── 1. Exponential ───────────────────────────────────────────────────
    try:
        popt, _ = curve_fit(
            _exp, t, q,
            p0=[qi_guess, 0.05],
            bounds=([qi_guess * 0.1, 1e-6], [qi_guess * 3, 2.0]),
            maxfev=8000
        )
        q_pred = _exp(t, *popt)
        r2 = _r_squared(q, q_pred)
        fits["Exponential"] = {
            "params": popt, "r2": r2,
            "eur": _eur_exp(popt[0], popt[1], t[-1] + forecast_months),
        }
    except Exception:
        pass

    # ── 2. Harmonic ──────────────────────────────────────────────────────
    try:
        popt, _ = curve_fit(
            _harm, t, q,
            p0=[qi_guess, 0.05],
            bounds=([qi_guess * 0.1, 1e-6], [qi_guess * 3, 2.0]),
            maxfev=8000
        )
        q_pred = _harm(t, *popt)
        r2 = _r_squared(q, q_pred)
        fits["Harmonic"] = {
            "params": popt, "r2": r2,
            "eur": _eur_harm(popt[0], popt[1], t[-1] + forecast_months),
        }
    except Exception:
        pass

    # ── 3. Hyperbolic ────────────────────────────────────────────────────
    try:
        popt, _ = curve_fit(
            _hyp, t, q,
            p0=[qi_guess, 0.05, 0.5],
            bounds=([qi_guess * 0.1, 1e-6, 0.01], [qi_guess * 3, 2.0, 0.99]),
            maxfev=8000
        )
        q_pred = _hyp(t, *popt)
        r2 = _r_squared(q, q_pred)
        fits["Hyperbolic"] = {
            "params": popt, "r2": r2,
            "eur": _eur_hyp(popt[0], popt[1], popt[2], t[-1] + forecast_months),
        }
    except Exception:
        pass

    if not fits:
        result.error = "Curve fitting failed for all decline types"
        return result

    # ── Select best fit ────────────────────────────────────────────────────
    best_name = max(fits, key=lambda k: fits[k]["r2"])
    best      = fits[best_name]
    params    = best["params"]

    result.decline_type = best_name
    result.r2           = best["r2"]
    result.eur          = best["eur"]
    result.qi           = float(params[0])
    result.Di           = float(params[1])
    result.b            = float(params[2]) if len(params) > 2 else 0.0
    result.all_fits     = fits
    result.remaining_res = max(0.0, result.eur - result.cum_actual)

    # ── Generate forecast arrays ───────────────────────────────────────────
    t_fc = np.linspace(0, t[-1] + forecast_months, 300)
    if best_name == "Exponential":
        q_fc = _exp(t_fc, result.qi, result.Di)
    elif best_name == "Harmonic":
        q_fc = _harm(t_fc, result.qi, result.Di)
    else:
        q_fc = _hyp(t_fc, result.qi, result.Di, result.b)

    result.forecast_t = t_fc
    result.forecast_q = q_fc

    # P10 / P90 scenarios (±15%)
    result.all_fits["_t_actual"] = t
    result.all_fits["_q_actual"] = q
    result.all_fits["_t_fc"]     = t_fc
    result.all_fits["_q_fc_p10"] = q_fc * 1.15
    result.all_fits["_q_fc_p90"] = q_fc * 0.85

    return result


def decline_summary_html(res: DeclineResult) -> str:
    """Return HTML for a mini stats row under the decline chart."""
    if res.error:
        return f'<div style="color:#ff4545;font-size:10px;font-family:Share Tech Mono,monospace">⚠ {res.error}</div>'
    color_map = {"Exponential": "#3aafff", "Harmonic": "#f5c542", "Hyperbolic": "#a87fff", "Unknown": "#8ab8d8"}
    c = color_map.get(res.decline_type, "#8ab8d8")
    items = [
        ("Type",        res.decline_type,      c),
        ("R²",          f"{res.r2:.4f}",        "#e8f4ff"),
        ("qi",          f"{res.qi:,.1f}",        "#2ecc71"),
        ("Di (mo⁻¹)",   f"{res.Di:.4f}",        "#ff9040"),
        ("EUR",         f"{res.eur:,.0f}",       "#3aafff"),
        ("Remaining",   f"{res.remaining_res:,.0f}", "#a87fff"),
    ]
    cells = "".join(
        f'<td style="padding:4px 10px;border-right:1px solid #0a1d35">'
        f'<div style="font-size:7.5px;color:#1a4a6a;font-family:Share Tech Mono,monospace;'
        f'text-transform:uppercase;letter-spacing:1px">{lbl}</div>'
        f'<div style="font-size:12px;font-weight:700;color:{col};font-family:Rajdhani,sans-serif">{val}</div>'
        f'</td>'
        for lbl, val, col in items
    )
    return (
        f'<table style="background:#071526;border:1px solid #0d2540;border-radius:8px;'
        f'border-collapse:collapse;width:100%;margin-top:6px">'
        f'<tr>{cells}</tr></table>'
    )
