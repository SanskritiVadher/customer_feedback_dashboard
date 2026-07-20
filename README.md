# 📊 Sales Dashboard

An interactive sales analytics dashboard built with **Streamlit**, **Pandas**, and **Plotly** — designed to visualize sales performance, trends, and key metrics in a clean, easy-to-use interface.

🔗 **Live App:** [https://sanskritivadher-customer-feedback-dashboard-app-0hzopz.streamlit.app/]

---

## 🚀 Features

- 📈 Interactive visualizations (line charts, bar charts, pie charts) powered by Plotly
- 🔍 Filter sales data by date, region, product category, or other dimensions
- 📋 Summary metrics (total sales, growth rate, top products, etc.)
- 🧮 Clean, modular codebase for easy customization
- ☁️ Deployed live via Streamlit Community Cloud

---

## 🗂️ Project Structure

```
sales-dashboard/
│
├── app.py                 # Main Streamlit application
├── utils/                 # Helper functions and data processing modules
│   └── ...
├── data/                  # Sample sales dataset (CSV)
│   └── sales_data.csv
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – web app framework
- **Pandas** – data manipulation
- **Plotly** – interactive charts

---

## 💻 Running Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/SanskritiVadher/sales-dashboard.git
   cd sales-dashboard
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown in your terminal (usually `http://localhost:8501`)

---

## 📊 Sample Data

The dashboard uses a sample sales dataset located in the `data/` folder. You can replace this with your own CSV file, as long as the column structure matches what `app.py` expects.

---

## 🌐 Deployment

This app is deployed using **Streamlit Community Cloud**. Any changes pushed to the `main` branch on GitHub are automatically reflected on the live app within a minute or two.

---

## 🙋‍♀️ Author

**Sanskriti Vadher**
Built as part of a Vibe Coding workshop project.

---

## 📄 License

This project is open-source and available for learning and personal use.
