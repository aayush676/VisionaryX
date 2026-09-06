"""Goal Completion Prediction.

LogisticRegression trained on synthetic seed data mapping goal-progress
signals to a completion outcome. Same rationale as burnout_model.py: real
scikit-learn inference without requiring a historical dataset that doesn't
exist yet for a new product.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

_model: LogisticRegression | None = None


def _synthetic_label_prob(progress, days_remaining, consistency, streak_days) -> float:
    days_remaining = max(days_remaining, 1)
    momentum = (progress / 100) * 0.5 + (consistency / 100) * 0.3 + min(streak_days / 30, 1) * 0.2
    urgency_penalty = max(0, (30 - days_remaining) / 30) * 0.15 if days_remaining < 30 else 0
    return float(np.clip(momentum - urgency_penalty, 0, 1))


def _train() -> LogisticRegression:
    rng = np.random.default_rng(7)
    n = 1000
    progress = rng.uniform(0, 100, n)
    days_remaining = rng.uniform(1, 180, n)
    consistency = rng.uniform(0, 100, n)
    streak_days = rng.uniform(0, 60, n)

    X = np.column_stack([progress, days_remaining, consistency, streak_days])
    probs = np.array([_synthetic_label_prob(*row) for row in X])
    y = (rng.uniform(0, 1, n) < probs).astype(int)

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model


def _get_model() -> LogisticRegression:
    global _model
    if _model is None:
        _model = _train()
    return _model


def predict_goal_success_probability(progress: float, days_remaining: float,
                                      consistency: float, streak_days: float) -> float:
    model = _get_model()
    X = np.array([[progress, max(days_remaining, 1), consistency, streak_days]])
    proba = model.predict_proba(X)[0][1]
    return round(float(proba) * 100, 1)
