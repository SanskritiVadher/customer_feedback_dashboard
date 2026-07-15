"""
utils/rootcause.py
-------------------
Root-cause bucketing for negative feedback + Priority Score.
"""
import pandas as pd

# Keyword → root-cause bucket. Edit freely to match your dataset's vocabulary.
ROOT_CAUSE_MAP = {
    "Delivery/Shipping": ["delivery", "shipping", "late", "delayed", "arrived", "package"],
    "Product Quality":   ["broken", "defect", "quality", "damaged", "faulty", "poor"],
    "Billing/Pricing":   ["price", "charge", "billing", "refund", "expensive", "cost"],
    "Customer Service":  ["service", "support", "rude", "response", "staff", "help"],
    "Usability":         ["confusing", "difficult", "complicated", "interface", "hard"],
}

def assign_root_cause(review: str) -> str:
    """Tag a single review with the first matching root-cause bucket."""
    text = str(review).lower()
    for bucket, keywords in ROOT_CAUSE_MAP.items():
        if any(kw in text for kw in keywords):
            return bucket
    return "Other"


def build_priority_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the enriched dataframe (needs 'polarity_bucket' and 'review'
    columns) and returns a Priority Score table for negative feedback.
    """
    neg = df[df["polarity_bucket"] == "Negative"].copy()
    neg["root_cause"] = neg["review"].apply(assign_root_cause)

    # Recency weight: more recent complaints score higher (last 30 days = full weight)
    max_date = df["date"].max()
    neg["days_ago"] = (max_date - neg["date"]).dt.days
    neg["recency_weight"] = neg["days_ago"].apply(lambda d: 1.0 if d <= 30 else 0.5)

    summary = (
        neg.groupby("root_cause")
        .agg(
            volume=("review", "count"),
            avg_polarity=("polarity", "mean"),
            recency_weight=("recency_weight", "mean"),
        )
        .reset_index()
    )
    # Severity: more negative polarity = higher severity (flip sign, normalize 0-1)
    summary["severity"] = (summary["avg_polarity"].min() - summary["avg_polarity"]) / (
        summary["avg_polarity"].min() - summary["avg_polarity"].max() + 1e-9
    ) if summary["avg_polarity"].nunique() > 1 else 0.5

    summary["priority_score"] = (
        summary["volume"] * summary["severity"] * summary["recency_weight"]
    ).round(2)

    return summary.sort_values("priority_score", ascending=False).reset_index(drop=True)