import streamlit as st
import plotly.express as px
from utils import color_map_sentiment, apply_clean_white_layout

def render_alert_page(df_raw):
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">🚨</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #0f172a; font-weight:800;">CRITICAL ALERTS & <span style="color:#ef4444; font-style: italic;">NEGATIVE MONITOR</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.1em; color: #64748b; font-weight: 700;">HIGH PRIORITY RISK & NEGATIVE NEWS TRACKING</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if df_raw.empty:
        st.info("Tidak ada data untuk dianalisis.")
        return

    # Filter khusus untuk isu negatif / kritikal
    df_alert = df_raw.copy()
    if "sentiment" in df_alert.columns:
        df_alert = df_alert[df_alert["sentiment"] == "Negative"]

    st.markdown("---")
    st.markdown("<p style='font-weight:700; font-size:1.1rem; color:#1e293b;'>Negative News & Risk Feed</p>", unsafe_allow_html=True)

    if df_alert.empty:
        st.success("Bagus sekali! Tidak ada berita dengan sentimen negatif saat ini.")
        return

    # Search Bar khusus di halaman Alert
    col_search, col_dummy = st.columns([2, 1.2])
    with col_search:
        search_keyword = st.text_input(
            "Cari berita negatif / risiko:", 
            placeholder="Ketik kata kunci...", 
            key="search_alert"
        )

    if search_keyword:
        keyword = search_keyword.lower()
        mask = False
        for col in ["domain", "issue_topic", "gemini_summary", "ai_summary", "news_title", "title"]:
            if col in df_alert.columns:
                mask = mask | df_alert[col].astype(str).str.lower().str.contains(keyword, na=False)
        df_alert = df_alert[mask]

    summary_col = "gemini_summary" if "gemini_summary" in df_alert.columns else ("ai_summary" if "ai_summary" in df_alert.columns else None)
    base_cols = ["news_date", "domain", "new_tier", "issue_topic", "sentiment"]
    if summary_col:
        base_cols.append(summary_col)
    if "news_url" in df_alert.columns:
        base_cols.append("news_url")

    cols = [c for c in base_cols if c in df_alert.columns]
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

    st.dataframe(df_alert[cols], column_config=col_config, hide_index=True, use_container_width=True, height=500)
