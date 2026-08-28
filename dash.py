import streamlit as st
from utils import load_custom_css, load_local_dataset
from page_overview import render_overview_page
from page_alert import render_alert_page
from page_deepdive import render_deepdive_page

# 1. Page Configuration
st.set_page_config(
    page_title="TKB NEWS SENTIMENT ANALYSIS",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "OVERVIEW"

# Load Custom CSS Style
load_custom_css()

# Load Dataset
df_raw, loaded_file_name = load_local_dataset()

# 2. Sidebar Navigation Menu
with st.sidebar:
    st.markdown("<p style='font-size: 0.8rem; font-weight: 800; margin-bottom: 8px; color:#94a3b8; letter-spacing:0.05em;'>DASHBOARD MENU</p>", unsafe_allow_html=True)
    
    icon_overview = "https://raw.githubusercontent.com/sitialmasb/Streamlit/main/sentiment.png"
    icon_alert = "https://raw.githubusercontent.com/sitialmasb/Streamlit/main/alert.png"
    icon_deep = "https://raw.githubusercontent.com/sitialmasb/Streamlit/main/dive.png"
    
    # Menu 1: Sentiment Overview
    is_ov_active = st.session_state.active_page == "OVERVIEW"
    container_ov = st.container(border=True) if is_ov_active else st.container()
    with container_ov:
        col_icon_1, col_text_1 = st.columns([1, 4])
        with col_icon_1:
            st.image(icon_overview, width=24)
        with col_text_1:
            if st.button("Sentiment Overview\nOverview Dashboard", key="nav_overview", use_container_width=True):
                st.session_state.active_page = "OVERVIEW"
                st.rerun()

    # Menu 2: Alert & Peak Spike
    is_peak_active = st.session_state.active_page == "PEAK_ALERT"
    container_peak = st.container(border=True) if is_peak_active else st.container()
    with container_peak:
        col_icon_2, col_text_2 = st.columns([1, 4])
        with col_icon_2:
            st.image(icon_alert, width=24)
        with col_text_2:
            if st.button("Alert & Peak Spike\nAlert & Analysis", key="nav_peak", use_container_width=True):
                st.session_state.active_page = "PEAK_ALERT"
                st.rerun()

    # Menu 3: Topic Deep Dive
    is_deep_active = st.session_state.active_page == "DEEP_DIVE"
    container_deep = st.container(border=True) if is_deep_active else st.container()
    with container_deep:
        col_icon_3, col_text_3 = st.columns([1, 4])
        with col_icon_3:
            st.image(icon_deep, width=24)
        with col_text_3:
            if st.button("Topic Deep Dive\nIn-Depth Single Topic", key="nav_deep", use_container_width=True):
                st.session_state.active_page = "DEEP_DIVE"
                st.rerun()

    st.write("")
    if loaded_file_name:
        st.success(f" Connected: `{loaded_file_name}`")
    else:
        st.info("💡 Using built-in sample data.")

# 3. Router / Page Render Logic
if st.session_state.active_page == "OVERVIEW":
    render_overview_page(df_raw)
elif st.session_state.active_page == "PEAK_ALERT":
    render_alert_page(df_raw)
elif st.session_state.active_page == "DEEP_DIVE":
    render_deepdive_page(df_raw)

# 4. Footer
st.markdown("---")
st.markdown("<center style='color:#94a3b8; font-size:0.8rem; font-weight:600;'>TKB News Sentiment Analysis Dashboard © 2026</center>", unsafe_allow_html=True)
