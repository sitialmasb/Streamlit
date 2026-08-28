import streamlit as st
import plotly.express as px
from utils import color_map_sentiment, apply_clean_white_layout

def render_deepdive_page(df_raw):
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
            selected_single_topic = st.selectbox("📌 Select Topic for In-Depth Analysis:", options=available_topics)
        with col_sel_tier:
            tier_list_deep = sorted(list(df_raw["new_tier"].dropna().astype(str).unique())) if "new_tier" in df_raw.columns else []
            selected_tier_deep = st.multiselect("Filter Media Tier", options=tier_list_deep, default=tier_list_deep)

        df_deep = df_raw[df_raw["issue_topic"] == selected_single_topic].copy()
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
                    <div class="pill-title">ISSUE NEWS VOLUME</div>
                    <div class="pill-value">{deep_total}</div>
                    <div class="pill-sub">Total Articles</div>
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

        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
            st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Sentiment Proportion: {selected_single_topic}</p>", unsafe_allow_html=True)
            if not df_deep.empty and "sentiment" in df_deep.columns:
                fig_deep_pie = px.pie(df_deep, names='sentiment', hole=0.5, color='sentiment', color_discrete_map=color_map_sentiment)
                fig_deep_pie.update_traces(textinfo='percent+value')
                fig_deep_pie = apply_clean_white_layout(fig_deep_pie, height=310)
                st.plotly_chart(fig_deep_pie, use_container_width=True)
            
        with col_g2:
            st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-bottom:6px; color:#1e293b;'>Media Tier Breakdown: {selected_single_topic}</p>", unsafe_allow_html=True)
            if not df_deep.empty and "new_tier" in df_deep.columns and "sentiment" in df_deep.columns:
                df_deep_tier = df_deep.groupby(['new_tier', 'sentiment']).size().reset_index(name='count')
                fig_deep_tier = px.bar(df_deep_tier, x='new_tier', y='count', color='sentiment', color_discrete_map=color_map_sentiment, barmode='stack', text='count')
                fig_deep_tier = apply_clean_white_layout(fig_deep_tier, height=310)
                fig_deep_tier.update_layout(xaxis_title="Media Tier", yaxis_title="Articles Count")
                st.plotly_chart(fig_deep_tier, use_container_width=True)

        st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-bottom:4px; color:#1e293b;'>Article List & AI Summary for Topic: '{selected_single_topic}'</p>", unsafe_allow_html=True)
        
        col_dt_title, col_dt_filter = st.columns([2, 1.2])
        with col_dt_filter:
            tbl_sent_choice_deep = st.selectbox(
                "Filter Sentiment for this Topic:",
                options=["All Sentiments", "Positive", "Neutral", "Negative"],
                index=0,
                key="tbl_sent_deep"
            )
        
        df_table_deep = df_deep.copy()
        if tbl_sent_choice_deep != "All Sentiments" and "sentiment" in df_table_deep.columns:
            df_table_deep = df_table_deep[df_table_deep["sentiment"] == tbl_sent_choice_deep]

        summary_col_dp = "gemini_summary" if "gemini_summary" in df_table_deep.columns else ("ai_summary" if "ai_summary" in df_table_deep.columns else None)
        base_cols_dp = ["news_date", "domain", "new_tier", "sentiment"]
        if summary_col_dp:
            base_cols_dp.append(summary_col_dp)
        if "news_url" in df_table_deep.columns:
            base_cols_dp.append("news_url")

        cols_deep = [c for c in base_cols_dp if c in df_table_deep.columns]
        col_cfg_deep = {
            "news_url": st.column_config.LinkColumn("Article URL", display_text="Open Link 🔗"),
            "domain": st.column_config.TextColumn("Media Domain"),
            "news_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD")
        }
        if summary_col_dp:
            col_cfg_deep[summary_col_dp] = st.column_config.TextColumn("Article Summary (AI Summary)", width="large")
            
        st.dataframe(df_table_deep[cols_deep], column_config=col_cfg_deep, hide_index=True, use_container_width=True, height=380)

    else:
        st.warning("Column `issue_topic` not found in the dataset.")


