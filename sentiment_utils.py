"""
sentiment_utils.py
Utility functions for sentiment analysis using TextBlob.
"""

import nltk
from textblob import TextBlob
import pandas as pd

# Download required NLTK data silently
def download_nltk_data():
    packages = ["punkt", "punkt_tab", "averaged_perceptron_tagger",
                 "averaged_perceptron_tagger_eng", "brown", "wordnet", "stopwords"]
    for pkg in packages:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

download_nltk_data()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a text using TextBlob.
    Returns polarity, subjectivity, and a sentiment label.
    """
    blob = TextBlob(str(text))
    polarity = blob.sentiment.polarity        # -1.0 (negative) to +1.0 (positive)
    subjectivity = blob.sentiment.subjectivity  # 0.0 (objective) to 1.0 (subjective)

    if polarity > 0.15:
        label = "Positive"
    elif polarity < -0.10:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "polarity": round(polarity, 4),
        "subjectivity": round(subjectivity, 4),
        "sentiment_label": label,
    }


def enrich_dataframe(df: pd.DataFrame, text_col: str = "review") -> pd.DataFrame:
    """
    Add sentiment columns to a DataFrame.
    """
    df = df.copy()
    results = df[text_col].apply(analyze_sentiment).apply(pd.Series)
    df = pd.concat([df, results], axis=1)

    # Polarity bucket for bar chart
    df["polarity_bucket"] = pd.cut(
        df["polarity"],
        bins=[-1.01, -0.1, 0.15, 1.01],
        labels=["Negative", "Neutral", "Positive"],
    )
    return df


def get_keywords(text_series: pd.Series, top_n: int = 30) -> dict:
    """
    Extract and count frequent meaningful words from a Series of texts.
    Returns a dict {word: count}.
    """
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words("english"))
    extra_stop = {"product", "would", "also", "really", "bit", "one", "get", "got",
                  "use", "used", "using", "could", "every", "even", "though"}
    stop_words |= extra_stop

    word_freq: dict = {}
    for text in text_series.dropna():
        blob = TextBlob(str(text).lower())
        for word in blob.words:
            if len(word) > 3 and word.isalpha() and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_words[:top_n])
