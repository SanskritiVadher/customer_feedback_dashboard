# 💬 Customer Feedback Dashboard

A beautiful, interactive dashboard for analysing customer feedback using **TextBlob** (NLP sentiment analysis), **Plotly** (interactive charts), and **Streamlit** (web UI).

---

## 📁 Project Structure

```
customer_feedback_dashboard/
│
├── app.py                  ← Main Streamlit application
├── sentiment_utils.py      ← TextBlob sentiment analysis utilities
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
│
└── data/
    └── feedback.csv        ← Sample dataset (30 reviews)
```

---

## ✅ Prerequisites

- Python **3.9 – 3.12** installed
- VS Code installed
- Terminal / Command Prompt access

---

## 🚀 Step-by-Step Setup & Execution

### Step 1 — Open the project in VS Code

```
File → Open Folder → select  customer_feedback_dashboard/
```

### Step 2 — Open the VS Code terminal

```
Terminal → New Terminal   (or  Ctrl + ` )
```

### Step 3 — Create a virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

> You should see `(venv)` at the start of your terminal prompt.

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

> This installs Streamlit, Plotly, TextBlob, NLTK, WordCloud, and Matplotlib.
> First install may take 1–2 minutes.

### Step 5 — Run the dashboard

```bash
streamlit run app.py
```

### Step 6 — View in browser

Streamlit will print:

```
  Local URL:  http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open **http://localhost:8501** in your browser — the dashboard loads automatically.

---

## 🎛️ Features

| Feature | Description |
|---|---|
| **Sentiment Analysis** | TextBlob polarity + subjectivity per review |
| **KPI Cards** | Total reviews, avg rating, % positive/negative, avg polarity |
| **Pie Chart** | Sentiment distribution |
| **Bar Chart** | Rating distribution (1–5 stars) |
| **Area Chart** | Sentiment polarity trend over time |
| **Horizontal Bar** | Avg rating per category, coloured by polarity |
| **Scatter Plot** | Polarity vs Subjectivity bubble chart |
| **Grouped Bar** | Sentiment breakdown by category |
| **Word Cloud** | Most frequent keywords across reviews |
| **Product Leaderboard** | Dual-axis chart: avg rating + polarity |
| **Review Cards** | Individual reviews with badges + scores |
| **Filters** | Category · Sentiment · Rating · Date range |
| **Upload CSV** | Drop in your own data |
| **Export** | Download enriched CSV with sentiment scores |

---

## 📄 CSV Format (for your own data)

Your CSV must have these columns:

```
id, date, customer_name, product, rating, review, category
```

- `date` — any parseable date string (e.g. `2024-03-15`)
- `rating` — integer 1–5
- `review` — free text
- `category` — product category label

---

## 🛑 Stop the app

Press **Ctrl + C** in the terminal.

---

## 💡 Tips

- Edit `data/feedback.csv` to add your own reviews and restart the app.
- The sidebar lets you filter by category, sentiment, rating, and date range.
- Use the **Download CSV** button to export the enriched data with sentiment scores.
