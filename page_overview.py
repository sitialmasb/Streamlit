elif st.session_state.overview_subtab == "FEED":
        st.markdown("<p style='font-weight:700; font-size:1rem; margin-bottom:4px; color:#1e293b;'>Detailed News Feed & AI Summary</p>", unsafe_allow_html=True)
        
        # Kolom Filter: Search Bar & Sentiment Filter
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
        
        # Filter berdasarkan Sentiment
        if tbl_sent_choice != "All Sentiments" and "sentiment" in df_table_ov.columns:
            df_table_ov = df_table_ov[df_table_ov["sentiment"] == tbl_sent_choice]
            
        # Filter berdasarkan Search Bar (Mencari di berbagai kolom teks yang tersedia)
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
