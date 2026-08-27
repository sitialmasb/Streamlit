import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA SOFT / PASTEL
# ==========================================
st.set_page_config(
    page_title="TKB NEWS SENTIMENT ANALYSIS",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "OVERVIEW"

# Custom CSS: Soft Theme & Muted Filter Tags
st.markdown("""
<style>
    /* 1. Base App & Sidebar Background */
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

    /* 2. Global Text: Deep Slate */
    html, body, p, span, h1, h2, h3, h4, h5, h6, label, small, strong, div {
        color: #1e293b !important;
    }

    /* 3. Label Filter & Widget */
    [data-testid="stWidgetLabel"] label, 
    [data-testid="stWidgetLabel"] p,
    .stSelectbox label, 
    .stMultiSelect label {
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
    }

    /* 4. Selectbox & Multiselect Input Box */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div,
    div[role="combobox"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        color: #1e293b !important;
    }

    /* 5. Tag/Chip Multiselect: Soft Muted Palette */
    div[data-baseweb="select"] span[data-baseweb="tag"],
    span[data-baseweb="tag"],
    div[data-baseweb="tag"] {
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] span[data-baseweb="tag"] span,
    span[data-baseweb="tag"] span,
    div[data-baseweb="tag"] span {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] span[data-baseweb="tag"] svg,
    span[data-baseweb="tag"] svg,
    div[data-baseweb="tag"] svg {
        fill: #64748b !important;
        color: #64748b !important;
    }

    /* 6. Soft / Pastel Metric Pill Cards */
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
    
    .card-soft-white {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }
    .card-soft-white .pill-title { color: #0284c7 !important; }
    .card-soft-white .pill-value { color: #0f172a !important; }
    .card-soft-white .pill-sub { color: #0369a1 !important; }

    .card-soft-green {
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
    }
    .card-soft-green .pill-title { color: #166534 !important; }
    .card-soft-green .pill-value { color: #14532d !important; }
    .card-soft-green .pill-sub { color: #15803d !important; }

    .card-soft-blue {
        background: #f0f7ff !important;
        border: 1px solid #bfdbfe !important;
    }
    .card-soft-blue .pill-title { color: #1e40af !important; }
    .card-soft-blue .pill-value { color: #1e3a8a !important; }
    .card-soft-blue .pill-sub { color: #2563eb !important; }

    .card-soft-orange {
        background: #fff7ed !important;
        border: 1px solid #fed7aa !important;
    }
    .card-soft-orange .pill-title { color: #9a3412 !important; }
    .card-soft-orange .pill-value { color: #7c2d12 !important; }
    .card-soft-orange .pill-sub { color: #c2410c !important; }

    .card-soft-slate {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
    }
    .card-soft-slate .pill-title { color: #475569 !important; }
    .card-soft-slate .pill-value { color: #0f172a !important; }
    .card-soft-slate .pill-sub { color: #64748b !important; }

    .pill-title {
        font-size: 0.74rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .pill-value {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 4px 0;
    }
    .pill-sub {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* 7. Soft Alert Card */
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

    /* 8. Tabs Styling */
    button[data-baseweb="tab"] {
        color: #64748b !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0284c7 !important;
        border-bottom: 3px solid #0284c7 !important;
    }

    /* 9. Dataframe Container */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    /* 10. Sidebar Buttons */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 4px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid #e2e8f0 !important;
        background-color: #f8fafc !important;
        color: #334155 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: #f0f9ff !important;
        color: #0369a1 !important;
        border-color: #bae6fd !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. STANDARISASI & LOAD DATASET
# ==========================================
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
    candidate_files = [
        "data.xlsx", "dataset.xlsx", "data.csv", "dataset.csv"
    ]
    
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
            st.error(f"Gagal membaca file {file_found}: {e}")
            
    # Fallback dummy
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
            "Ringkasan AI: Pertamina memastikan ketersediaan pasokan energi aman dan stabil di seluruh regional.",
            "Ringkasan AI: Evaluasi harga BBM serta penguatan infrastruktur digital guna efisiensi distribusi.",
            "Ringkasan AI: Proyek transisi energi bersih dan dekarbonisasi terus dipercepat untuk mencapai target net zero emission.",
            "Ringkasan AI: Pemeliharaan berkala sarana dan fasilitas kilang dalam rangka peningkatan standar keselamatan kerja."
        ] * 15
    })
    return sample_data, None

df_raw, loaded_file_name = load_local_dataset()

# Soft Chart Colors
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


# ==========================================
# 3. SIDEBAR: NAVIGATION MENU
# ==========================================
with st.sidebar:
    st.markdown("<p style='font-size: 0.85rem; font-weight: 800; margin-bottom: 6px; color:#334155;'>MENU DASHBOARD</p>", unsafe_allow_html=True)
    
    if st.button("📊 SENTIMENT OVERVIEW", key="nav_overview", type="primary" if st.session_state.active_page == "OVERVIEW" else "secondary", use_container_width=True):
        st.session_state.active_page = "OVERVIEW"
        st.rerun()

    if st.button("🚨 ALERT & PEAK SPIKE", key="nav_peak", type="primary" if st.session_state.active_page == "PEAK_ALERT" else "secondary", use_container_width=True):
        st.session_state.active_page = "PEAK_ALERT"
        st.rerun()

    if st.button("🔍 TOPIC DEEP DIVE", key="nav_deep", type="primary" if st.session_state.active_page == "DEEP_DIVE" else "secondary", use_container_width=True):
        st.session_state.active_page = "DEEP_DIVE"
        st.rerun()

    st.write("")
    if loaded_file_name:
        st.success(f" Terhubung: `{loaded_file_name}`")
    else:
        st.info("💡 Memakai data sampel bawaan.")


# ==========================================
# 4. HALAMAN 1: SENTIMENT OVERVIEW
# ==========================================
if st.session_state.active_page == "OVERVIEW":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">📊</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #0f172a; font-weight:800;">TKB NEWS <span style="color:#0284c7; font-style: italic;">OVERVIEW</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.1em; color: #64748b; font-weight: 700;">GENERAL SENTIMENT & MEDIA PERFORMANCE MONITORING</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # In-page Filters
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sent_list = sorted(list(df_raw["sentiment"].dropna().unique())) if "sentiment" in df_raw.columns else []
        selected_sent = st.multiselect("Sentiment", options=sent_list, default=sent_list, key="ov_sent")
    with f2:
        tier_list = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
        selected_tier = st.multiselect("Tier Media", options=tier_list, default=tier_list, key="ov_tier")
    with f3:
        topic_list = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
        selected_topic = st.multiselect("Issue Topic", options=topic_list, default=topic_list, key="ov_topic")
    with f4:
        domain_list = sorted(list(df_raw["domain"].dropna().astype(str).unique())) if "domain" in df_raw.columns else []
        selected_domain = st.multiselect("Media Domain", options=domain_list, default=[], key="ov_domain")

    # Filter data
    df_filtered = df_raw.copy()
    if selected_sent and "sentiment" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["sentiment"].isin(selected_sent)]
    if selected_tier and "new_tier" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["new_tier"].astype(str).isin(selected_tier)]
    if selected_domain and "domain" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["domain"].astype(str).isin(selected_domain)]
    if selected_topic and "issue_topic" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["issue_topic"].astype(str).isin(selected_topic)]

    total_news = len(df_filtered)
    pos_count = len(df_filtered[df_filtered["sentiment"] == "Positive"]) if "sentiment" in df_filtered.columns else 0
    neu_count = len(df_filtered[df_filtered["sentiment"] == "Neutral"]) if "sentiment" in df_filtered.columns else 0
    neg_count = len(df_filtered[df_filtered["sentiment"] == "Negative"]) if "sentiment" in df_filtered.columns else 0
    top_topic = df_filtered["issue_topic"].mode()[0] if not df_filtered.empty and "issue_topic" in df_filtered.columns else "-"

    # Soft Metric Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-white">
                <div class="pill-title">TOTAL NEWS</div>
                <div class="pill-value">{total_news}</div>
                <div class="pill-sub">↑ Performance</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-green">
                <div class="pill-title">POSITIVE</div>
                <div class="pill-value">{pos_count}</div>
                <div class="pill-sub">{(pos_count/total_news*100) if total_news else 0:.1f}% DARI TOTAL</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-blue">
                <div class="pill-title">NEUTRAL</div>
                <div class="pill-value">{neu_count}</div>
                <div class="pill-sub">{(neu_count/total_news*100) if total_news else 0:.1f}% DARI TOTAL</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-orange">
                <div class="pill-title">NEGATIVE</div>
                <div class="pill-value">{neg_count}</div>
                <div class="pill-sub">{(neg_count/total_news*100) if total_news else 0:.1f}% PERLU TINDAKAN</div>
            </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-slate">
                <div class="pill-title">TOP TOPIC</div>
                <div class="pill-value" style="font-size:1.35rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{top_topic}">{top_topic}</div>
                <div class="pill-sub">VOLUME TERBESAR</div>
            </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Distribusi Sentiment & Media", "📌 Sebaran Issue Topic", "📰 Gemini AI News Feed"])
    with tab1:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Porsi Sentiment</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "sentiment" in df_filtered.columns:
                fig_pie = px.pie(df_filtered, names='sentiment', hole=0.55, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_pie.update_traces(textinfo='percent+value')
                fig_pie = apply_clean_white_layout(fig_pie, height=330)
                st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Sentiment Berdasarkan Tier Media</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "new_tier" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_tier_sent = df_filtered.groupby(['new_tier', 'sentiment']).size().reset_index(name='count')
                fig_tier = px.bar(df_tier_sent, x='new_tier', y='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='group', text='count')
                fig_tier = apply_clean_white_layout(fig_tier, height=330)
                fig_tier.update_layout(xaxis_title="Tier Media", yaxis_title="Jumlah Berita")
                st.plotly_chart(fig_tier, use_container_width=True)

    with tab2:
        c_top1, c_top2 = st.columns([1.2, 1])
        with c_top1:
            st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Komposisi Sentiment per Issue Topic</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "issue_topic" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_top_sent = df_filtered.groupby(['issue_topic', 'sentiment']).size().reset_index(name='count')
                fig_top = px.bar(df_top_sent, y='issue_topic', x='count', color='sentiment', color_discrete_map=color_map_sentiment, orientation='h', barmode='stack')
                fig_top = apply_clean_white_layout(fig_top, height=340)
                fig_top.update_layout(yaxis_title="", xaxis_title="Jumlah Berita")
                st.plotly_chart(fig_top, use_container_width=True)
        with c_top2:
            st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Top Domain Media (Volume)</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "domain" in df_filtered.columns:
                top_domains = df_filtered['domain'].value_counts().head(8).reset_index()
                top_domains.columns = ['Domain', 'Count']
                fig_domains = px.bar(top_domains, x='Count', y='Domain', orientation='h', color_discrete_sequence=['#60a5fa'], text='Count')
                fig_domains = apply_clean_white_layout(fig_domains, height=340)
                fig_domains.update_layout(yaxis=dict(autorange="reversed"), yaxis_title="", xaxis_title="Total Berita")
                st.plotly_chart(fig_domains, use_container_width=True)

    with tab3:
        st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Detail Feed Berita & Ringkasan Gemini AI</p>", unsafe_allow_html=True)
        cols = [c for c in ["news_date", "domain", "new_tier", "issue_topic", "sentiment", "gemini_summary", "news_url"] if c in df_filtered.columns]
        col_config = {
            "gemini_summary": st.column_config.TextColumn("Ringkasan Berita (Gemini Summary)", width="large"),
            "news_url": st.column_config.LinkColumn("Tautan Berita", display_text="Buka Link 🔗"),
            "domain": st.column_config.TextColumn("Media Domain"),
            "news_date": st.column_config.DateColumn("Tanggal", format="YYYY-MM-DD"),
            "sentiment": st.column_config.TextColumn("Sentiment"),
            "issue_topic": st.column_config.TextColumn("Issue Topic"),
            "new_tier": st.column_config.TextColumn("Tier")
        }
        st.dataframe(df_filtered[cols], column_config=col_config, hide_index=True, use_container_width=True, height=450)


# ==========================================
# 5. HALAMAN 2: ALERT & PEAK SPIKE
# ==========================================
elif st.session_state.active_page == "PEAK_ALERT":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #fff7ed; border: 1px solid #fed7aa; padding: 10px; border-radius: 12px; font-size: 1.3rem;">🚨</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #0f172a; font-weight:800;">CRISIS ALERT & <span style="color:#ea580c; font-style: italic;">PEAK ANALYSIS</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.1em; color: #64748b; font-weight: 700;">NEGATIVE SENTIMENT SPIKES & ROOT CAUSE INVESTIGATION</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    peak_data = analyze_negative_peak(df_raw)

    if peak_data:
        st.markdown(f"""
            <div class="alert-peak-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                    <span style="font-weight:800; font-size:1.05rem; color:#9a3412;">🚨 HIGHEST NEGATIVE SPIKE OCCURRENCE</span>
                    <span style="background:#ffedd5; color:#9a3412; border: 1px solid #fed7aa; padding:4px 12px; border-radius:16px; font-size:0.8rem; font-weight:800;">
                        {peak_data['peak_count']} Artikel Negatif
                    </span>
                </div>
                <div style="font-size:0.92rem; color:#334155; line-height: 1.6;">
                    Lonjakan sentimen negatif tertinggi terdeteksi pada tanggal <b>{peak_data['peak_date']}</b>. 
                    Isu pemicu utama didominasi oleh topik <b><mark style="background:#fef3c7; color:#92400e; padding:2px 6px; border-radius:4px; font-weight:700;">{peak_data['cause_topic']}</mark></b>.
                </div>
            </div>
        """, unsafe_allow_html=True)

        pk1, pk2, pk3 = st.columns(3)
        with pk1:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-white">
                    <div class="pill-title">TANGGAL PUNCAK (PEAK DATE)</div>
                    <div class="pill-value" style="font-size:1.5rem; color:#0f172a;">{peak_data['peak_date']}</div>
                    <div class="pill-sub">Titik Krisis Tertinggi</div>
                </div>
            """, unsafe_allow_html=True)
        with pk2:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-orange">
                    <div class="pill-title">TOTAL BERITA NEGATIF</div>
                    <div class="pill-value">{peak_data['peak_count']}</div>
                    <div class="pill-sub">Volume Lonjakan Harian</div>
                </div>
            """, unsafe_allow_html=True)
        with pk3:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-slate">
                    <div class="pill-title">ROOT CAUSE (TOPIC)</div>
                    <div class="pill-value" style="font-size:1.5rem; color:#0f172a;">{peak_data['cause_topic']}</div>
                    <div class="pill-sub">Faktor Penyebab Utama</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<p style='font-weight:700; font-size:1rem; margin-top:14px; margin-bottom:6px; color:#1e293b;'>Timeline Tren Sentimen Negatif & Anomali Spike</p>", unsafe_allow_html=True)
        df_trend = peak_data["daily_trend"]
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=df_trend["news_date"],
            y=df_trend["count"],
            mode='lines+markers',
            name='Negative Sentiment',
            line=dict(color='#fb923c', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(251, 146, 60, 0.12)'
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=[peak_data["peak_date_raw"]],
            y=[peak_data["peak_count"]],
            mode='markers+text',
            name='Peak Point',
            text=[f"Peak: {peak_data['peak_count']}"],
            textposition="top center",
            marker=dict(color='#ea580c', size=12, symbol='circle')
        ))
        
        fig_trend = apply_clean_white_layout(fig_trend, height=360)
        fig_trend.update_layout(xaxis_title="Tanggal Berita", yaxis_title="Jumlah Berita Negatif")
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-top:14px; margin-bottom:6px; color:#1e293b;'>Daftar Berita Pemicu pada Tanggal Puncak ({peak_data['peak_date']})</p>", unsafe_allow_html=True)
        cols_peak = [c for c in ["domain", "new_tier", "issue_topic", "gemini_summary", "news_url"] if c in peak_data["peak_articles"].columns]
        col_cfg_peak = {
            "gemini_summary": st.column_config.TextColumn("Ringkasan Isu Berita (Gemini Summary)", width="large"),
            "news_url": st.column_config.LinkColumn("Tautan Berita", display_text="Buka Link 🔗"),
            "domain": st.column_config.TextColumn("Portal Media"),
            "issue_topic": st.column_config.TextColumn("Topik Isu"),
            "new_tier": st.column_config.TextColumn("Tier")
        }
        st.dataframe(peak_data["peak_articles"][cols_peak], column_config=col_cfg_peak, hide_index=True, use_container_width=True, height=360)

    else:
        st.info("Tidak ditemukan data sentimen negatif atau kolom tanggal yang valid.")


# ==========================================
# 6. HALAMAN 3: TOPIC DEEP DIVE
# ==========================================
elif st.session_state.active_page == "DEEP_DIVE":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #f0f7ff; border: 1px solid #bfdbfe; padding: 10px; border-radius: 12px; font-size: 1.3rem;">🔍</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #0f172a; font-weight:800;">TOPIC <span style="color:#0284c7; font-style: italic;">DEEP DIVE</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.1em; color: #64748b; font-weight: 700;">IN-DEPTH SINGLE TOPIC INVESTIGATION & ANALYSIS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    available_topics = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
    
    if available_topics:
        col_sel_top, col_sel_tier = st.columns([2, 1])
        with col_sel_top:
            selected_single_topic = st.selectbox("📌 Pilih Topik yang Ingin Dianalisis Secara Mendalam:", options=available_topics)
        with col_sel_tier:
            tier_list_deep = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
            selected_tier_deep = st.multiselect("Filter Tier Media", options=tier_list_deep, default=tier_list_deep)

        df_deep = df_raw[df_raw["issue_topic"] == selected_single_topic].copy()
        if selected_tier_deep and "new_tier" in df_deep.columns:
            df_deep = df_deep[df_deep["new_tier"].astype(str).isin(selected_tier_deep)]
        
        deep_total = len(df_deep)
        deep_pos = len(df_deep[df_deep["sentiment"] == "Positive"]) if "sentiment" in df_deep.columns else 0
        deep_neu = len(df_deep[df_deep["sentiment"] == "Neutral"]) if "sentiment" in df_deep.columns else 0
        deep_neg = len(df_deep[df_deep["sentiment"] == "Negative"]) if "sentiment" in df_deep.columns else 0

        # Soft Cards Deep Dive
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-white">
                    <div class="pill-title">VOLUME BERITA ISU</div>
                    <div class="pill-value">{deep_total}</div>
                    <div class="pill-sub">Total Artikel</div>
                </div>
            """, unsafe_allow_html=True)
        with d2:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-green">
                    <div class="pill-title">POSITIVE</div>
                    <div class="pill-value">{deep_pos}</div>
                    <div class="pill-sub">{(deep_pos/deep_total*100) if deep_total else 0:.1f}% DARI ISU</div>
                </div>
            """, unsafe_allow_html=True)
        with d3:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-blue">
                    <div class="pill-title">NEUTRAL</div>
                    <div class="pill-value">{deep_neu}</div>
                    <div class="pill-sub">{(deep_neu/deep_total*100) if deep_total else 0:.1f}% DARI ISU</div>
                </div>
            """, unsafe_allow_html=True)
        with d4:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-orange">
                    <div class="pill-title">NEGATIVE</div>
                    <div class="pill-value">{deep_neg}</div>
                    <div class="pill-sub">{(deep_neg/deep_total*100) if deep_total else 0:.1f}% BUTUH MITIGASI</div>
                </div>
            """, unsafe_allow_html=True)

        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Proporsi Sentiment: {selected_single_topic}</p>", unsafe_allow_html=True)
            if not df_deep.empty and "sentiment" in df_deep.columns:
                fig_deep_pie = px.pie(df_deep, names='sentiment', hole=0.5, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_deep_pie.update_traces(textinfo='percent+value')
                fig_deep_pie = apply_clean_white_layout(fig_deep_pie, height=310)
                st.plotly_chart(fig_deep_pie, use_container_width=True)
            
        with col_g2:
            st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Sebaran Media Tier: {selected_single_topic}</p>", unsafe_allow_html=True)
            if not df_deep.empty and "new_tier" in df_deep.columns and "sentiment" in df_deep.columns:
                df_deep_tier = df_deep.groupby(['new_tier', 'sentiment']).size().reset_index(name='count')
                fig_deep_tier = px.bar(df_deep_tier, x='new_tier', y='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='stack', text='count')
                fig_deep_tier = apply_clean_white_layout(fig_deep_tier, height=310)
                fig_deep_tier.update_layout(xaxis_title="Tier Media", yaxis_title="Jumlah")
                st.plotly_chart(fig_deep_tier, use_container_width=True)

        st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Daftar Berita & Ringkasan Khusus Topik: '{selected_single_topic}'</p>", unsafe_allow_html=True)
        cols_deep = [c for c in ["news_date", "domain", "new_tier", "sentiment", "gemini_summary", "news_url"] if c in df_deep.columns]
        col_cfg_deep = {
            "gemini_summary": st.column_config.TextColumn("Ringkasan Berita (Gemini Summary)", width="large"),
            "news_url": st.column_config.LinkColumn("Link Berita", display_text="Buka Link 🔗"),
            "domain": st.column_config.TextColumn("Media Domain"),
            "news_date": st.column_config.DateColumn("Tanggal", format="YYYY-MM-DD")
        }
        st.dataframe(df_deep[cols_deep], column_config=col_cfg_deep, hide_index=True, use_container_width=True, height=380)

    else:
        st.warning("Kolom `issue_topic` tidak ditemukan pada dataset.")

# ==========================================
# 7. FOOTER
# ==========================================
st.markdown("---")
st.markdown("<center style='color:#94a3b8; font-size:0.8rem; font-weight:600;'>© Copyright PT Pertamina (Persero) 2026. All Rights Reserved</center>", unsafe_allow_html=True)
