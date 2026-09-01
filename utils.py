import os
import base64
import numpy as np
import pandas as pd
import streamlit as st

# Color Palette Mappings
color_map_sentiment = {
    "Positive": "#16a34a",
    "Neutral": "#237ece",
    "Negative": "#ea580c"
}

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    return ""

def standardize_sentiment_en(val):
    if pd.isna(val):
        return "Neutral"
    s = str(val).strip().lower()
    if any(k in s for k in ["pos", "baik", "positif"]):
        return "Positive"
    elif any(k in s for k in ["neg", "buruk", "negatif"]):
        return "Negative"
    return "Neutral"

def apply_clean_white_layout(fig, height=280):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", size=11, family="sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False)
    return fig

def generate_svg_bars(series, bar_color):
    """Menghasilkan SVG mini bar chart yang embed langsung di dalam kartu HTML."""
    if series is not None and not series.empty:
        vals = series.tail(10).values.tolist()
        if len(vals) < 10:
            vals = [0] * (10 - len(vals)) + vals
    else:
        vals = [2, 4, 3, 5, 2, 4, 6, 3, 5, 8]

    max_v = max(vals) if max(vals) > 0 else 1
    svg_height = 24
    bar_width = 6
    gap = 4
    
    rects = []
    for i, v in enumerate(vals):
        h = max(3, int((v / max_v) * svg_height))
        y = svg_height - h
        x = i * (bar_width + gap)
        rects.append(f'<rect x="{x}" y="{y}" width="{bar_width}" height="{h}" rx="2" fill="{bar_color}" />')
        
    total_w = 10 * (bar_width + gap) - gap
    return f'<svg width="{total_w}" height="{svg_height}" viewBox="0 0 {total_w} {svg_height}" style="display:block;">{"".join(rects)}</svg>'

def check_login():
    """Mempertahankan sesi login saat browser di-refresh via query params."""
    if not st.session_state.get("logged_in", False):
        user_param = st.query_params.get("user")
        role_param = st.query_params.get("role")
        
        if user_param and role_param:
            st.session_state.logged_in = True
            st.session_state.username = user_param
            st.session_state.user_role = role_param

    if not st.session_state.get("logged_in", False):
        st.markdown("""
            <div style="text-align:center; margin-top:50px; margin-bottom:20px;">
                <h2 style="color:#0f172a; font-weight:800; margin-bottom:4px;">TKB NEWS SENTIMENT ANALYSIS</h2>
                <span style="font-size:0.8rem; color:#64748b; font-weight:600;">Silakan login untuk mengakses dashboard</span>
            </div>
        """, unsafe_allow_html=True)
        
        _, col_login, _ = st.columns([1, 1.2, 1])
        with col_login:
            with st.form("login_form"):
                username_input = st.text_input("Username")
                password_input = st.text_input("Password", type="password")
                submit_btn = st.form_submit_button("Masuk ke Dashboard", use_container_width=True)

                if submit_btn:
                    if username_input == "admin" and password_input == "admin123":
                        st.session_state.logged_in = True
                        st.session_state.username = "Admin"
                        st.session_state.user_role = "admin"
                        st.query_params["user"] = "Admin"
                        st.query_params["role"] = "admin"
                        st.rerun()
                    elif username_input == "user" and password_input == "user123":
                        st.session_state.logged_in = True
                        st.session_state.username = "Viewer"
                        st.session_state.user_role = "viewer"
                        st.query_params["user"] = "Viewer"
                        st.query_params["role"] = "viewer"
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")
        st.stop()

@st.cache_data
def load_local_dataset():
    """Membaca file data lokal tanpa dependensi topic_issue."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidate_files = ["data.xlsx", "dataset.xlsx", "data.csv", "dataset.csv"]
    
    file_found = None
    for f in candidate_files:
        full_path = os.path.join(current_dir, f)
        if os.path.exists(full_path):
            file_found = full_path
            break
            
    if file_found:
        try:
            if file_found.endswith('.csv'):
                try:
                    df = pd.read_csv(file_found)
                except Exception:
                    df = pd.read_csv(file_found, sep=';')
            else:
                df = pd.read_excel(file_found)
            
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            if "sentiment" in df.columns:
                df["sentiment"] = df["sentiment"].apply(standardize_sentiment_en)
            if "news_date" in df.columns:
                df["news_date"] = pd.to_datetime(df["news_date"], errors="coerce")
                
            if "topic" in df.columns:
                df["topic"] = df["topic"].fillna("General").astype(str).str.strip()
            else:
                df["topic"] = "General"
                
            if "subtopic" in df.columns:
                df["subtopic"] = df["subtopic"].fillna("General").astype(str).str.strip()
            else:
                df["subtopic"] = "General"
                
            return df, os.path.basename(file_found)
        except Exception as e:
            st.error(f"Failed to read file {file_found}: {e}")
            
    # Dummy fallback data
    np.random.seed(42)
    topic_structure = {
        "Governance & Integrity": ["Anti-Corruption Compliance", "Leadership Ethics"],
        "Operational Quality": ["Supply Chain Continuity", "Infrastructure Maintenance"],
        "Customer & Service": ["Digital Platform Reliability", "Billing Inquiries"]
    }
    domains = ["kompas.com", "detik.com", "tempo.co", "bisnis.com"]
    dates = pd.date_range(end="2026-08-25", periods=60, freq="D")
    
    rows = []
    for i in range(80):
        t = np.random.choice(list(topic_structure.keys()))
        st_val = np.random.choice(topic_structure[t])
        rows.append({
            "news_url": f"https://{np.random.choice(domains)}/read/{1000+i}",
            "sentiment": np.random.choice(["Positive", "Neutral", "Negative"], p=[0.45, 0.35, 0.2]),
            "news_date": np.random.choice(dates),
            "topic": t,
            "subtopic": st_val,
            "domain": np.random.choice(domains),
            "new_tier": np.random.choice(["Tier 1", "Tier 2", "Tier 3"], p=[0.5, 0.3, 0.2]),
            "ai_summary": "AI Summary: Operational protocols audited and supply pipeline remains resilient."
        })
    return pd.DataFrame(rows), None

def analyze_negative_peak(df):
    if "news_date" not in df.columns or "sentiment" not in df.columns:
        return "N/A", 0, "No data", "No mitigation required."
    df_neg = df[df["sentiment"] == "Negative"].dropna(subset=["news_date"])
    if df_neg.empty:
        return "N/A", 0, "No negative incidents found.", "Normal operational status."
    
    peak_row = df_neg.groupby(df_neg["news_date"].dt.date).size().reset_index(name="count").sort_values(by="count", ascending=False).iloc[0]
    peak_date = str(peak_row["news_date"])
    peak_count = peak_row["count"]
    
    peak_df = df_neg[df_neg["news_date"].dt.date.astype(str) == peak_date]
    top_sub = peak_df["subtopic"].mode()[0] if "subtopic" in peak_df.columns and not peak_df["subtopic"].empty else "Operations"
    
    root_cause = f"Spike driven primarily by issues in '{top_sub}'."
    mitigation = "Activate standard crisis communication and clarify media releases across Tier 1 domains."
    return peak_date, peak_count, root_cause, mitigation
