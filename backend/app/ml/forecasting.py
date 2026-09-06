"""Time-Series Forecasting.

Weighted linear-trend extrapolation over recent history stands in for
LSTM/Prophet: with only weeks of per-user data available (not the months of
history those models need to beat a trend line), a transparent trend
projection is both cheaper and more honest about its confidence. Swap in a
real Prophet/LSTM model behind `project_forward` once enough longitudinal
data has accumulated per user.
"""
import numpy as np


def project_forward(history: list[float], steps_ahead: int, min_value: float = 0, max_value: float = 100) -> list[float]:
    """Project `steps_ahead` future points from a numeric history series.

    Falls back to flat continuation of the last value when history is too
    short to fit a trend line.
    """
    if not history:
        return [50.0] * steps_ahead

    if len(history) < 3:
        last = history[-1]
        return [float(np.clip(last, min_value, max_value))] * steps_ahead

    x = np.arange(len(history))
    y = np.array(history)
    slope, intercept = np.polyfit(x, y, 1)

    # Dampen the slope over the horizon so long projections don't run away
    # linearly forever (diminishing-momentum assumption).
    future_x = np.arange(len(history), len(history) + steps_ahead)
    damping = np.linspace(1.0, 0.6, steps_ahead)
    projected = intercept + slope * future_x * damping

    return [float(np.clip(v, min_value, max_value)) for v in projected]


def trend_direction(history: list[float]) -> str:
    if len(history) < 2:
        return "stable"
    slope = np.polyfit(np.arange(len(history)), np.array(history), 1)[0]
    if slope > 0.5:
        return "improving"
    if slope < -0.5:
        return "declining"
    return "stable"
