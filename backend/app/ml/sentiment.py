"""Emotional Intelligence System.

Lightweight sentiment + emotion detection: VADER (lexicon-based, no heavy
model download) supplies an overall polarity score, and a keyword-weighted
layer maps journal text onto the six emotion dimensions the product tracks
(stress, burnout, focus, happiness, anxiety, motivation). This keeps the
service fast and dependency-light while still being real quantitative
analysis rather than a fixed lookup table.
"""
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

_EMOTION_KEYWORDS: dict[str, list[str]] = {
    "stress": ["stressed", "stress", "overwhelmed", "pressure", "deadline", "panic", "tense"],
    "burnout": ["burnout", "burnt out", "exhausted", "drained", "tired", "fatigue", "numb", "no motivation"],
    "focus": ["focused", "focus", "productive", "flow", "concentration", "deep work", "clarity"],
    "happiness": ["happy", "excited", "grateful", "proud", "joy", "great day", "accomplished", "relieved"],
    "anxiety": ["anxious", "anxiety", "worried", "nervous", "afraid", "scared", "uneasy", "doubt"],
    "motivation": ["motivated", "inspired", "determined", "driven", "ambitious", "goal", "excited to"],
}


def _keyword_score(text_lower: str, keywords: list[str]) -> float:
    hits = sum(len(re.findall(re.escape(kw), text_lower)) for kw in keywords)
    # Diminishing returns: first hit matters most, cap at 100.
    return min(100.0, hits * 22.0)


def analyze_journal_text(text: str) -> dict:
    text_lower = text.lower()
    vader_scores = _analyzer.polarity_scores(text)
    compound = vader_scores["compound"]  # -1..1

    emotions = {name: _keyword_score(text_lower, kws) for name, kws in _EMOTION_KEYWORDS.items()}

    # Blend VADER polarity into the affect-aligned dimensions so a purely
    # negative/positive entry still moves the needle even with no keyword hits.
    emotions["happiness"] = round(min(100.0, emotions["happiness"] + max(0.0, compound) * 60), 1)
    emotions["stress"] = round(min(100.0, emotions["stress"] + max(0.0, -compound) * 40), 1)
    emotions["anxiety"] = round(min(100.0, emotions["anxiety"] + max(0.0, -compound) * 30), 1)
    emotions["burnout"] = round(emotions["burnout"], 1)
    emotions["focus"] = round(emotions["focus"], 1)
    emotions["motivation"] = round(emotions["motivation"], 1)

    dominant_emotion = max(emotions, key=emotions.get) if any(emotions.values()) else "neutral"
    if all(v == 0 for v in emotions.values()):
        dominant_emotion = "positive" if compound > 0.2 else "negative" if compound < -0.2 else "neutral"

    return {
        "sentiment_score": round(compound, 3),
        "dominant_emotion": dominant_emotion,
        "emotions": emotions,
    }
