import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA TERANG
# ==========================================
st.set_page_config(
    page_title="SENTIMENT ANALYSIS",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "MONITORING"

# Custom CSS: Menghilangkan Space Atas & Merapikan Elemen
st.markdown("""
<style>
    /* 1. Base App & Hilangkan Space/Padding Kosong di Atas Halaman */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
    }
    
    /* Pangkas jarak kosong di bagian atas aplikasi utama */
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
        border-right: 1px solid #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        gap: 0.35rem !important;
    }

    /* 2. Global Text */
    html, body, p, span, h1, h2, h3, h4, h5, h6, label, small, strong, div {
        color: #0f172a !important;
    }

    /* 3. Label Filter & Widget */
    [data-testid="stWidgetLabel"] label, 
    [data-testid="stWidgetLabel"] p,
    .stSelectbox label, 
    .stMultiSelect label {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
    }

    /* 4. Selectbox & Multiselect */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div,
    div[role="combobox"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        color: #000000 !important;
    }

    /* 5. Tag/Chip Multiselect */
    div[data-baseweb="select"] span[data-baseweb="tag"],
    span[data-baseweb="tag"] {
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] span[data-baseweb="tag"] span,
    span[data-baseweb="tag"] span {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="select"] span[data-baseweb="tag"] svg,
    span[data-baseweb="tag"] svg {
        fill: #475569 !important;
        color: #475569 !important;
    }

    /* 6. Metric Cards Sesuai Desain */
    .metric-pill-card {
        border-radius: 24px !important;
        padding: 20px 22px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
    }
    
    .card-white {
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0;
    }
    .card-white .pill-title { color: #2563eb !important; font-weight: 800; }
    .card-white .pill-value { color: #0f172a !important; }
    .card-white .pill-sub { color: #10b981 !important; }

    .card-green {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: #ffffff !important;
    }
    .card-blue {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
        color: #ffffff !important;
    }
    .card-orange {
        background: linear-gradient(135deg, #ea580c, #f97316) !important;
        color: #ffffff !important;
    }
    .card-slate {
        background: linear-gradient(135deg, #475569, #64748b) !important;
        color: #ffffff !important;
    }

    .pill-title {
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: rgba(255, 255, 255, 0.95);
    }
    .pill-value {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 4px 0;
        color: #ffffff;
    }
    .pill-sub {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: rgba(255, 255, 255, 0.9);
    }

    /* 7. Alert Box Peak Sentimen Negatif */
    .alert-peak-box {
        background: #ffffff;
        border-left: 5px solid #dc2626;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 18px;
        margin-top: 8px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }

    /* 8. Tabs Navigasi */
    button[data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 3px solid #2563eb !important;
    }

    /* 9. Dataframe Container */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* 10. Tombol Menu Navigasi di Sidebar */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 4px;
        font-weight: 700;
        font-size: 0.82rem;
        border: 1px solid #cbd5e1 !important;
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #e2e8f0 !important;
        border-color: #94a3b8 !important;
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: #eff6ff !important;
        color: #2563eb !important;
        border-color: #93c5fd !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. STANDARISASI SENTIMEN & LOAD DATASET
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
            
    # Dummy fallback
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

color_map_sentiment = {
    'Positive': '#10b981',
    'Neutral': '#3b82f6',
    'Negative': '#f97316'
}

def apply_clean_white_layout(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#000000", size=11, family="Arial"),
        xaxis=dict(
            showgrid=True, 
            gridcolor="#f1f5f9", 
            linecolor="#cbd5e1",
            tickfont=dict(color="#000000", size=10)
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#f1f5f9", 
            linecolor="#cbd5e1",
            tickfont=dict(color="#000000", size=10)
        ),
        legend=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#cbd5e1",
            borderwidth=1,
            font=dict(color="#000000")
        )
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
    sample_summary = df_peak_news["gemini_summary"].iloc[0] if "gemini_summary" in df_peak_news.columns and not df_peak_news.empty else "-"
    
    return {
        "peak_date": peak_date.strftime('%d %B %Y'),
        "peak_date_raw": peak_date,
        "peak_count": peak_count,
        "cause_topic": top_cause_topic,
        "summary": sample_summary,
        "daily_trend": df_neg_daily
    }


# ==========================================
# 3. SIDEBAR: NAVIGATION MENU SAJA
# ==========================================
with st.sidebar:
    st.markdown("<p style='font-size: 0.85rem; font-weight: 800; margin-bottom: 4px; color:#0f172a;'>MENU DASHBOARD</p>", unsafe_allow_html=True)
    
    btn_mon = st.button(
        "📊 SENTIMENT & ISSUE TOPIC MONITORING",
        key="nav_mon",
        type="primary" if st.session_state.active_page == "MONITORING" else "secondary",
        use_container_width=True
    )
    if btn_mon:
        st.session_state.active_page = "MONITORING"
        st.rerun()

    btn_deep = st.button(
        "🔍 TOPIC DEEP DIVE",
        key="nav_deep",
        type="primary" if st.session_state.active_page == "DEEP_DIVE" else "secondary",
        use_container_width=True
    )
    if btn_deep:
        st.session_state.active_page = "DEEP_DIVE"
        st.rerun()

    st.write("")
    if loaded_file_name:
        st.success(f" Terhubung: `{loaded_file_name}`")
    else:
        st.info("💡 Memakai data sampel bawaan.")


# ==========================================
# 4. HALAMAN 1: MONITORING
# ==========================================
if st.session_state.active_page == "MONITORING":
    # Header Icon Putih Berborder Abu
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">📡</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #000000; font-weight:800;">TKB NEWS'S <span style="color:#2563eb; font-style: italic;">SENTIMENT ANALYSIS</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.12em; color: #334155; font-weight: 700;">SENTIMENT & ISSUE TOPIC MONITORING</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # In-page Filters Langsung (Tanpa div kosong)
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sent_list = sorted(list(df_raw["sentiment"].dropna().unique())) if "sentiment" in df_raw.columns else []
        selected_sent = st.multiselect("Sentiment", options=sent_list, default=sent_list, key="mon_sent")
    with f2:
        tier_list = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
        selected_tier = st.multiselect("Tier Media", options=tier_list, default=tier_list, key="mon_tier")
    with f3:
        topic_list = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
        selected_topic = st.multiselect("Issue Topic", options=topic_list, default=topic_list, key="mon_topic")
    with f4:
        domain_list = sorted(list(df_raw["domain"].dropna().astype(str).unique())) if "domain" in df_raw.columns else []
        selected_domain = st.multiselect("Media Domain", options=domain_list, default=[], key="mon_domain")

    # Terapkan Filter
    df_filtered = df_raw.copy()
    if selected_sent and "sentiment" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["sentiment"].isin(selected_sent)]
    if selected_tier and "new_tier" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["new_tier"].astype(str).isin(selected_tier)]
    if selected_domain and "domain" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["domain"].astype(str).isin(selected_domain)]
    if selected_topic and "issue_topic" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["issue_topic"].astype(str).isin(selected_topic)]

    # Hitung Nilai KPI
    total_news = len(df_filtered)
    pos_count = len(df_filtered[df_filtered["sentiment"] == "Positive"]) if "sentiment" in df_filtered.columns else 0
    neu_count = len(df_filtered[df_filtered["sentiment"] == "Neutral"]) if "sentiment" in df_filtered.columns else 0
    neg_count = len(df_filtered[df_filtered["sentiment"] == "Negative"]) if "sentiment" in df_filtered.columns else 0
    top_topic = df_filtered["issue_topic"].mode()[0] if not df_filtered.empty and "issue_topic" in df_filtered.columns else "-"

    # Baris Metric Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
            <div class="metric-pill-card card-white">
                <div class="pill-title">TOTAL NEWS</div>
                <div class="pill-value">{total_news}</div>
                <div class="pill-sub">↑ Performance</div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
            <div class="metric-pill-card card-green">
                <div class="pill-title">POSITIVE</div>
                <div class="pill-value">{pos_count}</div>
                <div class="pill-sub">{(pos_count/total_news*100) if total_news else 0:.1f}% DARI TOTAL</div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="metric-pill-card card-blue">
                <div class="pill-title">NEUTRAL</div>
                <div class="pill-value">{neu_count}</div>
                <div class="pill-sub">{(neu_count/total_news*100) if total_news else 0:.1f}% DARI TOTAL</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
            <div class="metric-pill-card card-orange">
                <div class="pill-title">NEGATIVE</div>
                <div class="pill-value">{neg_count}</div>
                <div class="pill-sub">MITIGATION ONGOING</div>
            </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
            <div class="metric-pill-card card-slate">
                <div class="pill-title">TOP TOPIC</div>
                <div class="pill-value" style="font-size:1.35rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{top_topic}">{top_topic}</div>
                <div class="pill-sub">VOLUME TERBESAR</div>
            </div>
        """, unsafe_allow_html=True)

    # Banner Peak Negative Alert
    peak_info = analyze_negative_peak(df_filtered)
    if peak_info:
        st.markdown(f"""
            <div class="alert-peak-box">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                    <span style="font-weight:800; font-size:0.95rem; color:#dc2626;">🚨 NEGATIVE SENTIMENT PEAK DETECTED</span>
                    <span style="background:#fee2e2; color:#b91c1c; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;">
                        Lonjakan: {peak_info['peak_count']} Berita Negatif
                    </span>
                </div>
                <div style="font-size:0.88rem; color:#1e293b; margin-bottom:4px;">
                    <b>Periode Puncak:</b> <span style="color:#0f172a; font-weight:700;">{peak_info['peak_date']}</span> &nbsp;|&nbsp; 
                    <b>Faktor Penyebab Utama:</b> <span style="background:#f1f5f9; border:1px solid #cbd5e1; padding:2px 8px; border-radius:6px; font-weight:700;">{peak_info['cause_topic']}</span>
                </div>
                <div style="font-size:0.83rem; color:#475569; background:#f8fafc; padding:8px 12px; border-radius:6px; border:1px solid #e2e8f0;">
                    <b>Ringkasan Isu Terkait:</b> "{peak_info['summary']}"
                </div>
            </div>
        """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Distribusi Sentiment & Trend Peak", "📌 Sebaran Issue Topic", "📰 Gemini AI News Feed"])
    
    with tab1:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            st.markdown("<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Porsi Sentiment</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "sentiment" in df_filtered.columns:
                fig_pie = px.pie(df_filtered, names='sentiment', hole=0.55, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_pie.update_traces(textinfo='percent+value')
                fig_pie = apply_clean_white_layout(fig_pie, height=330)
                st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            st.markdown("<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Tren Harian Sentimen Negatif & Titik Puncak</p>", unsafe_allow_html=True)
            if peak_info and not peak_info["daily_trend"].empty:
                df_trend = peak_info["daily_trend"]
                fig_trend = go.Figure()
                
                fig_trend.add_trace(go.Scatter(
                    x=df_trend["news_date"],
                    y=df_trend["count"],
                    mode='lines+markers',
                    name='Negative News',
                    line=dict(color='#ea580c', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(234, 88, 12, 0.1)'
                ))
                
                fig_trend.add_trace(go.Scatter(
                    x=[peak_info["peak_date_raw"]],
                    y=[peak_info["peak_count"]],
                    mode='markers+text',
                    name='Peak Point',
                    text=[f"Peak: {peak_info['peak_count']}"],
                    textposition="top center",
                    marker=dict(color='#991b1b', size=12, symbol='circle')
                ))
                
                fig_trend = apply_clean_white_layout(fig_trend, height=330)
                fig_trend.update_layout(xaxis_title="Tanggal Berita", yaxis_title="Jumlah Berita Negatif")
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Data sentimen negatif belum memiliki tanggal yang valid untuk tren waktu.")

    with tab2:
        c_top1, c_top2 = st.columns([1.2, 1])
        with c_top1:
            st.markdown("<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Komposisi Sentiment per Issue Topic</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "issue_topic" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_top_sent = df_filtered.groupby(['issue_topic', 'sentiment']).size().reset_index(name='count')
                fig_top = px.bar(df_top_sent, y='issue_topic', x='count', color='sentiment', color_discrete_map=color_map_sentiment, orientation='h', barmode='stack')
                fig_top = apply_clean_white_layout(fig_top, height=340)
                fig_top.update_layout(yaxis_title="", xaxis_title="Jumlah Berita")
                st.plotly_chart(fig_top, use_container_width=True)
            
        with c_top2:
            st.markdown("<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Top Domain Media (Volume)</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "domain" in df_filtered.columns:
                top_domains = df_filtered['domain'].value_counts().head(8).reset_index()
                top_domains.columns = ['Domain', 'Count']
                fig_domains = px.bar(top_domains, x='Count', y='Domain', orientation='h', color_discrete_sequence=['#2563eb'], text='Count')
                fig_domains = apply_clean_white_layout(fig_domains, height=340)
                fig_domains.update_layout(yaxis=dict(autorange="reversed"), yaxis_title="", xaxis_title="Total Berita")
                st.plotly_chart(fig_domains, use_container_width=True)

    with tab3:
        st.markdown("<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Detail Feed Berita & Ringkasan Gemini AI</p>", unsafe_allow_html=True)
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
# 5. HALAMAN 2: TOPIC DEEP DIVE
# ==========================================
elif st.session_state.active_page == "DEEP_DIVE":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">🔍</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #000000; font-weight:800;">TOPIC <span style="color:#2563eb; font-style: italic;">DEEP DIVE</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.12em; color: #334155; font-weight: 700;">IN-DEPTH SINGLE TOPIC INVESTIGATION & ANALYSIS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    available_topics = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
    
    if available_topics:
        # Filter Langsung (Tanpa div kosong)
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

        # Cards Pill Deep Dive
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f"""
                <div class="metric-pill-card card-white">
                    <div class="pill-title">VOLUME BERITA ISU</div>
                    <div class="pill-value">{deep_total}</div>
                    <div class="pill-sub">Total Artikel</div>
                </div>
            """, unsafe_allow_html=True)
        with d2:
            st.markdown(f"""
                <div class="metric-pill-card card-green">
                    <div class="pill-title">POSITIVE</div>
                    <div class="pill-value">{deep_pos}</div>
                    <div class="pill-sub">{(deep_pos/deep_total*100) if deep_total else 0:.1f}% DARI ISU</div>
                </div>
            """, unsafe_allow_html=True)
        with d3:
            st.markdown(f"""
                <div class="metric-pill-card card-blue">
                    <div class="pill-title">NEUTRAL</div>
                    <div class="pill-value">{deep_neu}</div>
                    <div class="pill-sub">{(deep_neu/deep_total*100) if deep_total else 0:.1f}% DARI ISU</div>
                </div>
            """, unsafe_allow_html=True)
        with d4:
            st.markdown(f"""
                <div class="metric-pill-card card-orange">
                    <div class="pill-title">NEGATIVE</div>
                    <div class="pill-value">{deep_neg}</div>
                    <div class="pill-sub">{(deep_neg/deep_total*100) if deep_total else 0:.1f}% BUTUH MITIGASI</div>
                </div>
            """, unsafe_allow_html=True)

        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            st.markdown(f"<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Proporsi Sentiment: {selected_single_topic}</p>", unsafe_allow_html=True)
            if not df_deep.empty and "sentiment" in df_deep.columns:
                fig_deep_pie = px.pie(df_deep, names='sentiment', hole=0.5, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_deep_pie.update_traces(textinfo='percent+value')
                fig_deep_pie = apply_clean_white_layout(fig_deep_pie, height=310)
                st.plotly_chart(fig_deep_pie, use_container_width=True)
            
        with col_g2:
            st.markdown(f"<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Sebaran Media Tier: {selected_single_topic}</p>", unsafe_allow_html=True)
            if not df_deep.empty and "new_tier" in df_deep.columns and "sentiment" in df_deep.columns:
                df_deep_tier = df_deep.groupby(['new_tier', 'sentiment']).size().reset_index(name='count')
                fig_deep_tier = px.bar(df_deep_tier, x='new_tier', y='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='stack', text='count')
                fig_deep_tier = apply_clean_white_layout(fig_deep_tier, height=310)
                fig_deep_tier.update_layout(xaxis_title="Tier Media", yaxis_title="Jumlah")
                st.plotly_chart(fig_deep_tier, use_container_width=True)

        st.markdown(f"<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Daftar Berita & Ringkasan Khusus Topik: '{selected_single_topic}'</p>", unsafe_allow_html=True)
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
# 6. FOOTER
# ==========================================
st.markdown("---")
st.markdown("<center style='color:#64748b; font-size:0.8rem; font-weight:700;'>© Copyright PT Pertamina (Persero) 2026. All Rights Reserved</center>", unsafe_allow_html=True)
