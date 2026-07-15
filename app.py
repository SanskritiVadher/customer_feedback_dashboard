"""
app.py
------
Customer Feedback Dashboard
Powered by  Streamlit · Plotly · TextBlob

Run:
    streamlit run app.py
"""

import io
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ── Local utils package ────────────────────────────────────────────────────────
from utils.sentiment import enrich_dataframe
from utils.keywords  import get_keywords
from utils.rootcause import build_priority_table


# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Customer Feedback Dashboard",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* KPI metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #2e3557;
        border-radius: 12px;
        padding: 18px 24px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.78rem !important;
        color: #8892b0 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        font-size: 2rem !important;
        font-weight: 700;
        color: #e2e8f0 !important;
    }

    /* Section headers */
    .section-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: #a5b4fc;
        letter-spacing: 0.04em;
        margin-bottom: 0.4rem;
        padding-bottom: 6px;
        border-bottom: 1px solid #2e3557;
    }

    /* Sentiment badges */
    .badge-positive { background:#14532d; color:#86efac; padding:3px 10px;
                      border-radius:20px; font-size:0.78rem; font-weight:600; }
    .badge-neutral  { background:#1e3a5f; color:#93c5fd; padding:3px 10px;
                      border-radius:20px; font-size:0.78rem; font-weight:600; }
    .badge-negative { background:#450a0a; color:#fca5a5; padding:3px 10px;
                      border-radius:20px; font-size:0.78rem; font-weight:600; }

    /* Review cards */
    .review-card {
        background: #1a1f35;
        border: 1px solid #2e3557;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .review-meta { color: #8892b0; font-size: 0.8rem; margin-bottom: 6px; }
    .review-text { color: #cbd5e1; font-size: 0.92rem; line-height: 1.55; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #141824;
        border-right: 1px solid #2e3557;
    }

    hr { border-color: #2e3557; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
SENTIMENT_COLORS = {
    "Positive": "#4ade80",
    "Neutral":  "#60a5fa",
    "Negative": "#f87171",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_color   ="#cbd5e1",
    font_family  ="Inter, sans-serif",
    margin       =dict(l=20, r=20, t=40, b=20),
)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def star_rating(n: float) -> str:
    full = int(round(n))
    return "★" * full + "☆" * (5 - full)


def sentiment_badge(label: str) -> str:
    cls = f"badge-{label.lower()}"
    return f'<span class="{cls}">{label}</span>'


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING  (cached so re-runs are instant)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Analysing feedback with TextBlob…")
def load_data(uploaded_file):
    if uploaded_file is None:
        df = pd.read_csv("data/feedback.csv")
    else:
        df = pd.read_csv(uploaded_file)

    df["date"] = pd.to_datetime(df["date"])
    df = enrich_dataframe(df, text_col="review")   # ← utils/sentiment.py
    priority_df = build_priority_table(df)          # ← utils/rootcause.py
    return df, priority_df


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  — upload + filters
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 💬 Feedback Dashboard")
    st.caption("Sentiment · Trends · Insights")
    st.divider()

    uploaded = st.file_uploader(
        "Upload your own CSV",
        type=["csv"],
        help="Required columns: date, customer_name, product, rating, review, category",
    )
    st.divider()

    df_raw, priority_df = load_data(uploaded)

    st.markdown("### Filters")

    categories = ["All"] + sorted(df_raw["category"].unique().tolist())
    sel_cat = st.selectbox("Category", categories)

    sel_sent = st.selectbox("Sentiment", ["All", "Positive", "Neutral", "Negative"])

    rating_range = st.slider("Rating range", 1, 5, (1, 5))

    date_min = df_raw["date"].min().date()
    date_max = df_raw["date"].max().date()
    date_range = st.date_input(
        "Date range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    st.divider()
    st.caption("Built with Streamlit · Plotly · TextBlob")


# ══════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS
# ══════════════════════════════════════════════════════════════════════════════
df = df_raw.copy()

if sel_cat != "All":
    df = df[df["category"] == sel_cat]
if sel_sent != "All":
    df = df[df["sentiment_label"] == sel_sent]

df = df[df["rating"].between(*rating_range)]

if len(date_range) == 2:
    df = df[
        (df["date"].dt.date >= date_range[0]) &
        (df["date"].dt.date <= date_range[1])
    ]


# ══════════════════════════════════════════════════════════════════════════════
# TITLE BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📊 Customer Feedback Dashboard")
st.markdown(
    f"Showing **{len(df)}** reviews  ·  "
    f"Avg rating **{df['rating'].mean():.2f} / 5**  ·  "
    f"Avg polarity **{df['polarity'].mean():+.3f}**"
)
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4, k5 = st.columns(5)

pos_pct = (df["sentiment_label"] == "Positive").mean() * 100
neg_pct = (df["sentiment_label"] == "Negative").mean() * 100

k1.metric("📝 Total Reviews",  len(df))
k2.metric("⭐ Avg Rating",     f"{df['rating'].mean():.2f}")
k3.metric("😊 Positive",       f"{pos_pct:.0f}%")
k4.metric("😞 Negative",       f"{neg_pct:.0f}%")
k5.metric("🎯 Avg Polarity",   f"{df['polarity'].mean():+.3f}")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — Sentiment pie  |  Rating bar
# ══════════════════════════════════════════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Sentiment Distribution</div>', unsafe_allow_html=True)

    sent_counts = df["sentiment_label"].value_counts().reset_index()
    sent_counts.columns = ["Sentiment", "Count"]

    fig_pie = px.pie(
        sent_counts, names="Sentiment", values="Count",
        color="Sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        hole=0.45,
    )
    fig_pie.update_traces(
        textinfo="label+percent",
        textfont_size=13,
        marker=dict(line=dict(color="#0f1117", width=2)),
    )
    fig_pie.update_layout(**PLOTLY_LAYOUT, showlegend=False, height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Rating Distribution</div>', unsafe_allow_html=True)

    rating_counts = df["rating"].value_counts().sort_index().reset_index()
    rating_counts.columns = ["Rating", "Count"]

    fig_bar = px.bar(
        rating_counts, x="Rating", y="Count",
        color="Count",
        color_continuous_scale=["#f87171", "#fb923c", "#facc15", "#4ade80", "#22d3ee"],
        text="Count",
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_showscale=False,
        height=300,
        xaxis_title="Star Rating",
        yaxis_title="Number of Reviews",
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — Polarity over time  |  Avg rating by category
# ══════════════════════════════════════════════════════════════════════════════
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-header">Sentiment Polarity Over Time</div>', unsafe_allow_html=True)

    df_time = (
        df.set_index("date")
        .resample("W")["polarity"]
        .mean()
        .reset_index()
    )
    df_time.columns = ["Date", "Avg Polarity"]

    fig_line = px.area(
        df_time, x="Date", y="Avg Polarity",
        color_discrete_sequence=["#818cf8"],
        line_shape="spline",
    )
    fig_line.update_traces(fillcolor="rgba(129,140,248,0.15)")
    fig_line.add_hline(y=0, line_dash="dash", line_color="#f87171", opacity=0.6)
    fig_line.update_layout(
        **PLOTLY_LAYOUT,
        height=300,
        yaxis_title="Avg Polarity",
        yaxis_range=[-1, 1],
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col4:
    st.markdown('<div class="section-header">Avg Rating by Category</div>', unsafe_allow_html=True)

    cat_stats = (
        df.groupby("category")
        .agg(Avg_Rating=("rating", "mean"), Avg_Polarity=("polarity", "mean"))
        .reset_index()
        .sort_values("Avg_Rating", ascending=True)
    )

    fig_cat = px.bar(
        cat_stats, x="Avg_Rating", y="category", orientation="h",
        color="Avg_Polarity",
        color_continuous_scale=["#f87171", "#facc15", "#4ade80"],
        color_continuous_midpoint=0,
        text=cat_stats["Avg_Rating"].apply(lambda v: f"{v:.2f}"),
    )
    fig_cat.update_traces(textposition="outside")
    fig_cat.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_showscale=False,
        height=300,
        xaxis_title="Avg Rating",
        yaxis_title="",
        xaxis_range=[0, 5.8],
    )
    st.plotly_chart(fig_cat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — Scatter (polarity vs subjectivity)  |  Sentiment × category
# ══════════════════════════════════════════════════════════════════════════════
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-header">Polarity vs Subjectivity</div>', unsafe_allow_html=True)

    fig_scatter = px.scatter(
        df, x="polarity", y="subjectivity",
        color="sentiment_label",
        color_discrete_map=SENTIMENT_COLORS,
        size="rating",
        hover_data=["customer_name", "product", "rating"],
        opacity=0.8,
    )
    fig_scatter.add_vline(x=0,   line_dash="dash", line_color="#475569", opacity=0.5)
    fig_scatter.add_hline(y=0.5, line_dash="dash", line_color="#475569", opacity=0.5)
    fig_scatter.update_layout(
        **PLOTLY_LAYOUT,
        height=320,
        xaxis_title="Polarity  (Neg ← → Pos)",
        yaxis_title="Subjectivity  (Obj ← → Subj)",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col6:
    st.markdown('<div class="section-header">Sentiment Breakdown by Category</div>', unsafe_allow_html=True)

    sent_cat = (
        df.groupby(["category", "sentiment_label"])
        .size()
        .reset_index(name="Count")
    )
    fig_group = px.bar(
        sent_cat, x="category", y="Count", color="sentiment_label",
        color_discrete_map=SENTIMENT_COLORS,
        barmode="group",
    )
    fig_group.update_layout(
        **PLOTLY_LAYOUT,
        height=320,
        xaxis_title="Category",
        yaxis_title="Count",
        legend_title="Sentiment",
    )
    st.plotly_chart(fig_group, use_container_width=True)

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# ROOT-CAUSE PRIORITY RANKING  (utils/rootcause.py)  ← NEW SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">🎯 Root-Cause Priority Ranking</div>', unsafe_allow_html=True)
st.caption("Negative feedback grouped by root cause, ranked by Priority Score = volume × severity × recency")

if not priority_df.empty:
    pcol1, pcol2 = st.columns([1.3, 1])

    with pcol1:
        st.dataframe(
            priority_df.rename(columns={
                "root_cause": "Root Cause",
                "volume": "Volume",
                "avg_polarity": "Avg Polarity",
                "recency_weight": "Recency Weight",
                "severity": "Severity",
                "priority_score": "Priority Score",
            }).style.background_gradient(subset=["Priority Score"], cmap="Reds"),
            use_container_width=True,
            hide_index=True,
        )

    with pcol2:
        fig_priority = px.bar(
            priority_df.sort_values("priority_score"),
            x="priority_score", y="root_cause", orientation="h",
            color="priority_score",
            color_continuous_scale=["#facc15", "#f87171", "#7f1d1d"],
            text=priority_df.sort_values("priority_score")["priority_score"].apply(lambda v: f"{v:.1f}"),
        )
        fig_priority.update_traces(textposition="outside")
        fig_priority.update_layout(
            **PLOTLY_LAYOUT,
            coloraxis_showscale=False,
            height=320,
            xaxis_title="Priority Score",
            yaxis_title="",
        )
        st.plotly_chart(fig_priority, use_container_width=True)

    top_cause = priority_df.iloc[0]
    st.info(
        f"**Recommendation:** *{top_cause['root_cause']}* has the highest priority score "
        f"({top_cause['priority_score']:.1f}) — driven by {int(top_cause['volume'])} complaints "
        f"with an average polarity of {top_cause['avg_polarity']:+.2f}. This should be the "
        f"first area addressed."
    )
else:
    st.info("No negative feedback in the current filter selection to analyse.")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# WORD CLOUD  (utils/keywords.py)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">Top Keywords in Reviews</div>', unsafe_allow_html=True)

keywords = get_keywords(df["review"], top_n=50)   # ← utils/keywords.py

if keywords:
    wc = WordCloud(
        width=1400, height=360,
        background_color="#1a1f35",
        colormap="cool",
        max_words=60,
        collocations=False,
        prefer_horizontal=0.7,
    ).generate_from_frequencies(keywords)

    fig_wc, ax = plt.subplots(figsize=(14, 3.5))
    fig_wc.patch.set_facecolor("#1a1f35")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc, use_container_width=True)
    plt.close(fig_wc)
else:
    st.info("Not enough text data to generate a word cloud.")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT LEADERBOARD  (dual-axis)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">Product Leaderboard</div>', unsafe_allow_html=True)

prod_stats = (
    df.groupby("product")
    .agg(
        Reviews      =("review",  "count"),
        Avg_Rating   =("rating",  "mean"),
        Avg_Polarity =("polarity","mean"),
    )
    .reset_index()
    .sort_values("Avg_Rating", ascending=False)
)

fig_lb = go.Figure()
fig_lb.add_trace(go.Bar(
    name="Avg Rating",
    x=prod_stats["product"],
    y=prod_stats["Avg_Rating"],
    marker_color="#818cf8",
    yaxis="y",
))
fig_lb.add_trace(go.Scatter(
    name="Avg Polarity",
    x=prod_stats["product"],
    y=prod_stats["Avg_Polarity"],
    mode="lines+markers",
    marker=dict(color="#4ade80", size=8),
    line=dict(color="#4ade80", width=2),
    yaxis="y2",
))
fig_lb.update_layout(
    **PLOTLY_LAYOUT,
    height=340,
    yaxis  =dict(title="Avg Rating",   range=[0, 5.5], color="#818cf8"),
    yaxis2 =dict(title="Avg Polarity", overlaying="y", side="right",
                 range=[-1, 1], color="#4ade80"),
    legend =dict(orientation="h", x=0, y=1.12),
    xaxis_tickangle=-35,
)
st.plotly_chart(fig_lb, use_container_width=True)

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# INDIVIDUAL REVIEW CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">Customer Reviews</div>', unsafe_allow_html=True)

sort_options = {
    "Date (newest first)":       ("date",     False),
    "Rating (high → low)":       ("rating",   False),
    "Rating (low → high)":       ("rating",   True),
    "Polarity (high → low)":     ("polarity", False),
    "Polarity (low → high)":     ("polarity", True),
}
sort_choice = st.selectbox("Sort by", list(sort_options.keys()))
sort_col, sort_asc = sort_options[sort_choice]

df_sorted = df.sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)

for _, row in df_sorted.head(10).iterrows():
    badge = sentiment_badge(row["sentiment_label"])
    stars = star_rating(row["rating"])
    st.markdown(f"""
    <div class="review-card">
        <div class="review-meta">
            <strong style="color:#e2e8f0">{row['customer_name']}</strong>
            &nbsp;·&nbsp; {row['product']}
            &nbsp;·&nbsp; <span style="color:#facc15">{stars}</span>
            &nbsp;·&nbsp; {row['date'].strftime('%b %d, %Y')}
            &nbsp;·&nbsp; {badge}
            &nbsp;·&nbsp; <span style="color:#8892b0">Polarity: {row['polarity']:+.3f} &nbsp;|&nbsp;
                           Subjectivity: {row['subjectivity']:.3f}</span>
        </div>
        <div class="review-text">{row['review']}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">Export Analysed Data</div>', unsafe_allow_html=True)

export_cols = [
    "date", "customer_name", "product", "category",
    "rating", "review", "polarity", "subjectivity", "sentiment_label",
]
csv_buf = io.StringIO()
df[export_cols].to_csv(csv_buf, index=False)

st.download_button(
    label="⬇️  Download CSV with Sentiment Scores",
    data=csv_buf.getvalue().encode(),
    file_name="feedback_with_sentiment.csv",
    mime="text/csv",
)