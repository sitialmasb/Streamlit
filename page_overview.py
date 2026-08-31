import streamlit as st
import plotly.express as px
import pandas as pd
from utils import color_map_sentiment, apply_clean_white_layout, get_base64_image, analyze_negative_peak

def render_overview_page(df_raw):
    icon_overview_b64 = get_base64_image("assets/icons/icon_sentiment.png")
    
    # -------------------------------------------------------------
    # 1. HEADER HALAMAN
    # -------------------------------------------------------------
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <div style="background: #f0f7ff; border: 1px solid #237ece; padding: 6px; border-radius: 8px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                <img src="{icon_overview_b64}" width="20" height="20" style="object-fit: contain;" />
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.3rem; color: #0f172a; font-weight:800;">SENTIMENT <span style="color:#237ece; font-style: italic;">OVERVIEW</span></h2>
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; color: #64748b; font-weight: 700;">OVERVIEW DASHBOARD & MEDIA SENTIMENT METRICS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "overview_subtab" not in st.session_state:
        st.session_state.overview_subtab = "DISTRIBUTION"

    # -------------------------------------------------------------
    # 2. FILTERING (DATE RANGE & METADATA)
    # -------------------------------------------------------------
    min_date = df_raw["news_date"].min().date() if "news_date" in df_raw.columns and not df_raw["news_date"].dropna().empty else None
    max_date = df_raw["news_date"].max().date() if "news_date" in df_raw.columns and not df_raw["news_date"].dropna().empty else None

    f_date, f1, f2, f3, f4, f5 = st.columns([1.3, 1, 1, 1.2, 1.2, 1.1])
    
    with f_date:
        if min_date and max_date:
            selected_date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="ov_date_range"
            )
        else:
            selected_date_range = None
            st.caption("No valid dates found")

    with f1:
        sent_list = sorted(list(df_raw["sentiment"].dropna().unique())) if "sentiment" in df_raw.columns else []
        selected_sent = st.multiselect("Sentiment", options=sent_list, default=[], key="ov_sent")
    with f2:
        tier_list = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
        selected_tier = st.multiselect("Media Tier", options=tier_list, default=[], key="ov_tier")
    with f3:
        topic_list = sorted(list(df_raw["topic"].dropna().astype(str).unique())) if "topic" in df_raw.columns else []
        selected_topic = st.multiselect("Topic", options=topic_list, default=[], key="ov_topic")
    with f4:
        if selected_topic and "topic" in df_raw.columns:
            subtopic_pool = df_raw[df_raw["topic"].isin(selected_topic)]
        else:
            subtopic_pool = df_raw
        subtopic_list = sorted(list(subtopic_pool["subtopic"].dropna().astype(str).unique())) if "subtopic" in subtopic_pool.columns else []
        selected_subtopic = st.multiselect("Subtopic", options=subtopic_list, default=[], key="ov_subtopic")
    with f5:
        domain_list = sorted(list(df_raw["domain"].dropna().astype(str).unique())) if "domain" in df_raw.columns else []
        selected_domain = st.multiselect("Media Domain", options=domain_list, default=[], key="ov_domain")

    # Menerapkan Filter
    df_filtered = df_raw.copy()

    if selected_date_range and isinstance(selected_date_range, tuple) and "news_date" in df_filtered.columns:
        if len(selected_date_range) == 2:
            start_d, end_d = selected_date_range
            df_filtered = df_filtered[
                (df_filtered["news_date"].dt.date >= start_d) & 
                (df_filtered["news_date"].dt.date <= end_d)
            ]
        elif len(selected_date_range) == 1:
            start_d = selected_date_range[0]
            df_filtered = df_filtered[df_filtered["news_date"].dt.date == start_d]

    if selected_sent and "sentiment" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["sentiment"].isin(selected_sent)]
    if selected_tier and "new_tier" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["new_tier"].astype(str).isin(selected_tier)]
    if selected_topic and "topic" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["topic"].astype(str).isin(selected_topic)]
    if selected_subtopic and "subtopic" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["subtopic"].astype(str).isin(selected_subtopic)]
    if selected_domain and "domain" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["domain"].astype(str).isin(selected_domain)]

    # -------------------------------------------------------------
    # 3. METRIK UTAMA (2 BARIS x 3 KOLOM)
    # -------------------------------------------------------------
    total_news = len(df_filtered)
    pos_count = len(df_filtered[df_filtered["sentiment"] == "Positive"]) if "sentiment" in df_filtered.columns else 0
    neu_count = len(df_filtered[df_filtered["sentiment"] == "Neutral"]) if "sentiment" in df_filtered.columns else 0
    neg_count = len(df_filtered[df_filtered["sentiment"] == "Negative"]) if "sentiment" in df_filtered.columns else 0
    top_topic = df_filtered["topic"].mode()[0] if not df_filtered.empty and "topic" in df_filtered.columns else "-"
    
    peak_data_ov = analyze_negative_peak(df_filtered)
    peak_date_str = peak_data_ov["peak_date"] if peak_data_ov else "-"
    peak_val_str = f"{peak_data_ov['peak_count']} News" if peak_data_ov and peak_data_ov['peak_count'] > 0 else "0 News"
    peak_cause_str = f"{peak_data_ov['cause_topic']}" if peak_data_ov and peak_data_ov['peak_count'] > 0 else "NORMAL"

    # BARIS 1: TOTAL NEWS, TOP TOPIC, PEAK SPIKE
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-white">
                <div class="pill-title">TOTAL NEWS</div>
                <div class="pill-value">{total_news}</div>
                <div class="pill-sub">ALL ARTICLES IN PERIOD</div>
            </div>
        """, unsafe_allow_html=True)
    with r1_c2:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-slate">
                <div class="pill-title">TOP TOPIC</div>
                <div class="pill-value" style="font-size:1.2rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{top_topic}">{top_topic}</div>
                <div class="pill-sub">LARGEST SHARE VOLUME</div>
            </div>
        """, unsafe_allow_html=True)
    with r1_c3:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-orange">
                <div class="pill-title">🚨 PEAK SPIKE DATE</div>
                <div class="pill-value" style="font-size:1.2rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{peak_date_str}">{peak_val_str}</div>
                <div class="pill-sub" style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{peak_cause_str}">{peak_date_str} ({peak_cause_str})</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")  # Spacing antar baris metrik

    # BARIS 2: POSITIVE, NEUTRAL, NEGATIVE
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    with r2_c1:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-green">
                <div class="pill-title">POSITIVE</div>
                <div class="pill-value">{pos_count}</div>
                <div class="pill-sub">{(pos_count/total_news*100) if total_news else 0:.1f}% OF TOTAL ARTICLES</div>
            </div>
        """, unsafe_allow_html=True)
    with r2_c2:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-blue">
                <div class="pill-title">NEUTRAL</div>
                <div class="pill-value">{neu_count}</div>
                <div class="pill-sub">{(neu_count/total_news*100) if total_news else 0:.1f}% OF TOTAL ARTICLES</div>
            </div>
        """, unsafe_allow_html=True)
    with r2_c3:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-orange">
                <div class="pill-title">NEGATIVE</div>
                <div class="pill-value">{neg_count}</div>
                <div class="pill-sub">{(neg_count/total_news*100) if total_news else 0:.1f}% MITIGATION REQUIRED</div>
            </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 4. SUB-TAB KONTEN (DISTRIBUSI / BREAKDOWN / FEED)
    # -------------------------------------------------------------
    st.markdown('<div class="capsule-rail-wrapper">', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        if st.button("📊 SENTIMENT DISTRIBUTION", key="pnav_dist", type="primary" if st.session_state.overview_subtab == "DISTRIBUTION" else "secondary", use_container_width=True):
            st.session_state.overview_subtab = "DISTRIBUTION"
            st.rerun()
    with p2:
        if st.button("📁 TOPIC & SUBTOPIC BREAKDOWN", key="pnav_topic", type="primary" if st.session_state.overview_subtab == "BREAKDOWN" else "secondary", use_container_width=True):
            st.session_state.overview_subtab = "BREAKDOWN"
            st.rerun()
    with p3:
        if st.button("📰 AI NEWS FEED", key="pnav_feed", type="primary" if st.session_state.overview_subtab == "FEED" else "secondary", use_container_width=True):
            st.session_state.overview_subtab = "FEED"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.overview_subtab == "DISTRIBUTION":
        c1, c2 = st.columns([1, 1.4])
        with c1:
            st.markdown("<p style='font-weight:700; font-size:0.88rem; margin-bottom:4px; color:#1e293b;'>Sentiment Share</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "sentiment" in df_filtered.columns:
                fig_pie = px.pie(df_filtered, names='sentiment', hole=0.55, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_pie.update_traces(textinfo='percent+value')
                fig_pie = apply_clean_white_layout(fig_pie, height=280)
                st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.markdown("<p style='font-weight:700; font-size:0.88rem; margin-bottom:4px; color:#1e293b;'>Sentiment by Media Tier</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "new_tier" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_tier_sent = df_filtered.groupby(['new_tier', 'sentiment']).size().reset_index(name='count')
                fig_tier = px.bar(df_tier_sent, x='new_tier', y='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='group', text='count')
                fig_tier = apply_clean_white_layout(fig_tier, height=280)
                fig_tier.update_layout(xaxis_title="Media Tier", yaxis_title="Number of Articles")
                st.plotly_chart(fig_tier, use_container_width=True)

    elif st.session_state.overview_subtab == "BREAKDOWN":
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("<p style='font-weight:700; font-size:0.88rem; margin-bottom:4px; color:#1e293b;'>Sentiment by Main Topic</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "topic" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_top_sent = df_filtered.groupby(['topic', 'sentiment']).size().reset_index(name='count')
                fig_top = px.bar(df_top_sent, y='topic', x='count', color='sentiment', color_discrete_map=color_map_sentiment, orientation='h', barmode='stack')
                fig_top = apply_clean_white_layout(fig_top, height=320)
                fig_top.update_layout(yaxis_title="", xaxis_title="Articles Count")
                st.plotly_chart(fig_top, use_container_width=True)
        with g2:
            st.markdown("<p style='font-weight:700; font-size:0.88rem; margin-bottom:4px; color:#1e293b;'>Sentiment by Subtopic</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "subtopic" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_sub_sent = df_filtered.groupby(['subtopic', 'sentiment']).size().reset_index(name='count')
                fig_sub = px.bar(df_sub_sent, y='subtopic', x='count', color='sentiment', color_discrete_map=color_map_sentiment, orientation='h', barmode='stack')
                fig_sub = apply_clean_white_layout(fig_sub, height=320)
                fig_sub.update_layout(yaxis_title="", xaxis_title="Articles Count")
                st.plotly_chart(fig_sub, use_container_width=True)

    elif st.session_state.overview_subtab == "FEED":
        st.markdown("<p style='font-weight:700; font-size:0.88rem; margin-bottom:4px; color:#1e293b;'>Detailed News Feed & AI Summary</p>", unsafe_allow_html=True)
        
        col_search, col_t_filter = st.columns([2, 1.2])
        with col_search:
            search_keyword = st.text_input(
                "Cari berita (Judul/Domain/Topic/Subtopic/Ringkasan):", 
                placeholder="Ketik kata kunci...", 
                key="search_news_feed"
            )
        with col_t_filter:
            tbl_sent_choice = st.selectbox(
                "Filter Article Sentiment:",
                options=["All Sentiments", "Positive", "Neutral", "Negative"],
                index=0,
                key="tbl_sent_ov"
            )
        
        df_table_ov = df_filtered.copy()
        if tbl_sent_choice != "All Sentiments" and "sentiment" in df_table_ov.columns:
            df_table_ov = df_table_ov[df_table_ov["sentiment"] == tbl_sent_choice]
            
        if search_keyword:
            keyword = search_keyword.lower()
            mask = False
            for col in ["domain", "topic", "subtopic", "gemini_summary", "ai_summary", "news_title", "title"]:
                if col in df_table_ov.columns:
                    mask = mask | df_table_ov[col].astype(str).str.lower().str.contains(keyword, na=False)
            df_table_ov = df_table_ov[mask]
            
        summary_col = "gemini_summary" if "gemini_summary" in df_table_ov.columns else ("ai_summary" if "ai_summary" in df_table_ov.columns else None)
        base_cols = ["news_date", "domain", "new_tier", "topic", "subtopic", "sentiment"]
        if summary_col:
            base_cols.append(summary_col)
        if "news_url" in df_table_ov.columns:
            base_cols.append("news_url")
            
        cols = [c for c in base_cols if c in df_table_ov.columns]
        col_config = {
            "news_url": st.column_config.LinkColumn("Article URL", display_text="Open Link 🔗"),
            "domain": st.column_config.TextColumn("Media Domain"),
            "news_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "sentiment": st.column_config.TextColumn("Sentiment"),
            "topic": st.column_config.TextColumn("Topic"),
            "subtopic": st.column_config.TextColumn("Subtopic"),
            "new_tier": st.column_config.TextColumn("Tier")
        }
        if summary_col:
            col_config[summary_col] = st.column_config.TextColumn("Article Summary (AI Summary)", width="large")
            
        st.dataframe(df_table_ov[cols], column_config=col_config, hide_index=True, use_container_width=True, height=380)
