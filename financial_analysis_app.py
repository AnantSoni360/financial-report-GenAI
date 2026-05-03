import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Advanced Financial Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Advanced Financial Analysis Dashboard")
st.markdown("*Powered by Google Generative AI*")

# API Key configuration
api_key = st.secrets.get("GOOGLE_API_KEY") if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.warning("⚠️ Google API Key not found. Please add it to secrets or environment variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Sidebar - File upload section
st.sidebar.header("📁 Data Source")
data_source = st.sidebar.radio(
    "Choose data source:",
    ["Upload CSV File", "Use Default S&P 500"]
)

df = None

if data_source == "Upload CSV File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload your CSV file",
        type="csv",
        help="Upload a CSV file with financial data. Required columns: Name, Sector, Price, Price/Earnings, etc."
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success(f"✅ File uploaded! ({len(df)} rows)")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {str(e)}")
            df = None
else:
    # Load default S&P 500 data
    @st.cache_data
    def load_data():
        df = pd.read_csv("https://raw.githubusercontent.com/datasets/s-and-p-500-companies-financials/refs/heads/main/data/constituents-financials.csv")
        return df

    with st.spinner("Loading default S&P 500 data..."):
        df = load_data()

# Check if data is loaded
if df is None:
    st.warning("⚠️ Please upload a CSV file or select default data to continue.")
    st.stop()

# Data preprocessing
df = df.dropna()
df = df.drop(columns=["Symbol", "SEC Filings"], errors='ignore')

# Identify numeric columns
numeric_cols = [
    "Price", "Price/Earnings", "Dividend Yield",
    "Earnings/Share", "52 Week Low", "52 Week High",
    "Market Cap", "EBITDA", "Price/Sales", "Price/Book"
]

# Only process columns that exist in the data
available_numeric_cols = [col for col in numeric_cols if col in df.columns]

for col in available_numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna()

# Check if we have required columns for analysis
required_cols = ['Name', 'Sector']
if not all(col in df.columns for col in required_cols):
    st.error("❌ Error: CSV must contain 'Name' and 'Sector' columns")
    st.stop()

# Feature engineering
if "Price/Earnings" in df.columns:
    df["Valuation"] = df["Price/Earnings"].apply(
        lambda x: "Undervalued" if x < 15 else "Overvalued" if x > 25 else "Fair"
    )
else:
    df["Valuation"] = "N/A"

if "Price" in df.columns and "52 Week Low" in df.columns and "52 Week High" in df.columns:
    df["Market_Position"] = (
        (df["Price"] - df["52 Week Low"]) /
        (df["52 Week High"] - df["52 Week Low"])
    ) * 100
else:
    df["Market_Position"] = 0

if "Earnings/Share" in df.columns:
    df["Profit_Status"] = df["Earnings/Share"].apply(
        lambda x: "Profitable" if x > 0 else "Loss"
    )
else:
    df["Profit_Status"] = "N/A"

if "Market Cap" in df.columns:
    def size_category(x):
        if x > 1e11:
            return "Large Cap"
        elif x > 1e10:
            return "Mid Cap"
        else:
            return "Small Cap"
    df["Company_Size"] = df["Market Cap"].apply(size_category)
else:
    df["Company_Size"] = "N/A"

# Risk Score calculation
if "Price/Earnings" in df.columns and "Dividend Yield" in df.columns:
    df["Risk_Score"] = (df["Price/Earnings"] / 50 * 100 - df["Dividend Yield"] * 100).clip(0, 100)
else:
    df["Risk_Score"] = 50

# Analysis
sector_analysis = df.groupby("Sector").agg({
    col: "mean" for col in ["Market Cap", "Price/Earnings", "Earnings/Share"] 
    if col in df.columns
}).reset_index()

if "Market Cap" in sector_analysis.columns:
    sector_analysis["Company_Count"] = df.groupby("Sector").size().values

top_companies = df.sort_values(
    by="Market Cap" if "Market Cap" in df.columns else "Name",
    ascending=False
).head(5)

# Build summary
summary = {
    "Total Companies": len(df),
}

if "Price/Earnings" in df.columns:
    summary["Avg P/E Ratio"] = round(df["Price/Earnings"].mean(), 2)

if "Earnings/Share" in df.columns:
    summary["Avg EPS"] = round(df["Earnings/Share"].mean(), 2)
    summary["Profitable %"] = round((df["Earnings/Share"] > 0).mean() * 100, 2)

if "Dividend Yield" in df.columns:
    summary["Avg Div Yield"] = f"{round(df['Dividend Yield'].mean(), 2)}%"

# Key insights
insights = []
if "Price/Earnings" in df.columns and summary.get("Avg P/E Ratio", 0) > 25:
    insights.append("🔴 Market appears overvalued - High average P/E ratio")
if summary.get("Profitable %", 0) > 70:
    insights.append("🟢 Strong profitability - Majority of companies are profitable")
if summary.get("Profitable %", 0) < 50:
    insights.append("🟡 Profitability concern - Less than half companies are profitable")

if not sector_analysis.empty:
    top_sector = sector_analysis.sort_values(
        by="Market Cap" if "Market Cap" in sector_analysis.columns else sector_analysis.columns[1],
        ascending=False
    ).iloc[0]["Sector"]
    insights.append(f"📍 {top_sector} sector dominates the portfolio")

if not insights:
    insights.append("✓ Analysis completed. Review detailed insights below.")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", 
    "📈 Visualizations", 
    "🔍 Detailed Analysis",
    "⚖️ Comparison",
    "🤖 AI Insights",
    "📥 Export"
])

# TAB 1: OVERVIEW
with tab1:
    st.subheader("Summary Metrics")
    cols = st.columns(len(summary))
    for i, (key, value) in enumerate(summary.items()):
        with cols[i]:
            st.metric(key, value)
    
    st.subheader("📈 Key Insights")
    for insight in insights:
        st.info(insight)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        if "Market Cap" in df.columns:
            st.metric("Total Market Cap", f"${df['Market Cap'].sum()/1e12:.2f}T")
    with col2:
        if "Price/Book" in df.columns:
            st.metric("Avg Price/Book", f"{df['Price/Book'].mean():.2f}")
    with col3:
        profitable_count = (df["Earnings/Share"] > 0).sum() if "Earnings/Share" in df.columns else 0
        st.metric("Profitable Companies", profitable_count)

# TAB 2: VISUALIZATIONS
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Sector Distribution")
        if not sector_analysis.empty and "Market Cap" in sector_analysis.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            sector_data = sector_analysis.sort_values("Market Cap", ascending=True)
            ax.barh(sector_data["Sector"], sector_data["Market Cap"]/1e12, color='#667eea')
            ax.set_xlabel("Average Market Cap (Trillion $)")
            ax.set_title("Market Cap by Sector")
            st.pyplot(fig)
    
    with col2:
        st.subheader("💰 Company Size Distribution")
        if "Company_Size" in df.columns:
            size_counts = df["Company_Size"].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#667eea', '#764ba2', '#f093fb']
            ax.pie(size_counts.values, labels=size_counts.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax.set_title("Distribution by Company Size")
            st.pyplot(fig)
    
    # P/E Ratio distribution
    if "Price/Earnings" in df.columns:
        st.subheader("📈 P/E Ratio Distribution")
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.hist(df["Price/Earnings"].dropna(), bins=30, color='#667eea', edgecolor='black')
        ax.axvline(df["Price/Earnings"].mean(), color='red', linestyle='--', label=f'Mean: {df["Price/Earnings"].mean():.2f}')
        ax.set_xlabel("P/E Ratio")
        ax.set_ylabel("Frequency")
        ax.set_title("Distribution of P/E Ratios")
        ax.legend()
        st.pyplot(fig)
    
    # Profitability status
    if "Profit_Status" in df.columns:
        st.subheader("💹 Profitability Status")
        status_counts = df["Profit_Status"].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#28a745', '#dc3545']
        ax.bar(status_counts.index, status_counts.values, color=colors)
        ax.set_ylabel("Number of Companies")
        ax.set_title("Profitable vs Loss-Making Companies")
        st.pyplot(fig)

# TAB 3: DETAILED ANALYSIS
with tab3:
    st.subheader("🏢 Sector Analysis")
    st.dataframe(
        sector_analysis.sort_values("Market Cap", ascending=False) if "Market Cap" in sector_analysis.columns else sector_analysis,
        use_container_width=True
    )
    
    st.subheader("⭐ Top 5 Companies")
    display_cols = ["Name"]
    if "Market Cap" in top_companies.columns:
        display_cols.append("Market Cap")
    if "Price/Earnings" in top_companies.columns:
        display_cols.append("Price/Earnings")
    if "Earnings/Share" in top_companies.columns:
        display_cols.append("Earnings/Share")
    if "Company_Size" in top_companies.columns:
        display_cols.append("Company_Size")
    
    st.dataframe(top_companies[display_cols], use_container_width=True)
    
    # Valuation Analysis
    if "Valuation" in df.columns:
        st.subheader("💎 Valuation Analysis")
        val_counts = df["Valuation"].value_counts()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Undervalued", val_counts.get("Undervalued", 0))
        with col2:
            st.metric("Fair Value", val_counts.get("Fair", 0))
        with col3:
            st.metric("Overvalued", val_counts.get("Overvalued", 0))

# TAB 4: COMPARISON TOOL
with tab4:
    st.subheader("⚖️ Company Comparison")
    
    # Select companies to compare
    companies = df["Name"].tolist()
    selected_companies = st.multiselect(
        "Select companies to compare:",
        companies,
        default=companies[:3] if len(companies) >= 3 else companies
    )
    
    if selected_companies:
        comparison_df = df[df["Name"].isin(selected_companies)][["Name"] + available_numeric_cols]
        st.dataframe(comparison_df.set_index("Name"), use_container_width=True)
        
        # Comparison visualization
        if "Price/Earnings" in df.columns and len(selected_companies) > 0:
            fig, ax = plt.subplots(figsize=(12, 5))
            comp_data = df[df["Name"].isin(selected_companies)]
            ax.bar(comp_data["Name"], comp_data["Price/Earnings"], color='#667eea')
            ax.set_ylabel("P/E Ratio")
            ax.set_title("P/E Ratio Comparison")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

# TAB 5: AI INSIGHTS
with tab5:
    st.subheader("🤖 AI-Generated Financial Report")
    
    # Sector filter for report
    sectors = df["Sector"].unique().tolist()
    selected_sector = st.selectbox("Generate report for sector (optional):", ["All Sectors"] + sectors)
    
    filtered_df = df if selected_sector == "All Sectors" else df[df["Sector"] == selected_sector]
    
    prompt = f"""
You are a professional financial analyst. Analyze the following financial data and provide comprehensive insights.

Data Source: {"Uploaded CSV File" if data_source == "Upload CSV File" else "S&P 500 Dataset"}
Sector: {selected_sector if selected_sector != "All Sectors" else "Multiple Sectors"}
Number of Companies: {len(filtered_df)}

Summary Statistics:
{filtered_df[available_numeric_cols].describe().to_string()}

Valuation Metrics:
- Average P/E Ratio: {filtered_df["Price/Earnings"].mean() if "Price/Earnings" in filtered_df.columns else "N/A"}
- Average EPS: {filtered_df["Earnings/Share"].mean() if "Earnings/Share" in filtered_df.columns else "N/A"}
- Profitable Companies: {(filtered_df["Earnings/Share"] > 0).sum() if "Earnings/Share" in filtered_df.columns else "N/A"}

Top 5 Companies:
{filtered_df.nlargest(5, "Market Cap" if "Market Cap" in filtered_df.columns else "Name")[['Name', 'Sector'] + [col for col in available_numeric_cols if col in filtered_df.columns]][:3].to_string() if len(filtered_df) > 0 else "No data"}

Key Insights Generated:
{insights}

Please provide:
1. Market Overview & Trends
2. Sector-specific Analysis
3. Investment Opportunities
4. Risk Assessment
5. Actionable Recommendations
6. Future Outlook
"""

    if st.button("🔮 Generate AI Report", type="primary", use_container_width=True):
        with st.spinner("🤖 Generating AI insights..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")

# TAB 6: EXPORT
with tab6:
    st.subheader("📥 Export & Download")
    
    # Export data options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Full Dataset", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Click to download CSV",
                data=csv,
                file_name="financial_analysis_data.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Sector Analysis", use_container_width=True):
            csv = sector_analysis.to_csv(index=False)
            st.download_button(
                label="Click to download CSV",
                data=csv,
                file_name="sector_analysis.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("⭐ Download Top Companies", use_container_width=True):
            csv = top_companies.to_csv(index=False)
            st.download_button(
                label="Click to download CSV",
                data=csv,
                file_name="top_companies.csv",
                mime="text/csv"
            )
    
    st.divider()
    
    # Statistics summary
    st.subheader("📊 Dataset Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Numeric Column Statistics:**")
        st.dataframe(df[available_numeric_cols].describe(), use_container_width=True)
    
    with col2:
        st.write("**Categorical Columns:**")
        cat_stats = pd.DataFrame({
            "Column": ["Sector", "Valuation", "Profit_Status", "Company_Size"],
            "Unique Values": [
                df["Sector"].nunique() if "Sector" in df.columns else 0,
                df["Valuation"].nunique() if "Valuation" in df.columns else 0,
                df["Profit_Status"].nunique() if "Profit_Status" in df.columns else 0,
                df["Company_Size"].nunique() if "Company_Size" in df.columns else 0
            ]
        })
        st.dataframe(cat_stats, use_container_width=True)

# Footer
st.divider()
st.markdown("""
---
**Dashboard Version:** 2.0 | **Last Updated:** May 2026
*Built with Streamlit & Google Generative AI*
""")
