"""
Customer Feedback Dashboard
Powered by Streamlit · Plotly · TextBlob
"""

import io
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image

from sentiment_utils import enrich_dataframe, get_keywords

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Feedback Dashboard",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #0f1117; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Metric cards */
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
        font-size: 1.1rem;
        font-weight: 600;
        color: #a5b4fc;
        letter-spacing: 0.04em;
        margin-bottom: 0.5rem;
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

    /* Review card */
    .review-card {
        background: #1a1f35;
        border: 1px solid #2e3557;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .review-meta { color: #8892b0; font-size:0.8rem; margin-bottom:6px; }
    .review-text { color: #cbd5e1; font-size:0.92rem; line-height:1.55; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #141824;
        border-right: 1px solid #2e3557;
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #a5b4fc;
    }

    /* Divider */
    hr { border-color: #2e3557; }

    /* Plotly chart backgrounds match page */
    .js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
SENTIMENT_COLORS = {"Positive": "#4ade80", "Neutral": "#60a5fa", "Negative": "#f87171"}
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#cbd5e1",
    font_family="Inter, sans-serif",
    margin=dict(l=20, r=20, t=40, b=20),
)

def star_rating(n: float) -> str:
    full = int(round(n))
    return "★" * full + "☆" * (5 - full)

def sentiment_badge(label: str) -> str:
    cls = f"badge-{label.lower()}"
    return f'<span class="{cls}">{label}</span>'


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Analysing feedback…")
def load_data(file) -> pd.DataFrame:
    if file is None:
        df = pd.read_csv("data/feedback.csv")
    else:
        df = pd.read_csv(file)

    df["date"] = pd.to_datetime(df["date"])
    df = enrich_dataframe(df, text_col="review")
    return df


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💬 Feedback Dashboard")
    st.caption("Sentiment · Trends · Insights")
    st.divider()

    uploaded = st.file_uploader(
        "Upload your own CSV",
        type=["csv"],
        help="Columns needed: date, customer_name, product, rating, review, category",
    )
    st.divider()

    df_raw = load_data(uploaded)

    # Filters
    st.markdown("### Filters")

    categories = ["All"] + sorted(df_raw["category"].unique().tolist())
    sel_cat = st.selectbox("Category", categories)

    sentiments = ["All", "Positive", "Neutral", "Negative"]
    sel_sent = st.selectbox("Sentiment", sentiments)

    rating_range = st.slider("Rating range", 1, 5, (1, 5))

    date_min = df_raw["date"].min().date()
    date_max = df_raw["date"].max().date()
    date_range = st.date_input("Date range", value=(date_min, date_max),
                               min_value=date_min, max_value=date_max)
    st.divider()
    st.caption("Built with Streamlit · Plotly · TextBlob")


# ── Filter data ────────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_cat != "All":
    df = df[df["category"] == sel_cat]
if sel_sent != "All":
    df = df[df["sentiment_label"] == sel_sent]
df = df[df["rating"].between(*rating_range)]
if len(date_range) == 2:
    df = df[(df["date"].dt.date >= date_range[0]) & (df["date"].dt.date <= date_range[1])]


# ── Title ──────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Customer Feedback Dashboard")
st.markdown(f"Showing **{len(df)}** reviews  ·  Avg rating **{df['rating'].mean():.2f} / 5**  "
            f"·  Avg sentiment **{df['polarity'].mean():+.3f}**")
st.divider()


# ── KPI row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
pos_pct = (df["sentiment_label"] == "Positive").mean() * 100
neg_pct = (df["sentiment_label"] == "Negative").mean() * 100
k1.metric("📝 Total Reviews", len(df))
k2.metric("⭐ Avg Rating", f"{df['rating'].mean():.2f}")
k3.metric("😊 Positive", f"{pos_pct:.0f}%")
k4.metric("😞 Negative", f"{neg_pct:.0f}%")
k5.metric("🎯 Avg Polarity", f"{df['polarity'].mean():+.3f}")

st.divider()


# ── Row 1: Sentiment pie + Rating distribution ─────────────────────────────────
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
    fig_pie.update_traces(textinfo="label+percent", textfont_size=13,
                          marker=dict(line=dict(color="#0f1117", width=2)))
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
    fig_bar.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=300,
                           xaxis_title="Star Rating", yaxis_title="Number of Reviews")
    st.plotly_chart(fig_bar, use_container_width=True)


# ── Row 2: Polarity over time + Category heatmap ──────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-header">Sentiment Polarity Over Time</div>', unsafe_allow_html=True)
    df_time = df.set_index("date").resample("W")["polarity"].mean().reset_index()
    df_time.columns = ["Date", "Avg Polarity"]
    fig_line = px.area(
        df_time, x="Date", y="Avg Polarity",
        color_discrete_sequence=["#818cf8"],
        line_shape="spline",
    )
    fig_line.add_hline(y=0, line_dash="dash", line_color="#f87171", opacity=0.6)
    fig_line.update_layout(**PLOTLY_LAYOUT, height=300,
                            yaxis_title="Avg Polarity", yaxis_range=[-1, 1])
    fig_line.update_traces(fillcolor="rgba(129,140,248,0.15)")
    st.plotly_chart(fig_line, use_container_width=True)

with col4:
    st.markdown('<div class="section-header">Avg Rating by Category</div>', unsafe_allow_html=True)
    cat_stats = df.groupby("category").agg(
        Avg_Rating=("rating", "mean"),
        Count=("rating", "count"),
        Avg_Polarity=("polarity", "mean"),
    ).reset_index().sort_values("Avg_Rating", ascending=True)

    fig_cat = px.bar(
        cat_stats, x="Avg_Rating", y="category", orientation="h",
        color="Avg_Polarity",
        color_continuous_scale=["#f87171", "#facc15", "#4ade80"],
        color_continuous_midpoint=0,
        text=cat_stats["Avg_Rating"].apply(lambda v: f"{v:.2f}"),
        hover_data={"Count": True},
    )
    fig_cat.update_traces(textposition="outside")
    fig_cat.update_layout(**PLOTLY_LAYOUT, height=300,
                           coloraxis_showscale=False,
                           xaxis_title="Avg Rating", yaxis_title="",
                           xaxis_range=[0, 5.5])
    st.plotly_chart(fig_cat, use_container_width=True)


# ── Row 3: Polarity vs Subjectivity scatter + Sentiment by category ────────────
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
    fig_scatter.update_layout(**PLOTLY_LAYOUT, height=320,
                               xaxis_title="Polarity (Neg ← → Pos)",
                               yaxis_title="Subjectivity (Obj ← → Subj)")
    fig_scatter.add_vline(x=0, line_dash="dash", line_color="#475569", opacity=0.5)
    fig_scatter.add_hline(y=0.5, line_dash="dash", line_color="#475569", opacity=0.5)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col6:
    st.markdown('<div class="section-header">Sentiment Breakdown by Category</div>', unsafe_allow_html=True)
    sent_cat = df.groupby(["category", "sentiment_label"]).size().reset_index(name="Count")
    fig_group = px.bar(
        sent_cat, x="category", y="Count", color="sentiment_label",
        color_discrete_map=SENTIMENT_COLORS,
        barmode="group",
    )
    fig_group.update_layout(**PLOTLY_LAYOUT, height=320,
                             xaxis_title="Category", yaxis_title="Count",
                             legend_title="Sentiment")
    st.plotly_chart(fig_group, use_container_width=True)


# ── Row 4: Word cloud ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Top Keywords in Reviews</div>', unsafe_allow_html=True)
keywords = get_keywords(df["review"], top_n=50)

if keywords:
    wc = WordCloud(
        width=1400, height=380,
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
    st.info("Not enough text data to generate word cloud.")

st.divider()


# ── Row 5: Product leaderboard ────────────────────────────────────────────────
st.markdown('<div class="section-header">Product Leaderboard</div>', unsafe_allow_html=True)
prod_stats = df.groupby("product").agg(
    Reviews=("review", "count"),
    Avg_Rating=("rating", "mean"),
    Avg_Polarity=("polarity", "mean"),
    Positive=("sentiment_label", lambda x: (x == "Positive").sum()),
    Negative=("sentiment_label", lambda x: (x == "Negative").sum()),
).reset_index().sort_values("Avg_Rating", ascending=False)

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
    yaxis=dict(title="Avg Rating", range=[0, 5.5], color="#818cf8"),
    yaxis2=dict(title="Avg Polarity", overlaying="y", side="right",
                range=[-1, 1], color="#4ade80"),
    legend=dict(orientation="h", x=0, y=1.12),
    xaxis_tickangle=-35,
)
st.plotly_chart(fig_lb, use_container_width=True)

st.divider()


# ── Row 6: Individual reviews ─────────────────────────────────────────────────
st.markdown('<div class="section-header">Customer Reviews</div>', unsafe_allow_html=True)

sort_by = st.selectbox("Sort by", ["Date (newest)", "Rating (high→low)", "Rating (low→high)",
                                    "Polarity (high→low)", "Polarity (low→high)"])
sort_map = {
    "Date (newest)": ("date", False),
    "Rating (high→low)": ("rating", False),
    "Rating (low→high)": ("rating", True),
    "Polarity (high→low)": ("polarity", False),
    "Polarity (low→high)": ("polarity", True),
}
scol, sasc = sort_map[sort_by]
df_sorted = df.sort_values(scol, ascending=sasc).reset_index(drop=True)

for _, row in df_sorted.head(10).iterrows():
    badge = sentiment_badge(row["sentiment_label"])
    stars = star_rating(row["rating"])
    st.markdown(f"""
    <div class="review-card">
        <div class="review-meta">
            <strong style="color:#e2e8f0">{row['customer_name']}</strong> &nbsp;·&nbsp;
            {row['product']} &nbsp;·&nbsp;
            <span style="color:#facc15">{stars}</span> &nbsp;·&nbsp;
            {row['date'].strftime('%b %d, %Y')} &nbsp;·&nbsp;
            {badge} &nbsp;·&nbsp;
            <span style="color:#8892b0">Polarity: {row['polarity']:+.3f}</span>
        </div>
        <div class="review-text">{row['review']}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ── Export ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Export Analysed Data</div>', unsafe_allow_html=True)
csv_buffer = io.StringIO()
export_cols = ["date", "customer_name", "product", "category", "rating",
               "review", "polarity", "subjectivity", "sentiment_label"]
df[export_cols].to_csv(csv_buffer, index=False)

st.download_button(
    label="⬇️  Download CSV with Sentiment Scores",
    data=csv_buffer.getvalue().encode(),
    file_name="feedback_with_sentiment.csv",
    mime="text/csv",
)
