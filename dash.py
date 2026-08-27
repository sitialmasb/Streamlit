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

# Custom CSS
st.markdown("""
<style>
    /* 1. Base App & Sidebar Background */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #cbd5e1 !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        gap: 0.35rem !important;
    }

    /* 2. Global Text: Hitam Pekat */
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
        font-size: 0.88rem !important;
    }

    /* 4. Selectbox & Multiselect: Abu-Abu Lembut */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div,
    div[role="combobox"] {
        background-color: #f1f5f9 !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        color: #000000 !important;
    }

    /* 5. Tag/Chip Multiselect */
    div[data-baseweb="select"] span[data-baseweb="tag"],
    span[data-baseweb="tag"] {
        background-color: #e2e8f0 !important;
        border: 1px solid #94a3b8 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] span[data-baseweb="tag"] span,
    span[data-baseweb="tag"] span {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="select"] span[data-baseweb="tag"] svg,
    span[data-baseweb="tag"] svg {
        fill: #000000 !important;
        color: #000000 !important;
    }

    /* 6. Metric Cards */
    .metric-card {
        border-radius: 12px;
        padding: 16px 20px;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 800;
        color: #334155 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #000000 !important;
        margin: 4px 0;
    }
    .metric-sub {
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* 7. Tabs Navigasi */
    button[data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 3px solid #2563eb !important;
    }

    /* 8. Dataframe Container */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* 9. Tombol Menu Navigasi */
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 2px;
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
    # Dapatkan direktori absolut dari file script yang sedang berjalan
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Daftar nama file yang dicari di folder
    candidate_files = [
        "data.xlsx"
    ]
    
    file_found = None
    for f in candidate_files:
        full_path = os.path.join(current_dir, f)
        if os.path.exists(full_path):
            file_found = full_path
            break
        # Fallback pencarian direktori relatif
        elif os.path.exists(f):
            file_found = f
            break
            
    if file_found:
        try:
            if file_found.endswith('.csv'):
                # Handle separator koma atau titik koma otomatis
                try:
                    df = pd.read_csv(file_found)
                except Exception:
                    df = pd.read_csv(file_found, sep=';')
            else:
                df = pd.read_excel(file_found)
            
            # Bersihkan nama kolom menjadi lowercase
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            if "sentiment" in df.columns:
                df["sentiment"] = df["sentiment"].apply(standardize_sentiment_en)
            
            if "news_date" in df.columns:
                df["news_date"] = pd.to_datetime(df["news_date"], errors="coerce")
                
            return df, os.path.basename(file_found)
        except Exception as e:
            st.error(f"Gagal membaca file {file_found}: {e}")
            
    # Dummy fallback jika file benar-benar tidak ditemukan
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
    'Neutral': '#f59e0b',
    'Negative': '#ef4444'
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


# ==========================================
# 3. SIDEBAR: MENU & FILTERS
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

    if loaded_file_name:
        st.success(f" Terhubung: `{loaded_file_name}`")
    else:
        st.info("💡 Memakai data sampel bawaan.")

    st.markdown("<p style='font-size: 0.85rem; font-weight: 800; margin-top: 10px; margin-bottom: 2px; color:#0f172a;'>🎯 FILTER DATA</p>", unsafe_allow_html=True)

    sent_list = sorted(list(df_raw["sentiment"].dropna().unique())) if "sentiment" in df_raw.columns else []
    selected_sent = st.multiselect("Sentiment", options=sent_list, default=sent_list)

    tier_list = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
    selected_tier = st.multiselect("Tier Media", options=tier_list, default=tier_list)

    domain_list = sorted(list(df_raw["domain"].dropna().astype(str).unique())) if "domain" in df_raw.columns else []
    selected_domain = st.multiselect("Media Domain", options=domain_list, default=[])

    topic_list = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
    if st.session_state.active_page == "MONITORING":
        selected_topic = st.multiselect("Issue Topic", options=topic_list, default=topic_list)
    else:
        selected_topic = topic_list


# Terapkan Filter
df_filtered = df_raw.copy()
if selected_sent and "sentiment" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["sentiment"].isin(selected_sent)]
if selected_tier and "new_tier" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["new_tier"].astype(str).isin(selected_tier)]
if selected_domain and "domain" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["domain"].astype(str).isin(selected_domain)]
if st.session_state.active_page == "MONITORING" and selected_topic and "issue_topic" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["issue_topic"].astype(str).isin(selected_topic)]


# ==========================================
# 4. HALAMAN 1: MONITORING
# ==========================================
if st.session_state.active_page == "MONITORING":
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">📡</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #000000; font-weight:800;">TKB NEWS'S <span style="color:#2563eb; font-style: italic;">SENTIMENT ANALYSIS</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.12em; color: #334155; font-weight: 700;">SENTIMENT & ISSUE TOPIC MONITORING</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    total_news = len(df_filtered)
    pos_count = len(df_filtered[df_filtered["sentiment"] == "Positive"]) if "sentiment" in df_filtered.columns else 0
    neu_count = len(df_filtered[df_filtered["sentiment"] == "Neutral"]) if "sentiment" in df_filtered.columns else 0
    neg_count = len(df_filtered[df_filtered["sentiment"] == "Negative"]) if "sentiment" in df_filtered.columns else 0
    top_topic = df_filtered["issue_topic"].mode()[0] if not df_filtered.empty and "issue_topic" in df_filtered.columns else "-"

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total News</div><div class="metric-value">{total_news}</div><div class="metric-sub" style="color:#2563eb;">Berita Terdata</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Positive</div><div class="metric-value" style="color:#10b981;">{pos_count}</div><div class="metric-sub" style="color:#10b981;">{(pos_count/total_news*100) if total_news else 0:.1f}%</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Neutral</div><div class="metric-value" style="color:#d97706;">{neu_count}</div><div class="metric-sub" style="color:#d97706;">{(neu_count/total_news*100) if total_news else 0:.1f}%</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Negative</div><div class="metric-value" style="color:#dc2626;">{neg_count}</div><div class="metric-sub" style="color:#dc2626;">Perlu Tindakan</div></div>', unsafe_allow_html=True)
    with k5:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Top Topic</div><div class="metric-value" style="color:#7c3aed; font-size:1.15rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{top_topic}">{top_topic}</div><div class="metric-sub" style="color:#7c3aed;">Volume Terbesar</div></div>', unsafe_allow_html=True)

    st.write("")

    tab1, tab2, tab3 = st.tabs(["📈 Distribusi Sentiment & Media", "📌 Sebaran Issue Topic", "📰 Gemini AI News Feed"])
    
    with tab1:
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown("<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Porsi Sentiment</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "sentiment" in df_filtered.columns:
                fig_pie = px.pie(df_filtered, names='sentiment', hole=0.55, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_pie.update_traces(textinfo='percent+value')
                fig_pie = apply_clean_white_layout(fig_pie, height=330)
                st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            st.markdown("<p style='font-weight:700; font-size:1.05rem; margin-bottom:6px; color:#000;'>Sentiment Berdasarkan Tier Media</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "new_tier" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_tier_sent = df_filtered.groupby(['new_tier', 'sentiment']).size().reset_index(name='count')
                fig_tier = px.bar(df_tier_sent, x='new_tier', y='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='group', text='count')
                fig_tier = apply_clean_white_layout(fig_tier, height=330)
                fig_tier.update_layout(xaxis_title="Tier Media", yaxis_title="Jumlah Berita")
                st.plotly_chart(fig_tier, use_container_width=True)

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
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">🔍</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #000000; font-weight:800;">TOPIC <span style="color:#2563eb; font-style: italic;">DEEP DIVE</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.12em; color: #334155; font-weight: 700;">IN-DEPTH SINGLE TOPIC INVESTIGATION & ANALYSIS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    available_topics = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
    
    if available_topics:
        selected_single_topic = st.selectbox("📌 Pilih Topik yang Ingin Dianalisis Secara Mendalam:", options=available_topics)
        
        df_deep = df_filtered[df_filtered["issue_topic"] == selected_single_topic]
        
        deep_total = len(df_deep)
        deep_pos = len(df_deep[df_deep["sentiment"] == "Positive"]) if "sentiment" in df_deep.columns else 0
        deep_neu = len(df_deep[df_deep["sentiment"] == "Neutral"]) if "sentiment" in df_deep.columns else 0
        deep_neg = len(df_deep[df_deep["sentiment"] == "Negative"]) if "sentiment" in df_deep.columns else 0

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Volume Berita Isu</div><div class="metric-value">{deep_total}</div><div class="metric-sub" style="color:#2563eb;">Total Artikel</div></div>', unsafe_allow_html=True)
        with d2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Positive</div><div class="metric-value" style="color:#10b981;">{deep_pos}</div><div class="metric-sub" style="color:#10b981;">{(deep_pos/deep_total*100) if deep_total else 0:.1f}%</div></div>', unsafe_allow_html=True)
        with d3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Neutral</div><div class="metric-value" style="color:#d97706;">{deep_neu}</div><div class="metric-sub" style="color:#d97706;">{(deep_neu/deep_total*100) if deep_total else 0:.1f}%</div></div>', unsafe_allow_html=True)
        with d4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Negative</div><div class="metric-value" style="color:#dc2626;">{deep_neg}</div><div class="metric-sub" style="color:#dc2626;">Perlu Tindakan</div></div>', unsafe_allow_html=True)

        st.write("")

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
