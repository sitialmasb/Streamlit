import base64
import os
import streamlit as st
import pandas as pd
import numpy as np
from openai import OpenAI
import plotly.graph_objects as go

# Color Palette Mappings
color_map_sentiment = {
    'Positive': '#16a34a',
    'Neutral': '#237ece',
    'Negative': '#ea580c'
}

def load_custom_css():
    st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #fafbfc !important;
        }
        div.block-container {
            padding-top: 0.8rem !important;
            padding-bottom: 1.5rem !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            height: 1.5rem !important;
        }
        html, body, p, span, h1, h2, h3, h4, h5, h6, label, small, strong, div {
            color: #1e293b !important;
        }
        h2 { font-size: 1.35rem !important; }
        
        /* Label Widget */
        [data-testid="stWidgetLabel"] label, 
        [data-testid="stWidgetLabel"] p,
        .stSelectbox label, 
        .stMultiSelect label {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.78rem !important;
            margin-bottom: 2px !important;
        }

        /* Override Select & Multiselect */
        div[data-baseweb="select"] > div {
            min-height: 36px !important;
            border-radius: 6px !important;
            font-size: 0.82rem !important;
            border-color: #cbd5e1 !important;
        }
        div[data-baseweb="select"]:focus-within > div {
            border-color: #237ece !important;
            box-shadow: 0 0 0 1px #237ece !important;
        }
        div[data-baseweb="tag"] {
            background-color: #f0f7ff !important;
            border: 1px solid #237ece !important;
            border-radius: 4px !important;
        }
        div[data-baseweb="tag"] span {
            color: #237ece !important;
            font-weight: 600 !important;
            font-size: 0.75rem !important;
        }
        div[data-baseweb="tag"] svg {
            fill: #237ece !important;
        }
        li[data-baseweb="menu-item"]:hover {
            background-color: #f0f7ff !important;
            color: #237ece !important;
        }
        li[data-baseweb="menu-item"][aria-selected="true"] {
            background-color: #ebf4fc !important;
            color: #237ece !important;
            font-weight: 700 !important;
        }
        input[type="text"] {
            height: 36px !important;
            font-size: 0.82rem !important;
            border-radius: 6px !important;
        }
        input[type="text"]:focus {
            border-color: #237ece !important;
            box-shadow: 0 0 0 1px #237ece !important;
        }

        /* Metric Cards */
        .metric-pill-card {
            border-radius: 12px !important;
            padding: 12px 14px !important;
            min-height: 90px !important;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
            border: 1px solid #e2e8f0;
            transition: transform 0.15s ease-in-out;
        }
        .metric-pill-card:hover {
            transform: translateY(-1px);
        }
        .card-soft-white { background: #ffffff !important; border: 1px solid #e2e8f0 !important; }
        .card-soft-green { background: #f0fdf4 !important; border: 1px solid #bbf7d0 !important; }
        .card-soft-blue { background: #f0f7ff !important; border: 1px solid #237ece !important; }
        .card-soft-orange { background: #fff7ed !important; border: 1px solid #fed7aa !important; }
        .card-soft-slate { background: #f8fafc !important; border: 1px solid #e2e8f0 !important; }

        .pill-title { font-size: 0.68rem !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; color: #64748b !important; }
        .pill-value { font-size: 1.45rem !important; font-weight: 800; line-height: 1.1; margin: 2px 0; color: #0f172a !important; }
        .pill-sub { font-size: 0.65rem !important; font-weight: 600; text-transform: uppercase; color: #94a3b8 !important; }

        .alert-peak-card {
            background: #fff7ed;
            border-left: 5px solid #ea580c;
            border-top: 1px solid #fed7aa;
            border-right: 1px solid #fed7aa;
            border-bottom: 1px solid #fed7aa;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 16px;
        }
        div.capsule-rail-wrapper { margin-top: 16px !important; margin-bottom: 14px !important; }
        [data-testid="stDataFrame"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 6px;
        }

        button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
            background-color: #237ece !important;
            border-color: #237ece !important;
            color: #ffffff !important;
        }
        button[kind="primary"] p, button[kind="primary"] span,
        div[data-testid="stFormSubmitButton"] button p, div[data-testid="stFormSubmitButton"] button span {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""

def standardize_sentiment_en(val):
    if pd.isna(val):
        return "Neutral"
    s = str(val).strip().lower()
    if any(k in s for k in ["pos", "baik", "positif"]):
        return "Positive"
    elif any(k in s for k in ["neg", "buruk", "negatif"]):
        return "Negative"
    return "Neutral"

def apply_clean_white_layout(fig, height=280):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", size=11, family="sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False)
    return fig

def generate_svg_bars(series, bar_color):
    """Menghasilkan SVG mini bar chart yang embed langsung di dalam kartu HTML."""
    if series is not None and not series.empty:
        vals = series.tail(10).values.tolist()
        if len(vals) < 10:
            vals = [0] * (10 - len(vals)) + vals
    else:
        vals = [2, 4, 3, 5, 2, 4, 6, 3, 5, 8]

    max_v = max(vals) if max(vals) > 0 else 1
    svg_height = 24
    bar_width = 6
    gap = 4
    
    rects = []
    for i, v in enumerate(vals):
        h = max(3, int((v / max_v) * svg_height))
        y = svg_height - h
        x = i * (bar_width + gap)
        rects.append(f'<rect x="{x}" y="{y}" width="{bar_width}" height="{h}" rx="2" fill="{bar_color}" />')
        
    total_w = 10 * (bar_width + gap) - gap
    return f'<svg width="{total_w}" height="{svg_height}" viewBox="0 0 {total_w} {svg_height}" style="display:block;">{"".join(rects)}</svg>'

def check_login():
    """Mempertahankan sesi login saat browser di-refresh via query params."""
    if not st.session_state.get("logged_in", False):
        user_param = st.query_params.get("user")
        role_param = st.query_params.get("role")
        
        if user_param and role_param:
            st.session_state.logged_in = True
            st.session_state.username = user_param
            st.session_state.user_role = role_param

    if not st.session_state.get("logged_in", False):
        st.markdown("""
            <div style="text-align:center; margin-top:40px; margin-bottom:20px;">
                <h2 style="color:#0f172a; font-weight:800; margin-bottom:4px;">TKB NEWS SENTIMENT ANALYSIS</h2>
                <span style="font-size:0.8rem; color:#64748b; font-weight:600;">Silakan login untuk mengakses dashboard</span>
            </div>
        """, unsafe_allow_html=True)
        
        _, col_login, _ = st.columns([1, 1.2, 1])
        with col_login:
            with st.form("login_form"):
                username_input = st.text_input("Username")
                password_input = st.text_input("Password", type="password")
                submit_btn = st.form_submit_button("Masuk ke Dashboard", use_container_width=True)

                if submit_btn:
                    if username_input == "admin" and password_input == "admin123":
                        st.session_state.logged_in = True
                        st.session_state.username = "Admin"
                        st.session_state.user_role = "admin"
                        st.query_params["user"] = "Admin"
                        st.query_params["role"] = "admin"
                        st.rerun()
                    elif username_input == "user" and password_input == "user123":
                        st.session_state.logged_in = True
                        st.session_state.username = "Viewer"
                        st.session_state.user_role = "viewer"
                        st.query_params["user"] = "Viewer"
                        st.query_params["role"] = "viewer"
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")
        st.stop()

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
                
            if "topic" in df.columns:
                df["topic"] = df["topic"].fillna("General").astype(str).str.strip()
            else:
                df["topic"] = "General"
                
            if "subtopic" in df.columns:
                df["subtopic"] = df["subtopic"].fillna("General").astype(str).str.strip()
            else:
                df["subtopic"] = "General"
                
            return df, os.path.basename(file_found)
        except Exception as e:
            st.error(f"Failed to read file {file_found}: {e}")
            
    np.random.seed(42)
    topic_structure = {
        "Governance & Integrity": ["Anti-Corruption Compliance", "Leadership Ethics"],
        "Operational Quality": ["Supply Chain Continuity", "Infrastructure Maintenance"],
        "Customer & Service": ["Digital Platform Reliability", "Billing Inquiries"]
    }
    domains = ["kompas.com", "detik.com", "tempo.co", "bisnis.com"]
    dates = pd.date_range(end="2026-08-25", periods=60, freq="D")
    
    rows = []
    for i in range(80):
        t = np.random.choice(list(topic_structure.keys()))
        st_val = np.random.choice(topic_structure[t])
        rows.append({
            "news_url": f"https://{np.random.choice(domains)}/read/{1000+i}",
            "sentiment": np.random.choice(["Positive", "Neutral", "Negative"], p=[0.45, 0.35, 0.2]),
            "news_date": np.random.choice(dates),
            "topic": t,
            "subtopic": st_val,
            "domain": np.random.choice(domains),
            "new_tier": np.random.choice(["Tier 1", "Tier 2", "Tier 3"], p=[0.5, 0.3, 0.2]),
            "gemini_summary": "AI Summary: Operational protocols audited and supply pipeline remains resilient."
        })
    return pd.DataFrame(rows), None

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
    
    top_cause_topic = df_peak_news["topic"].mode()[0] if "topic" in df_peak_news.columns and not df_peak_news["topic"].empty else "-"
    top_cause_subtopic = df_peak_news["subtopic"].mode()[0] if "subtopic" in df_peak_news.columns and not df_peak_news["subtopic"].empty else "-"
    
    return {
        "peak_date": peak_date.strftime('%d %B %Y'),
        "peak_date_raw": peak_date,
        "peak_count": peak_count,
        "cause_topic": top_cause_topic,
        "cause_subtopic": top_cause_subtopic,
        "peak_articles": df_peak_news,
        "daily_trend": df_neg_daily
    }

def generate_peak_crisis_summary(df_peak_articles):
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
