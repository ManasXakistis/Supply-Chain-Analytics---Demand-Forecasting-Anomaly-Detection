"""Error metrics and confidence-interval helpers shared across the dashboard.

These mirror the formulas used in the Week 3 notebooks so the app reports the
same numbers the models were evaluated with.
"""
import numpy as np

# z-scores for common two-sided confidence levels, used to turn a residual
# standard deviation into a +/- band around a point forecast.
Z_SCORES = {80: 1.28, 85: 1.44, 90: 1.645, 95: 1.96, 99: 2.576}


def mape(actual, predicted) -> float:
    """Mean Absolute Percentage Error (%), ignoring rows where actual == 0."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mask = actual != 0
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def rmse(actual, predicted) -> float:
    """Root Mean Squared Error, in the same units as the target."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))


def confidence_band(forecast, actual, confidence_level: int):
    """Build a +/- band around ``forecast`` sized from its own residual std.

    Using the residual std observed over the backtest window (rather than a
    fixed percentage of the forecast) means the band reflects how reliable
    *this* model actually was for *this* category, not a generic guess.
    Returns ``(lower, upper)`` arrays.
    """
    forecast = np.asarray(forecast, dtype=float)
    actual = np.asarray(actual, dtype=float)
    resid_std = float(np.std(actual - forecast, ddof=1)) if len(forecast) > 1 else 0.0
    z = Z_SCORES.get(confidence_level, 1.96)
    lower = forecast - z * resid_std
    upper = forecast + z * resid_std
    return lower, upper
