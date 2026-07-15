"""
utils/sentiment.py
------------------
TextBlob-based sentiment analysis helpers.
"""

import nltk
import pandas as pd
from textblob import TextBlob


# ── Download required NLTK corpora once ───────────────────────────────────────
def _download_nltk_data() -> None:
    packages = [
        "punkt",
        "punkt_tab",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "brown",
        "wordnet",
        "stopwords",
    ]
    for pkg in packages:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass


_download_nltk_data()


# ── Core sentiment function ────────────────────────────────────────────────────
def analyze_sentiment(text: str) -> dict:
    """
    Analyse a single piece of text with TextBlob.

    Returns
    -------
    dict with keys:
        polarity      float  -1.0 (very negative) → +1.0 (very positive)
        subjectivity  float   0.0 (objective)      →  1.0 (subjective)
        sentiment_label  str  'Positive' | 'Neutral' | 'Negative'
    """
    blob = TextBlob(str(text))
    polarity     = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.15:
        label = "Positive"
    elif polarity < -0.10:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "polarity":        round(polarity, 4),
        "subjectivity":    round(subjectivity, 4),
        "sentiment_label": label,
    }


# ── DataFrame enrichment ───────────────────────────────────────────────────────
def enrich_dataframe(df: pd.DataFrame, text_col: str = "review") -> pd.DataFrame:
    """
    Add polarity, subjectivity, sentiment_label, and polarity_bucket
    columns to *df* by running TextBlob on *text_col*.

    Parameters
    ----------
    df       : input DataFrame (not mutated)
    text_col : name of the column containing review text

    Returns
    -------
    A new DataFrame with four extra columns.
    """
    df = df.copy()

    sentiment_cols = (
        df[text_col]
        .apply(analyze_sentiment)
        .apply(pd.Series)
    )
    df = pd.concat([df, sentiment_cols], axis=1)

    df["polarity_bucket"] = pd.cut(
        df["polarity"],
        bins=[-1.01, -0.10, 0.15, 1.01],
        labels=["Negative", "Neutral", "Positive"],
    )

    return df
