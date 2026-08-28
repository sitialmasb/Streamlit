import streamlit as st
import plotly.graph_objects as go
from utils import analyze_negative_peak, apply_clean_white_layout

def render_alert_page(df_raw):
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
                        {peak_data['peak_count']} Negative Articles
                    </span>
                </div>
                <div style="font-size:0.92rem; color:#334155; line-height: 1.6;">
                    The highest spike in negative sentiment was detected on <b>{peak_data['peak_date']}</b>. 
                    The primary contributing factor is dominated by the topic <b><mark style="background:#fef3c7; color:#92400e; padding:2px 6px; border-radius:4px; font-weight:700;">{peak_data['cause_topic']}</mark></b>.
                </div>
            </div>
        """, unsafe_allow_html=True)

        pk1, pk2, pk3 = st.columns(3)
        with pk1:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-white">
                    <div class="pill-title">PEAK DATE</div>
                    <div class="pill-value" style="font-size:1.5rem; color:#0f172a;">{peak_data['peak_date']}</div>
                    <div class="pill-sub">Highest Crisis Point</div>
                </div>
            """, unsafe_allow_html=True)
        with pk2:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-orange">
                    <div class="pill-title">TOTAL NEGATIVE NEWS</div>
                    <div class="pill-value">{peak_data['peak_count']}</div>
                    <div class="pill-sub">Daily Spike Volume</div>
                </div>
            """, unsafe_allow_html=True)
        with pk3:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-slate">
                    <div class="pill-title">ROOT CAUSE (TOPIC)</div>
                    <div class="pill-value" style="font-size:1.5rem; color:#0f172a;">{peak_data['cause_topic']}</div>
                    <div class="pill-sub">Main Triggering Factor</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<p style='font-weight:700; font-size:1rem; margin-top:14px; margin-bottom:6px; color:#1e293b;'>Negative Sentiment Timeline & Spike Anomaly</p>", unsafe_allow_html=True)
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
        fig_trend.update_layout(xaxis_title="News Date", yaxis_title="Negative Article Count")
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown(f"<p style='font-weight:700; font-size:1rem; margin-top:14px; margin-bottom:6px; color:#1e293b;'>Triggering Articles on Peak Date ({peak_data['peak_date']})</p>", unsafe_allow_html=True)
        
        # --- TAMBAHAN SEARCH BAR DI SINI ---
        col_search_pk, col_dummy_pk = st.columns([2, 1.2])
        with col_search_pk:
            search_keyword_peak = st.text_input(
                "Cari berita puncaknya (Domain/Topik/Ringkasan):", 
                placeholder="Ketik kata kunci...", 
                key="search_peak_articles"
            )

        df_table_peak = peak_data["peak_articles"].copy()
        if search_keyword_peak:
            keyword = search_keyword_peak.lower()
            mask = False
            for col in ["domain", "issue_topic", "gemini_summary", "ai_summary", "news_title", "title"]:
                if col in df_table_peak.columns:
                    mask = mask | df_table_peak[col].astype(str).str.lower().str.contains(keyword, na=False)
            df_table_peak = df_table_peak[mask]
        # ------------------------------------

        summary_col_pk = "gemini_summary" if "gemini_summary" in df_table_peak.columns else ("ai_summary" if "ai_summary" in df_table_peak.columns else None)
        base_cols_pk = ["domain", "new_tier", "issue_topic"]
        if summary_col_pk:
            base_cols_pk.append(summary_col_pk)
        if "news_url" in df_table_peak.columns:
            base_cols_pk.append("news_url")
            
        cols_peak = [c for c in base_cols_pk if c in df_table_peak.columns]
        col_cfg_peak = {
            "news_url": st.column_config.LinkColumn("Article URL", display_text="Open Link 🔗"),
            "domain": st.column_config.TextColumn("Media Portal"),
            "issue_topic": st.column_config.TextColumn("Issue Topic"),
            "new_tier": st.column_config.TextColumn("Tier")
        }
        if summary_col_pk:
            col_cfg_peak[summary_col_pk] = st.column_config.TextColumn("Issue Summary (AI Summary)", width="large")
            
        st.dataframe(df_table_peak[cols_peak], column_config=col_cfg_peak, hide_index=True, use_container_width=True, height=360)

    else:
        st.info("No negative sentiment data or valid dates available.")
