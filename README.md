# 📊 Advanced Financial Analysis Dashboard

A powerful, AI-powered Streamlit application for comprehensive financial data analysis with interactive visualizations, sector analysis, company comparisons, and AI-generated insights powered by Google Generative AI.

---

## 🌟 Features

### **Core Capabilities**
- 📁 **CSV Upload** - Upload your own financial datasets or use S&P 500 data
- 📊 **Interactive Dashboard** - 6 specialized tabs with different analysis views
- 📈 **Advanced Visualizations** - Charts, histograms, pie charts, and more
- 🤖 **AI-Powered Reports** - Generate detailed financial analysis using Google Generative AI
- ⚖️ **Company Comparisons** - Compare multiple companies side-by-side
- 📥 **Data Export** - Download analysis results in CSV format

### **Dashboard Tabs**

1. **📊 Overview Tab**
   - Summary metrics (Companies, P/E Ratio, EPS, Profitability %)
   - Key insights with color-coded indicators
   - Quick stats (Total Market Cap, Price/Book, Profitable Count)

2. **📈 Visualizations Tab**
   - Sector distribution by market cap (bar chart)
   - Company size distribution (pie chart)
   - P/E ratio distribution (histogram)
   - Profitability status comparison (bar chart)

3. **🔍 Detailed Analysis Tab**
   - Sector analysis with aggregated metrics
   - Top 5 companies by market cap
   - Valuation analysis (Undervalued/Fair/Overvalued)

4. **⚖️ Comparison Tab**
   - Multi-select company comparison
   - Side-by-side metric display
   - Visual P/E ratio comparison

5. **🤖 AI Insights Tab**
   - Sector-specific AI report generation
   - Professional financial analysis
   - Investment recommendations
   - Risk assessment

6. **📥 Export Tab**
   - Download full dataset
   - Export sector analysis
   - Download top companies list
   - View dataset statistics

---

## 📋 Data Requirements

### **Required Columns**
- `Name` - Company name
- `Sector` - Industry category

### **Recommended Columns** (for full analysis)
- `Price`, `Price/Earnings`, `Dividend Yield`, `Earnings/Share`
- `52 Week Low`, `52 Week High`, `Market Cap`, `EBITDA`
- `Price/Sales`, `Price/Book`

### **Advanced Columns** (optional)
- `Revenue Growth %`, `Debt to Equity`, `Free Cash Flow`, `Analyst Rating`

---

## 🚀 Quick Start

### **1. Installation**

```bash
cd "New folder"
pip install -r requirements.txt
```

### **2. Configure API Key**

1. Get your free Google API key: https://makersuite.google.com/app/apikey
2. Edit `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "your-api-key-here"
   ```

### **3. Run the Application**

```bash
streamlit run financial_analysis_app.py
```

Access at: http://localhost:8501

---

## 📁 Project Files

```
New folder/
├── financial_analysis_app.py              # Main application
├── sample_financial_data.csv              # Basic dataset (37 companies)
├── sample_financial_data_advanced.csv     # Advanced dataset (45 companies)
├── requirements.txt                       # Dependencies
├── .streamlit/secrets.toml               # API configuration
└── README.md                              # Documentation
```

---

## 📊 Sample Datasets

- **sample_financial_data.csv**: 37 companies, basic metrics (perfect for learning)
- **sample_financial_data_advanced.csv**: 45 companies with Revenue Growth, Debt/Equity, Free Cash Flow, Analyst Ratings

---

## 🔧 Technical Stack

- **Python 3.12+** | **Streamlit 1.49+** | **Pandas 2.0+**
- **Google Generative AI** | **Matplotlib & Seaborn**

---

## 💡 Usage Examples

1. **Use Default S&P 500** → Explore built-in data
2. **Upload CSV** → Analyze custom financial data
3. **Generate Reports** → Get AI-powered insights
4. **Compare Companies** → Side-by-side analysis
5. **Export Results** → Download CSVs

---

## 🎯 Key Metrics

| Metric | Meaning |
|--------|---------|
| **P/E Ratio** | Price to Earnings (Lower = Undervalued) |
| **EPS** | Earnings Per Share (Higher = More Profitable) |
| **Market Cap** | Total Company Value |
| **Debt/Equity** | Financial Leverage (Lower = Less Risky) |
| **Free Cash Flow** | Available Cash for Operations |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r requirements.txt` |
| API Key error | Check `.streamlit/secrets.toml` |
| File upload error | Ensure CSV has "Name" and "Sector" columns |
| Slow loading | Use datasets <5000 rows |

---

## 🎓 For Viva Presentation

**Demonstrate:**
✅ Upload and analyze sample data
✅ Navigate different dashboard tabs
✅ Generate AI reports
✅ Compare companies
✅ Export results

**Key Points:**
- Data preprocessing & cleaning
- Feature engineering
- AI integration
- Tab-based UI organization
- Dynamic file handling

---

## 📝 License

Educational and commercial use permitted. Modify as needed.

---

**Version:** 2.0 | **Updated:** May 2026

*Built with ❤️ using Streamlit & Google Generative AI*
