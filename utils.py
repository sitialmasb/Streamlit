import streamlit as st
import pandas as pd
import numpy as np
import os
from openai import OpenAI

def load_custom_css():
    st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #fafbfc !important;
        }
        div.block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            height: 2rem !important;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 1rem !important;
        }
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
            gap: 0.35rem !important;
        }
        html, body, p, span, h1, h2, h3, h4, h5, h6, label, small, strong, div {
            color: #1e293b !important;
        }
        [data-testid="stWidgetLabel"] label, 
        [data-testid="stWidgetLabel"] p,
        .stSelectbox label, 
        .stMultiSelect label,
        .stRadio label {
            color: #334155 !important;
            font-weight: 700 !important;
            font-size: 0.85rem !important;
        }
        div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div,
        div[role="combobox"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            color: #1e293b !important;
        }
        .metric-pill-card {
            border-radius: 20px !important;
            padding: 20px 22px;
            min-height: 135px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03);
            border: 1px solid #e2e8f0;
            transition: transform 0.15s ease-in-out;
        }
        .metric-pill-card:hover {
            transform: translateY(-2px);
        }
        .card-soft-white { background: #ffffff !important; border: 1px solid #e2e8f0 !important; }
        .card-soft-white .pill-title { color: #0284c7 !important; }
        .card-soft-white .pill-value { color: #0f172a !important; }
        .card-soft-white .pill-sub { color: #0369a1 !important; }

        .card-soft-green { background: #f0fdf4 !important; border: 1px solid #bbf7d0 !important; }
        .card-soft-green .pill-title { color: #166534 !important; }
        .card-soft-green .pill-value { color: #14532d !important; }
        .card-soft-green .pill-sub { color: #15803d !important; }

        .card-soft-blue { background: #f0f7ff !important; border: 1px solid #bfdbfe !important; }
        .card-soft-blue .pill-title { color: #1e40af !important; }
        .card-soft-blue .pill-value { color: #1e3a8a !important; }
        .card-soft-blue .pill-sub { color: #2563eb !important; }

        .card-soft-orange { background: #fff7ed !important; border: 1px solid #fed7aa !important; }
        .card-soft-orange .pill-title { color: #9a3412 !important; }
        .card-soft-orange .pill-value { color: #7c2d12 !important; }
        .card-soft-orange .pill-sub { color: #c2410c !important; }

        .card-soft-slate { background: #f8fafc !important; border: 1px solid #e2e8f0 !important; }
        .card-soft-slate .pill-title { color: #475569 !important; }
        .card-soft-slate .pill-value { color: #0f172a !important; }
        .card-soft-slate .pill-sub { color: #64748b !important; }

        .pill-title { font-size: 0.74rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
        .pill-value { font-size: 2.1rem; font-weight: 800; line-height: 1.1; margin: 4px 0; }
        .pill-sub { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }

        .alert-peak-card {
            background: #fff7ed;
            border-left: 5px solid #f97316;
            border-top: 1px solid #ffedd5;
            border-right: 1px solid #ffedd5;
            border-bottom: 1px solid #ffedd5;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(249, 115, 22, 0.04);
        }
        div.capsule-rail-wrapper { margin-top: 28px !important; margin-bottom: 22px !important; }
        [data-testid="stDataFrame"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }
        section[data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            text-align: left;
            justify-content: flex-start;
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            border: 1px solid transparent !important;
            background-color: transparent !important;
            color: #475569 !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #f1f5f9 !important;
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background-color: #eff6ff !important;
            color: #1d4ed8 !important;
            border: 1px solid #dbeafe !important;
            border-left: 5px solid #2563eb !important;
            font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"] p {
            color: #1d4ed8 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def standardize_sentiment_en(val):
    if pd.isna(val):
        return val
    s = str(val).strip().lower()
    if "pos" in s:
        return "Positive"
    elif "neg" in s:
        return "Negative"
    elif "neu" in s or "net" in s:
        return "Neutral"
    return str(val).strip().capitalize()

@st.cache_data
def load_local_dataset():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidate_files = ["data.xlsx", "dataset.xlsx", "data.csv", "dataset.csv"]
    
    file_found = None
    for f in candidate_files:
        full_path = os.path.join(current_dir, f)
        if os.path.exists(full_path):
            file_found = full_path
            break
        elif os.path.exists(f):
            file_found = f
            break
            
    if file_found:
        try:
            if file_found.endswith('.csv'):
                try:
                    df = pd.read_csv(file_found)
                except Exception:
                    df = pd.read_csv(file_found, sep=';')
            else:
                df = pd.read_excel(file_found)
            
            df.columns = [str(c).strip().lower() for c in df.columns]
            if "sentiment" in df.columns:
                df["sentiment"] = df["sentiment"].apply(standardize_sentiment_en)
            if "news_date" in df.columns:
                df["news_date"] = pd.to_datetime(df["news_date"], errors="coerce")
            return df, os.path.basename(file_found)
        except Exception as e:
            st.error(f"Failed to read file {file_found}: {e}")
            
    # Fallback dummy dataset
    np.random.seed(42)
    topics = ["integrity", "loyalty", "quality", "services_facility", "other"]
    domains = ["kompas.com", "detik.com", "tempo.co", "bisnis.com", "cnbcindonesia.com"]
    dates = pd.date_range(end="2026-08-25", periods=60, freq="D")
    
    sample_data = pd.DataFrame({
        "news_url": [f"https://{np.random.choice(domains)}/read/{1000+i}" for i in range(60)],
        "sentiment": np.random.choice(["Positive", "Neutral", "Negative"], size=60, p=[0.45, 0.35, 0.2]),
        "news_date": np.random.choice(dates, size=60),
        "issue_topic": np.random.choice(topics, size=60),
        "domain": np.random.choice(domains, size=60),
        "new_tier": np.random.choice(["Tier 1", "Tier 2", "Tier 3"], size=60, p=[0.5, 0.3, 0.2]),
        "gemini_summary": [
            "AI Summary: Energy supplies and regional supply chain logistics remain stable and secure.",
            "AI Summary: Price evaluations and strategic digital infrastructure mitigation ongoing.",
            "AI Summary: Clean energy transition projects accelerating towards net zero goals.",
            "AI Summary: Regular refinery maintenance scheduled to ensure highest operational safety standards."
        ] * 15
    })
    return sample_data, None

color_map_sentiment = {
    'Positive': '#34d399',
    'Neutral': '#60a5fa',
    'Negative': '#fb923c'
}

def apply_clean_white_layout(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#334155", size=11, family="Arial"),
        xaxis=dict(showgrid=True, gridcolor="#f8fafc", linecolor="#e2e8f0", tickfont=dict(color="#475569", size=10)),
        yaxis=dict(showgrid=True, gridcolor="#f8fafc", linecolor="#e2e8f0", tickfont=dict(color="#475569", size=10)),
        legend=dict(bgcolor="rgba(255, 255, 255, 0.95)", bordercolor="#e2e8f0", borderwidth=1, font=dict(color="#334155"))
    )
    return fig

def analyze_negative_peak(df):
    if df.empty or "sentiment" not in df.columns or "news_date" not in df.columns:
        return None
    df_neg = df[(df["sentiment"] == "Negative") & (df["news_date"].notna())].copy()
    if df_neg.empty:
        return None
    df_neg_daily = df_neg.groupby(df_neg["news_date"].dt.date).size().reset_index(name="count")
    df_neg_daily = df_neg_daily.sort_values(by="news_date")
    peak_row = df_neg_daily.sort_values(by="count", ascending=False).iloc[0]
    peak_date = peak_row["news_date"]
    peak_count = peak_row["count"]
    df_peak_news = df_neg[df_neg["news_date"].dt.date == peak_date]
    top_cause_topic = df_peak_news["issue_topic"].mode()[0] if "issue_topic" in df_peak_news.columns and not df_peak_news["issue_topic"].empty else "-"
    return {
        "peak_date": peak_date.strftime('%d %B %Y'),
        "peak_date_raw": peak_date,
        "peak_count": peak_count,
        "cause_topic": top_cause_topic,
        "peak_articles": df_peak_news,
        "daily_trend": df_neg_daily
    }
from openai import OpenAI

def generate_peak_crisis_summary(df_peak_articles):
    """
    Merangkum artikel negatif pada peak date menggunakan OpenRouter API.
    Format output menggunakan tag HTML agar bersih tanpa nomor dan tanpa simbol bintang.
    """
    if df_peak_articles.empty:
        return "Tidak ada data artikel yang cukup untuk diringkas."
    
    api_key = None
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            api_key = st.secrets["OPENROUTER_API_KEY"]
        elif "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
    if not api_key:
        return "⚠️ **API Key belum dikonfigurasi.** Tambahkan `OPENROUTER_API_KEY` ke Streamlit Secrets atau environment variable."
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        summary_col = "gemini_summary" if "gemini_summary" in df_peak_articles.columns else ("ai_summary" if "ai_summary" in df_peak_articles.columns else "domain")
        combined_texts = " - ".join(df_peak_articles[summary_col].dropna().astype(str).tolist()[:8])
        
        # Instruksi diperketat agar menggunakan tag HTML <b> dan paragraf tanpa nomor
        prompt = (
            "Bertindaklah sebagai analis PR. Berdasarkan ringkasan berita negatif berikut, "
            "buatkan ringkasan super singkat dalam 2 paragraf terpisah tanpa nomor atau bullet point. "
            "Gunakan tag HTML <b>Akar Masalah:</b> di awal paragraf pertama dan <b>Peringatan:</b> di awal paragraf kedua:\n\n" + combined_texts
        )
        
        response = client.chat.completions.create(
            model="microsoft/phi-4",
            messages=[
                {"role": "system", "content": "Anda adalah asisten AI yang membuat ringkasan berita sangat singkat dalam bentuk paragraf bersih menggunakan tag HTML <b>, tanpa nomor, dan tanpa simbol markdown bintang."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal menghasilkan ringkasan AI: {str(e)}"
