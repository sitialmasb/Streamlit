import streamlit as st
import plotly.express as px
from utils import color_map_sentiment, apply_clean_white_layout

def render_deepdive_page(df_raw):
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">🔍</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #0f172a; font-weight:800;">DEEP DIVE <span style="color:#0284c7; font-style: italic;">ANALYSIS</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.1em; color: #64748b; font-weight: 700;">GRANULAR EXPLORATION & ARTICLE EXPLORER</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if df_raw.empty:
        st.info("Tidak ada data yang tersedia untuk dianalisis.")
        return

    # Filter Section for Deep Dive
    f1, f2, f3 = st.columns(3)
    with f1:
        topic_list = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
        selected_topic = st.multiselect("Filter Issue Topic", options=topic_list, default=topic_list, key="dd_topic")
    with f2:
        tier_list = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
        selected_tier = st.multiselect("Filter Media Tier", options=tier_list, default=tier_list, key="dd_tier")
    with f3:
        sent_list = sorted(list(df_raw["sentiment"].dropna().unique())) if "sentiment" in df_raw.columns else []
        selected_sent = st.multiselect("Filter Sentiment", options=sent_list, default=sent_list, key="dd_sent")

    df_filtered = df_raw.copy()
    if selected_topic and "issue_topic" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["issue_topic"].astype(str).isin(selected_topic)]
    if selected_tier and "new_tier" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["new_tier"].astype(str).isin(selected_tier)]
    if selected_sent and "sentiment" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["sentiment"].isin(selected_sent)]

    st.markdown("---")
    st.markdown("<p style='font-weight:700; font-size:1.1rem; color:#1e293b;'>Detailed Article Explorer (Deep Dive Feed)</p>", unsafe_allow_html=True)

    # Search Bar & Sentiment Filter untuk Deep Dive
    col_search, col_filter = st.columns([2, 1.2])
    with col_search:
        search_keyword = st.text_input(
            "Cari berita mendalam (Judul/Domain/Ringkasan):", 
            placeholder="Ketik kata kunci...", 
            key="search_deepdive"
        )
    with col_filter:
        table_sent = st.selectbox(
            "Filter Sentiment Tabel:",
            options=["All Sentiments", "Positive", "Neutral", "Negative"],
            index=0,
            key="tbl_sent_dd"
        )

    df_table = df_filtered.copy()
    if table_sent != "All Sentiments" and "sentiment" in df_table.columns:
        df_table = df_table[df_table["sentiment"] == table_sent]

    if search_keyword:
        keyword = search_keyword.lower()
        mask = False
        for col in ["domain", "issue_topic", "gemini_summary", "ai_summary", "news_title", "title"]:
            if col in df_table.columns:
                mask = mask | df_table[col].astype(str).str.lower().str.contains(keyword, na=False)
        df_table = df_table[mask]

    summary_col = "gemini_summary" if "gemini_summary" in df_table.columns else ("ai_summary" if "ai_summary" in df_table.columns else None)
    base_cols = ["news_date", "domain", "new_tier", "issue_topic", "sentiment"]
    if summary_col:
        base_cols.append(summary_col)
    if "news_url" in df_table.columns:
        base_cols.append("news_url")

    cols = [c for c in base_cols if c in df_table.columns]
    col_config = {
        "news_url": st.column_config.LinkColumn("Article URL", display_text="Open Link 🔗"),
        "domain": st.column_config.TextColumn("Media Domain"),
        "news_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        "sentiment": st.column_config.TextColumn("Sentiment"),
        "issue_topic": st.column_config.TextColumn("Issue Topic"),
        "new_tier": st.column_config.TextColumn("Tier")
    }
    if summary_col:
        col_config[summary_col] = st.column_config.TextColumn("Article Summary (AI Summary)", width="large")

    st.dataframe(df_table[cols], column_config=col_config, hide_index=True, use_container_width=True, height=500)
