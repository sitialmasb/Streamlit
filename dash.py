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

# Tambahan CSS khusus untuk sidebar menu custom agar mirip gambar referensi
st.sidebar.markdown("""
    <style>
        .custom-nav-btn {
            display: flex;
            align-items: center;
            width: 100%;
            padding: 10px 12px;
            margin-bottom: 8px;
            border-radius: 10px;
            background-color: transparent;
            border: 1px solid transparent;
            text-align: left;
            cursor: pointer;
            transition: background 0.2s;
            text-decoration: none !important;
        }
        .custom-nav-btn:hover {
            background-color: #f1f5f9;
        }
        .custom-nav-active {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            border-left: 4px solid #3b82f6 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Navigation Menu
with st.sidebar:
    st.markdown("<p style='font-size: 0.8rem; font-weight: 800; margin-bottom: 8px; color:#94a3b8; letter-spacing:0.05em;'>DASHBOARD MENU</p>", unsafe_allow_html=True)
    
    icon_overview = "https://raw.githubusercontent.com/sitialmasb/Streamlit/main/sentiment.png"
    icon_alert = "https://raw.githubusercontent.com/sitialmasb/Streamlit/main/alert.png"
    icon_deep = "https://raw.githubusercontent.com/sitialmasb/Streamlit/main/dive.png"
    
    # Data menu
    menus = [
        {"id": "OVERVIEW", "icon": icon_overview, "title": "Sentiment Overview", "subtitle": "Summary Dashboard"},
        {"id": "PEAK_ALERT", "icon": icon_alert, "title": "Crisis Alert & Peak", "subtitle": "Signal and Follow Up"},
        {"id": "DEEP_DIVE", "icon": icon_deep, "title": "Topic Deep Dive", "subtitle": "Explore Deep Insights"}
    ]

    for m in menus:
        is_active = st.session_state.active_page == m["id"]
        active_cls = "custom-nav-active" if is_active else ""
        
        # Membuat layout baris menggunakan kolom Streamlit
        col_ico, col_txt = st.columns([0.2, 0.8])
        with col_ico:
            st.image(m["icon"], width=22)
        with col_txt:
            # Menggunakan tombol asli Streamlit dengan teks bersih tanpa tag HTML
            if st.button(f"{m['title']}\n{m['subtitle']}", key=f"nav_{m['id']}", use_container_width=True):
                st.session_state.active_page = m["id"]
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
