import streamlit as st
import pandas as pd
import os
from utils import standardize_sentiment_en, get_base64_image

def render_admin_page(df_raw, loaded_file_name):
    if st.session_state.get("user_role") != "admin":
        st.error("⛔ Akses Ditolak: Anda tidak memiliki izin untuk melihat halaman ini.")
        st.stop()

    icon_admin_b64 = get_base64_image("assets/icons/icon_admin.png")

    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <div style="background: #f0f7ff; border: 1px solid #237ece; padding: 6px; border-radius: 8px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                <img src="{icon_admin_b64}" width="20" height="20" style="object-fit: contain;" />
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.3rem; color: #0f172a; font-weight:800;">ADMIN <span style="color:#237ece; font-style: italic;">SETTINGS</span></h2>
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; color: #64748b; font-weight: 700;">SYSTEM CONFIGURATION & DATASET MANAGEMENT</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab_data, tab_ai, tab_system = st.tabs(["📁 Dataset Manager", "🤖 AI & Model Settings", "📊 System Info"])

    with tab_data:
        st.markdown("<p style='font-weight:700; font-size:0.95rem; margin-top:8px; color:#1e293b;'>Unggah Dataset Baru</p>", unsafe_allow_html=True)
        st.write("Unggah file Excel (`.xlsx`) atau CSV (`.csv`) baru untuk menggantikan data aktif.")

        uploaded_file = st.file_uploader("Pilih file dataset", type=["csv", "xlsx"])

        if uploaded_file is not None:
            col_u1, _ = st.columns([1, 4])
            with col_u1:
                save_btn = st.button("💾 Simpan Dataset", type="primary", use_container_width=True)

            if save_btn:
                save_path = uploaded_file.name
                try:
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.cache_data.clear()
                    st.success(f"File `{uploaded_file.name}` berhasil disimpan.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan file: {e}")

        st.markdown("---")
        st.markdown("<p style='font-weight:700; font-size:0.95rem; color:#1e293b;'>Pratinjau Dataset Aktif</p>", unsafe_allow_html=True)
        st.info(f"File aktif saat ini: **`{loaded_file_name if loaded_file_name else 'Sample Built-in Dummy'}`** | Total baris: **{len(df_raw)}**")
        st.dataframe(df_raw.head(10), use_container_width=True, height=240)

    with tab_ai:
        st.markdown("<p style='font-weight:700; font-size:0.95rem; margin-top:8px; color:#1e293b;'>Pengaturan OpenRouter / Gemini API</p>", unsafe_allow_html=True)
        
        current_api_key = st.session_state.get("custom_api_key", "")
        api_input = st.text_input("OpenRouter / Gemini API Key", value=current_api_key, type="password", placeholder="sk-or-v1-...")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            model_selected = st.selectbox(
                "Pilih Default LLM Model:",
                options=["microsoft/phi-4", "google/gemini-2.0-flash-exp", "anthropic/claude-3.5-haiku", "openai/gpt-4o-mini"],
                index=0
            )
        with col_m2:
            temp_val = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.2, step=0.05)

        if st.button("Simpan Konfigurasi AI", type="primary"):
            st.session_state["custom_api_key"] = api_input
            st.session_state["ai_model"] = model_selected
            st.session_state["ai_temp"] = temp_val
            st.success("Konfigurasi AI berhasil diperbarui!")

    with tab_system:
        st.markdown("<p style='font-weight:700; font-size:0.95rem; margin-top:8px; color:#1e293b;'>Informasi Session & Pengguna</p>", unsafe_allow_html=True)
        
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-white">
                    <div class="pill-title">CURRENT USER</div>
                    <div class="pill-value" style="font-size:1.15rem;">{st.session_state.get('username', '-')}</div>
                    <div class="pill-sub">Logged In Account</div>
                </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-blue">
                    <div class="pill-title">USER ROLE</div>
                    <div class="pill-value" style="font-size:1.15rem;">{st.session_state.get('user_role', '-').upper()}</div>
                    <div class="pill-sub">Access Privilege</div>
                </div>
            """, unsafe_allow_html=True)
        with s3:
            st.markdown(f"""
                <div class="metric-pill-card card-soft-slate">
                    <div class="pill-title">TOTAL DATASET ROWS</div>
                    <div class="pill-value" style="font-size:1.15rem;">{len(df_raw)}</div>
                    <div class="pill-sub">Records in Memory</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<p style='font-weight:700; font-size:0.9rem; color:#b91c1c;'>⚠️ Danger Zone</p>", unsafe_allow_html=True)
        if st.button("🧹 Bersihkan Cache Dataset & Reload", type="secondary"):
            st.cache_data.clear()
            st.success("Cache berhasil dibersihkan.")
            st.rerun()
