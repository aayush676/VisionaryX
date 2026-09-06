"""Burnout Prediction.

A small RandomForestRegressor trained on synthetically generated seed data
(labels built from a domain-expert formula + Gaussian noise) stands in for a
production model that would otherwise need months of real longitudinal user
data to train responsibly. This keeps the "lightweight ML" promise: real
scikit-learn inference, no heavy training pipeline or external dataset
required to get the app running.
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor

_FEATURES = ["sleep_hours", "screen_time_hours", "study_hours", "consistency", "fitness_minutes"]
_model: RandomForestRegressor | None = None


def _synthetic_formula(sleep, screen_time, study, consistency, fitness) -> float:
    risk = (
        (8 - sleep) * 6.5
        + screen_time * 3.2
        + max(0, study - 6) * 4.0
        + (100 - consistency) * 0.25
        - fitness * 0.15
    )
    return float(np.clip(risk, 0, 100))


def _train() -> RandomForestRegressor:
    rng = np.random.default_rng(42)
    n = 800
    sleep = rng.uniform(3, 9, n)
    screen_time = rng.uniform(1, 12, n)
    study = rng.uniform(0, 12, n)
    consistency = rng.uniform(0, 100, n)
    fitness = rng.uniform(0, 90, n)

    X = np.column_stack([sleep, screen_time, study, consistency, fitness])
    y = np.array([
        _synthetic_formula(*row) + rng.normal(0, 4)
        for row in X
    ])
    y = np.clip(y, 0, 100)

    model = RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42)
    model.fit(X, y)
    return model


def _get_model() -> RandomForestRegressor:
    global _model
    if _model is None:
        _model = _train()
    return _model


def predict_burnout_risk(sleep_hours: float, screen_time_hours: float, study_hours: float,
                          consistency: float, fitness_minutes: float) -> float:
    model = _get_model()
    X = np.array([[sleep_hours, screen_time_hours, study_hours, consistency, fitness_minutes]])
    return round(float(np.clip(model.predict(X)[0], 0, 100)), 1)
