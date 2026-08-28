import streamlit as st
import plotly.express as px
from utils import color_map_sentiment, apply_clean_white_layout

def render_overview_page(df_raw):
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 10px; border-radius: 12px; font-size: 1.3rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">📊</div>
            <div>
                <h2 style="margin: 0; font-size: 1.6rem; color: #0f172a; font-weight:800;">TKB NEWS <span style="color:#0284c7; font-style: italic;">OVERVIEW</span></h2>
                <span style="font-size: 0.8rem; letter-spacing: 0.1em; color: #64748b; font-weight: 700;">GENERAL SENTIMENT & MEDIA PERFORMANCE MONITORING</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if "overview_subtab" not in st.session_state:
        st.session_state.overview_subtab = "DISTRIBUTION"

    # In-page Filters
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sent_list = sorted(list(df_raw["sentiment"].dropna().unique())) if "sentiment" in df_raw.columns else []
        selected_sent = st.multiselect("Sentiment", options=sent_list, default=sent_list, key="ov_sent")
    with f2:
        tier_list = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
        selected_tier = st.multiselect("Media Tier", options=tier_list, default=tier_list, key="ov_tier")
    with f3:
        topic_list = sorted(list(df_raw["issue_topic"].dropna().astype(str).unique())) if "issue_topic" in df_raw.columns else []
        selected_topic = st.multiselect("Issue Topic", options=topic_list, default=topic_list, key="ov_topic")
    with f4:
        domain_list = sorted(list(df_raw["domain"].dropna().astype(str).unique())) if "domain" in df_raw.columns else []
        selected_domain = st.multiselect("Media Domain", options=domain_list, default=[], key="ov_domain")

    # Apply Filters
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
                <div class="pill-sub">ALL ARTICLES</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-green">
                <div class="pill-title">POSITIVE</div>
                <div class="pill-value">{pos_count}</div>
                <div class="pill-sub">{(pos_count/total_news*100) if total_news else 0:.1f}% OF TOTAL</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-blue">
                <div class="pill-title">NEUTRAL</div>
                <div class="pill-value">{neu_count}</div>
                <div class="pill-sub">{(neu_count/total_news*100) if total_news else 0:.1f}% OF TOTAL</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-orange">
                <div class="pill-title">NEGATIVE</div>
                <div class="pill-value">{neg_count}</div>
                <div class="pill-sub">{(neg_count/total_news*100) if total_news else 0:.1f}% ACTION REQUIRED</div>
            </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
            <div class="metric-pill-card card-soft-slate">
                <div class="pill-title">TOP TOPIC</div>
                <div class="pill-value" style="font-size:1.35rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{top_topic}">{top_topic}</div>
                <div class="pill-sub">LARGEST VOLUME</div>
            </div>
        """, unsafe_allow_html=True)

    # Segmented Capsule Rail Control
    st.markdown('<div class="capsule-rail-wrapper">', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        if st.button("📊 SENTIMENT DISTRIBUTION", key="pnav_dist", type="primary" if st.session_state.overview_subtab == "DISTRIBUTION" else "secondary", use_container_width=True):
            st.session_state.overview_subtab = "DISTRIBUTION"
            st.rerun()
    with p2:
        if st.button("📁 ISSUE TOPIC BREAKDOWN", key="pnav_topic", type="primary" if st.session_state.overview_subtab == "BREAKDOWN" else "secondary", use_container_width=True):
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
            st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Sentiment Share</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "sentiment" in df_filtered.columns:
                fig_pie = px.pie(df_filtered, names='sentiment', hole=0.55, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_pie.update_traces(textinfo='percent+value')
                fig_pie = apply_clean_white_layout(fig_pie, height=330)
                st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Sentiment by Media Tier</p>", unsafe_allow_html=True)
            if not df_filtered.empty and "new_tier" in df_filtered.columns and "sentiment" in df_filtered.columns:
                df_tier_sent = df_filtered.groupby(['new_tier', 'sentiment']).size().reset_index(name='count')
                fig_tier = px.bar(df_tier_sent, x='new_tier', y='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='group', text='count')
                fig_tier = apply_clean_white_layout(fig_tier, height=330)
                fig_tier.update_layout(xaxis_title="Media Tier", yaxis_title="Number of Articles")
                st.plotly_chart(fig_tier, use_container_width=True)

    elif st.session_state.overview_subtab == "BREAKDOWN":
        st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Sentiment Composition per Issue Topic</p>", unsafe_allow_html=True)
        if not df_filtered.empty and "issue_topic" in df_filtered.columns and "sentiment" in df_filtered.columns:
            df_top_sent = df_filtered.groupby(['issue_topic', 'sentiment']).size().reset_index(name='count')
            fig_top = px.bar(df_top_sent, y='issue_topic', x='count', color='sentiment', color_discrete_map=color_map_sentiment, orientation='h', barmode='stack')
            fig_top = apply_clean_white_layout(fig_top, height=400)
            fig_top.update_layout(yaxis_title="", xaxis_title="Number of Articles")
            st.plotly_chart(fig_top, use_container_width=True)

    elif st.session_state.overview_subtab == "FEED":
        st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:4px; color:#1e293b;'>Detailed News Feed & AI Summary</p>", unsafe_allow_html=True)
        
        col_search, col_t_filter = st.columns([2, 1.2])
        with col_search:
            search_keyword = st.text_input(
                "Cari berita (Judul/Domain/Ringkasan):", 
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
            for col in ["domain", "issue_topic", "gemini_summary", "ai_summary", "news_title", "title"]:
                if col in df_table_ov.columns:
                    mask = mask | df_table_ov[col].astype(str).str.lower().str.contains(keyword, na=False)
            df_table_ov = df_table_ov[mask]
            
        summary_col = "gemini_summary" if "gemini_summary" in df_table_ov.columns else ("ai_summary" if "ai_summary" in df_table_ov.columns else None)
        base_cols = ["news_date", "domain", "new_tier", "issue_topic", "sentiment"]
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
            "issue_topic": st.column_config.TextColumn("Issue Topic"),
            "new_tier": st.column_config.TextColumn("Tier")
        }
        if summary_col:
            col_config[summary_col] = st.column_config.TextColumn("Article Summary (AI Summary)", width="large")
            
        st.dataframe(df_table_ov[cols], column_config=col_config, hide_index=True, use_container_width=True, height=450)
