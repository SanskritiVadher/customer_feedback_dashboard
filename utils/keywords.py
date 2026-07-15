"""
utils/keywords.py
-----------------
Keyword / word-frequency extraction from review text using TextBlob + NLTK.
"""

import pandas as pd
from textblob import TextBlob
from nltk.corpus import stopwords


# ── Stop-word set ──────────────────────────────────────────────────────────────
_BASE_STOP: set[str] = set()

try:
    _BASE_STOP = set(stopwords.words("english"))
except LookupError:
    import nltk
    nltk.download("stopwords", quiet=True)
    _BASE_STOP = set(stopwords.words("english"))

_EXTRA_STOP: set[str] = {
    "product", "would", "also", "really", "bit", "one",
    "get", "got", "use", "used", "using", "could", "every",
    "even", "though", "much", "good", "great", "like",
}

STOP_WORDS: set[str] = _BASE_STOP | _EXTRA_STOP


# ── Keyword extractor ─────────────────────────────────────────────────────────
def get_keywords(text_series: pd.Series, top_n: int = 50) -> dict[str, int]:
    """
    Count the most frequent meaningful words across all reviews.

    Parameters
    ----------
    text_series : pd.Series of raw review strings
    top_n       : how many top words to return

    Returns
    -------
    dict  { word: count }  sorted descending by count
    """
    word_freq: dict[str, int] = {}

    for text in text_series.dropna():
        blob = TextBlob(str(text).lower())
        for word in blob.words:
            if (
                len(word) > 3
                and word.isalpha()
                and word not in STOP_WORDS
            ):
                word_freq[word] = word_freq.get(word, 0) + 1

    sorted_items = sorted(word_freq.items(), key=lambda kv: kv[1], reverse=True)
    return dict(sorted_items[:top_n])
