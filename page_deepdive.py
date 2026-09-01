import streamlit as st
import plotly.express as px
import pandas as pd
from utils import color_map_sentiment, apply_clean_white_layout, get_base64_image

def render_deepdive_page(df_raw):
    icon_deepdive_b64 = get_base64_image("assets/icons/icon_deepdive.png")
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
            <div style="background: #f0f7ff; border: 1px solid #237ece; padding: 6px; border-radius: 8px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                <img src="{icon_deepdive_b64}" width="20" height="20" style="object-fit: contain;" />
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.3rem; color: #0f172a; font-weight:800;">TOPIC & SUBTOPIC <span style="color:#237ece; font-style: italic;">DEEP DIVE</span></h2>
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; color: #64748b; font-weight: 700;">IN-DEPTH TOPIC & SUBTOPIC INVESTIGATION</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "selected_deepdive_topic" not in st.session_state:
        st.session_state.selected_deepdive_topic = None

    if "topic" not in df_raw.columns:
        st.warning("Kolom `topic` tidak ditemukan di dalam dataset.")
        return

    # Urutkan topik dari jumlah artikel terbanyak (Descending)
    available_topics = df_raw["topic"].dropna().astype(str).value_counts().index.tolist()

    # =============================================================
    # TAMPILAN 1: GRID KARTU TOPIK (CLICKABLE CARD WIDGET)
    # =============================================================
    if st.session_state.selected_deepdive_topic is None:
        st.markdown("""
            <style>
                div[data-testid="stColumn"] div.stButton > button {
                    width: 100% !important;
                    min-height: 115px !important;
                    background-color: #ffffff !important;
                    border: 1px solid #e2e8f0 !important;
                    border-radius: 12px !important;
                    padding: 16px !important;
                    margin-bottom: 14px !important;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
                    text-align: left !important;
                    display: flex !important;
                    flex-direction: column !important;
                    justify-content: flex-start !important;
                    align-items: flex-start !important;
                    white-space: pre-wrap !important;
                    cursor: pointer !important;
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                }
                div[data-testid="stColumn"] div.stButton > button p {
                    text-align: left !important;
                    width: 100% !important;
                    color: #0f172a !important;
                    line-height: 1.4 !important;
                }
                div[data-testid="stColumn"] div.stButton > button:hover {
                    border-color: #237ece !important;
                    background-color: #f8fafc !important;
                    box-shadow: 0 8px 16px rgba(35, 126, 206, 0.12) !important;
                    transform: translateY(-3px) !important;
                }
                div[data-testid="stColumn"] div.stButton > button:active {
                    transform: translateY(0) !important;
                }
            </style>
        """, unsafe_allow_html=True)

        cols_per_row = 3
        for i in range(0, len(available_topics), cols_per_row):
            row_topics = available_topics[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            
            for j, t in enumerate(row_topics):
                with cols[j]:
                    df_t = df_raw[df_raw["topic"] == t]
                    t_total = len(df_t)
                    t_pos = len(df_t[df_t["sentiment"] == "Positive"]) if "sentiment" in df_t.columns else 0
                    t_neg = len(df_t[df_t["sentiment"] == "Negative"]) if "sentiment" in df_t.columns else 0
                    subtopic_count = df_t["subtopic"].nunique() if "subtopic" in df_t.columns else 0

                    card_label = f"📁 {t}\n\n{t_total} ARTICLES       🟢 {t_pos} Pos | 🔴 {t_neg} Neg\n🔖 {subtopic_count} Subtopics Available"
                    
                    if st.button(card_label, key=f"btn_fullcard_{t}", use_container_width=True):
                        st.session_state.selected_deepdive_topic = t
                        st.rerun()

    # =============================================================
    # TAMPILAN 2: DETAIL INVESTIGASI TOPIK (SETELAH KARTU DI-KLIK)
    # =============================================================
    else:
        selected_single_topic = st.session_state.selected_deepdive_topic

        col_back, _ = st.columns([1.5, 4.5])
        with col_back:
            if st.button("← Back to All Topics", key="btn_back_to_topics", type="primary", use_container_width=True):
                st.session_state.selected_deepdive_topic = None
                st.rerun()

        st.markdown(f"""
            <div style="margin-top: 10px; margin-bottom: 8px;">
                <span style="font-size: 0.82rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em; text-transform: uppercase;">Topic Investigation:</span>
                <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">{selected_single_topic}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        df_deep = df_raw[df_raw["topic"] == selected_single_topic].copy()
        subtopics_in_topic = sorted(list(df_deep["subtopic"].dropna().astype(str).unique())) if "subtopic" in df_deep.columns else []
        tier_list_deep = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []

        col_sel_sub, col_sel_tier = st.columns([2, 1])
        with col_sel_sub:
            selected_subtopics = st.multiselect("Filter Subtopic:", options=subtopics_in_topic, default=[])
        with col_sel_tier:
            selected_tier_deep = st.multiselect("Media Tier:", options=tier_list_deep, default=[])

        if selected_subtopics and "subtopic" in df_deep.columns:
            df_deep = df_deep[df_deep["subtopic"].astype(str).isin(selected_subtopics)]
        if selected_tier_deep and "new_tier" in df_deep.columns:
            df_deep = df_deep[df_deep["new_tier"].astype(str).isin(selected_tier_deep)]

        deep_total = len(df_deep)
        deep_pos = len(df_deep[df_deep["sentiment"] == "Positive"]) if "sentiment" in df_deep.columns else 0
        deep_neu = len(df_deep[df_deep["sentiment"] == "Neutral"]) if "sentiment" in df_deep.columns else 0
        deep_neg = len(df_deep[df_deep["sentiment"] == "Negative"]) if "sentiment" in df_deep.columns else 0

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-white">
                    <div class="pill-title">TOPIC NEWS VOLUME</div>
                    <div class="pill-value">{deep_total}</div>
                    <div class="pill-sub">Total Articles in Topic</div>
                </div>
            """, unsafe_allow_html=True)
        with d2:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-green">
                    <div class="pill-title">POSITIVE</div>
                    <div class="pill-value">{deep_pos}</div>
                    <div class="pill-sub">{(deep_pos/deep_total*100) if deep_total else 0:.1f}% OF TOPIC</div>
                </div>
            """, unsafe_allow_html=True)
        with d3:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-blue">
                    <div class="pill-title">NEUTRAL</div>
                    <div class="pill-value">{deep_neu}</div>
                    <div class="pill-sub">{(deep_neu/deep_total*100) if deep_total else 0:.1f}% OF TOPIC</div>
                </div>
            """, unsafe_allow_html=True)
        with d4:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-orange">
                    <div class="pill-title">NEGATIVE</div>
                    <div class="pill-value">{deep_neg}</div>
                    <div class="pill-sub">{(deep_neg/deep_total*100) if deep_total else 0:.1f}% MITIGATION REQUIRED</div>
                </div>
            """, unsafe_allow_html=True)

        st.write("")

        col_g1, col_g2 = st.columns([1, 1.2])
        with col_g1:
            st.markdown(f"<p style='font-weight:700; font-size:0.88rem; margin-bottom:4px; color:#1e293b;'>Sentiment Proportion</p>", unsafe_allow_html=True)
            if not df_deep.empty and "sentiment" in df_deep.columns:
                fig_deep_pie = px.pie(df_deep, names='sentiment', hole=0.5, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_deep_pie.update_traces(textinfo='percent+value')
                fig_deep_pie = apply_clean_white_layout(fig_deep_pie, height=280)
                st.plotly_chart(fig_deep_pie, use_container_width=True)
            
        with col_g2:
            st.markdown(f"<p style='font-weight:700; font-size:0.88rem; margin-bottom:4px; color:#1e293b;'>Subtopic Breakdown</p>", unsafe_allow_html=True)
            if not df_deep.empty and "subtopic" in df_deep.columns and "sentiment" in df_deep.columns:
                df_deep_sub = df_deep.groupby(['subtopic', 'sentiment']).size().reset_index(name='count')
                fig_deep_sub = px.bar(df_deep_sub, y='subtopic', x='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='stack', orientation='h', text='count')
                fig_deep_sub = apply_clean_white_layout(fig_deep_sub, height=280)
                fig_deep_sub.update_layout(xaxis_title="Articles Count", yaxis_title="")
                st.plotly_chart(fig_deep_sub, use_container_width=True)

        st.markdown(f"<p style='font-weight:700; font-size:0.88rem; margin-top:10px; margin-bottom:4px; color:#1e293b;'>Article List & AI Summary</p>", unsafe_allow_html=True)
        
        col_dt_title, col_dt_filter = st.columns([2, 1.2])
        with col_dt_title:
            search_keyword_deep = st.text_input("Cari berita topik ini (Domain/Subtopic/Ringkasan):", placeholder="Ketik kata kunci...", key="search_deepdive_topic")
        with col_dt_filter:
            tbl_sent_choice_deep = st.selectbox("Filter Sentiment:", options=["All Sentiments", "Positive", "Neutral", "Negative"], index=0, key="tbl_sent_deep")
        
        df_table_deep = df_deep.copy()
        if tbl_sent_choice_deep != "All Sentiments" and "sentiment" in df_table_deep.columns:
            df_table_deep = df_table_deep[df_table_deep["sentiment"] == tbl_sent_choice_deep]

        if search_keyword_deep:
            keyword = search_keyword_deep.lower()
            mask = False
            for col in ["domain", "subtopic", "gemini_summary", "ai_summary", "news_title", "title"]:
                if col in df_table_deep.columns:
                    mask = mask | df_table_deep[col].astype(str).str.lower().str.contains(keyword, na=False)
            df_table_deep = df_table_deep[mask]

        summary_col_dp = "gemini_summary" if "gemini_summary" in df_table_deep.columns else ("ai_summary" if "ai_summary" in df_table_deep.columns else None)
        base_cols_dp = ["news_date", "domain", "new_tier", "subtopic", "sentiment"]
        if summary_col_dp:
            base_cols_dp.append(summary_col_dp)
        if "news_url" in df_table_deep.columns:
            base_cols_dp.append("news_url")

        cols_deep = [c for c in base_cols_dp if c in df_table_deep.columns]
        col_cfg_deep = {
            "news_url": st.column_config.LinkColumn("Article URL", display_text="Open Link 🔗"),
            "domain": st.column_config.TextColumn("Media Domain"),
            "subtopic": st.column_config.TextColumn("Subtopic"),
            "news_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD")
        }
        if summary_col_dp:
            col_cfg_deep[summary_col_dp] = st.column_config.TextColumn("Article Summary (AI Summary)", width="large")
            
        st.dataframe(df_table_deep[cols_deep], column_config=col_cfg_deep, hide_index=True, use_container_width=True, height=340)
