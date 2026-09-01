import base64
import os
from PIL import Image, ImageDraw
import streamlit as st
from utils import load_custom_css, load_local_dataset, check_login, get_base64_image
from page_overview import render_overview_page
from page_alert import render_alert_page
from page_deepdive import render_deepdive_page
from page_admin import render_admin_page


# ==============================================================================
# 1. AUTO-GENERATE LOCAL PNG ICONS
# ==============================================================================
def create_sample_icons():
    os.makedirs("assets/icons", exist_ok=True)
    icon_color = (35, 126, 206, 255)       # HEX #237ece
    accent_color = (35, 126, 206, 255)     # HEX #237ece

    icons_def = [
        ("icon_sentiment.png", "clock"),
        ("icon_alert.png", "alert_doc"),
        ("icon_deepdive.png", "newspaper"),
        ("icon_admin.png", "settings"),
    ]

    for filename, itype in icons_def:
        path = os.path.join("assets/icons", filename)
        img = Image.new("RGBA", (80, 80), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        if itype == "clock":
            draw.ellipse([14, 18, 66, 70], outline=icon_color, width=4)
            draw.line([40, 44, 40, 28], fill=icon_color, width=4)
            draw.line([40, 44, 52, 44], fill=icon_color, width=4)
            draw.arc([8, 12, 28, 32], 120, 260, fill=icon_color, width=4)
            draw.arc([52, 12, 72, 32], 280, 60, fill=icon_color, width=4)
        elif itype == "alert_doc":
            draw.rounded_rectangle([16, 14, 64, 68], radius=6, outline=icon_color, width=4)
            draw.rounded_rectangle([28, 8, 52, 20], radius=4, outline=icon_color, width=3)
            draw.polygon([(40, 28), (30, 46), (50, 46)], outline=accent_color, width=3)
            draw.line([40, 36, 40, 40], fill=accent_color, width=3)
            draw.point([40, 43], fill=accent_color)
            draw.line([26, 54, 54, 54], fill=icon_color, width=3)
            draw.line([26, 60, 44, 60], fill=icon_color, width=3)
        elif itype == "newspaper":
            draw.rounded_rectangle([16, 16, 64, 68], radius=8, outline=icon_color, width=4)
            draw.ellipse([24, 24, 38, 38], outline=accent_color, width=3)
            draw.line([44, 28, 56, 28], fill=icon_color, width=3)
            draw.line([44, 36, 56, 36], fill=icon_color, width=3)
            draw.line([24, 48, 56, 48], fill=icon_color, width=3)
            draw.line([24, 56, 50, 56], fill=icon_color, width=3)
        elif itype == "settings":
            draw.ellipse([22, 22, 58, 58], outline=icon_color, width=4)
            draw.ellipse([34, 34, 46, 46], fill=accent_color)
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                draw.rectangle([36, 12, 44, 20], fill=icon_color)

        img.save(path, "PNG")


create_sample_icons()


# ==============================================================================
# 2. PAGE CONFIGURATION & LOGIN GUARD
# ==============================================================================
st.set_page_config(
    page_title="TKB NEWS SENTIMENT ANALYSIS",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_custom_css()
check_login()

if "active_page" not in st.session_state:
    st.session_state.active_page = "OVERVIEW"

df_raw, loaded_file_name = load_local_dataset()


# ==============================================================================
# 3. INJECT CSS MENU (ALIGN LEFT & CUSTOM HOVER)
# ==============================================================================
icon_overview_b64 = get_base64_image("assets/icons/icon_sentiment.png")
icon_alert_b64 = get_base64_image("assets/icons/icon_alert.png")
icon_deepdive_b64 = get_base64_image("assets/icons/icon_deepdive.png")
icon_admin_b64 = get_base64_image("assets/icons/icon_admin.png")

st.markdown(
    f"""
<style>
    /* Sidebar Base */
    [data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-right: 1px solid #edf2f7 !important;
    }}
    
    [data-testid="stSidebar"] .block-container {{
        padding-top: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* Menu Button Style: Align Left */
    [data-testid="stSidebar"] div.stButton > button {{
        width: 100% !important;
        min-height: 38px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        padding: 6px 12px !important;
        margin-bottom: 2px !important;
        border-radius: 6px !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        transition: all 0.15s ease-in-out !important;
    }}

    /* Menu Text Alignment */
    [data-testid="stSidebar"] div.stButton > button p,
    [data-testid="stSidebar"] div.stButton > button span {{
        margin: 0 !important;
        padding: 0 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        text-align: left !important;
        flex-grow: 1 !important;
        transition: color 0.15s ease-in-out !important;
    }}

    /* Hover State */
    [data-testid="stSidebar"] div.stButton > button:hover {{
        background-color: #f0f7ff !important;
    }}

    [data-testid="stSidebar"] div.stButton > button:hover p,
    [data-testid="stSidebar"] div.stButton > button:hover span {{
        color: #237ece !important;
        font-weight: 600 !important;
    }}

    /* Active State */
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
        background-color: #f0f7ff !important;
        border-left: 3px solid #237ece !important;
        border-radius: 0 6px 6px 0 !important;
    }}

    [data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] span {{
        color: #237ece !important;
        font-weight: 700 !important;
    }}

    /* Auto-Inject PNG Icons */
    div.st-key-btn_OVERVIEW button::before,
    div.st-key-btn_PEAK_ALERT button::before,
    div.st-key-btn_DEEP_DIVE button::before,
    div.st-key-btn_ADMIN_SETTINGS button::before {{
        content: "";
        display: inline-block;
        width: 18px;
        height: 18px;
        margin-right: 10px;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        flex-shrink: 0;
    }}

    div.st-key-btn_OVERVIEW button::before {{
        background-image: url('{icon_overview_b64}');
    }}
    div.st-key-btn_PEAK_ALERT button::before {{
        background-image: url('{icon_alert_b64}');
    }}
    div.st-key-btn_DEEP_DIVE button::before {{
        background-image: url('{icon_deepdive_b64}');
    }}
    div.st-key-btn_ADMIN_SETTINGS button::before {{
        background-image: url('{icon_admin_b64}');
    }}

    /* Tombol Logout */
    div.st-key-btn_logout button {{
        min-height: 32px !important;
        padding: 4px 10px !important;
        font-size: 0.8rem !important;
        justify-content: center !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        background-color: #ffffff !important;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# 4. SIDEBAR NAVIGATION MENU
# ==============================================================================
MENU_ITEMS = [
    {
        "id": "OVERVIEW",
        "title": "Sentiment Overview",
    },
    {
        "id": "PEAK_ALERT",
        "title": "Alert & Peak Spike",
    },
    {
        "id": "DEEP_DIVE",
        "title": "Topic Deep Dive",
    },
]

if st.session_state.get("user_role") == "admin":
    MENU_ITEMS.append({
        "id": "ADMIN_SETTINGS",
        "title": "Admin Settings",
    })

with st.sidebar:
    st.markdown(
        f"""
        <div style='margin-bottom: 10px; padding: 6px 10px; background:#f8fafc; border:1px solid #f1f5f9; border-radius:6px; display:flex; justify-content:space-between; align-items:center;'>
            <span style='color:#334155; font-size:0.8rem; font-weight:700;'>{st.session_state.get('username', 'User')}</span>
            <span style='font-size:0.65rem; background:#f0f7ff; color:#237ece; padding:1px 6px; border-radius:10px; font-weight:700;'>
                {st.session_state.get('user_role', 'VIEWER').upper()}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='font-size: 0.7rem; font-weight: 800; margin-bottom: 6px; margin-left: 4px; color:#94a3b8; letter-spacing:0.05em;'>DASHBOARD MENU</p>",
        unsafe_allow_html=True,
    )

    for item in MENU_ITEMS:
        is_active = st.session_state.active_page == item["id"]
        btn_type = "primary" if is_active else "secondary"

        if st.button(item["title"], key=f"btn_{item['id']}", type=btn_type, use_container_width=True):
            if st.session_state.active_page != item["id"]:
                st.session_state.active_page = item["id"]
                st.rerun()

    st.write("")
    if loaded_file_name:
        st.caption(f"📁 `{loaded_file_name}`")
    else:
        st.caption("💡 Sample Data")

    st.markdown("---")
    if st.button("🚪 Logout", key="btn_logout", use_container_width=True):
        # 1. Hapus state sesi
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.session_state.active_page = "OVERVIEW"
        
        # 2. Hapus parameter URL browser
        st.query_params.clear()
        
        st.rerun()


# ==============================================================================
# 5. ROUTER / PAGE RENDER LOGIC
# ==============================================================================
if st.session_state.active_page == "OVERVIEW":
    render_overview_page(df_raw)
elif st.session_state.active_page == "PEAK_ALERT":
    render_alert_page(df_raw)
elif st.session_state.active_page == "DEEP_DIVE":
    render_deepdive_page(df_raw)
elif st.session_state.active_page == "ADMIN_SETTINGS":
    render_admin_page(df_raw, loaded_file_name)


# ==============================================================================
# 6. FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    "<center style='color:#94a3b8; font-size:0.75rem; font-weight:600;'>TKB News Sentiment Analysis Dashboard © 2026</center>",
    unsafe_allow_html=True,
)
