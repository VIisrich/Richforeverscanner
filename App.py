import os
import streamlit as st
import requests
from datetime import datetime, timedelta
from google import genai
from PIL import Image

# ==============================================================================
# CONFIG & SECRETS
# ==============================================================================
JSONBIN_BIN_ID = "6aa51966ffd5d16053fd7e2f"
JSONBIN_MASTER_KEY = "$2a$10$V..urr.HG8zrlXI7byY/veOBjNWADGHWbJsfbEB3HfLmoaiGJ74xi"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

st.set_page_config(
    page_title="RichforeverAI",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# GLOBAL STYLE & IOS APP ICON INJECTION
# ==============================================================================
st.markdown("""
    <link rel="apple-touch-icon" href="logo.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="RichforeverAI">

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: radial-gradient(circle at 15% 0%, #1a1030 0%, #0b0c14 45%, #08090f 100%);
        color: #eef0f6;
    }

    /* Hero header */
    .rf-hero {
        text-align: center;
        padding: 1.4rem 1rem 1.6rem 1rem;
        margin-bottom: 1.2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(255,51,51,0.14), rgba(122,60,255,0.14));
        border: 1px solid rgba(255,255,255,0.07);
    }
    .rf-hero h1 {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0;
        background: linear-gradient(90deg, #ff5b5b, #ff9d5c 45%, #a06bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .rf-hero p {
        margin: 0.35rem 0 0 0;
        color: #9a9fb5;
        font-size: 0.92rem;
        letter-spacing: 0.3px;
    }

    /* Section headers inside pages */
    h2, h3 { color: #f3f4fa !important; font-weight: 700 !important; }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #ff3b3b, #ff6a3d);
        color: white;
        font-weight: 700;
        letter-spacing: 0.4px;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 0;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
        box-shadow: 0 4px 14px rgba(255, 59, 59, 0.25);
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(255, 59, 59, 0.35);
    }

    /* Cards */
    .rf-card {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.9rem;
    }
    .rf-card h4 {
        margin: 0 0 0.4rem 0;
        font-size: 1rem;
        color: #ff9d5c;
    }
    .rf-card p { margin: 0; color: #c4c8da; font-size: 0.92rem; line-height: 1.5; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12101c 0%, #0b0c14 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    .rf-sidebar-brand {
        text-align: center;
        padding: 0.6rem 0 1rem 0;
    }
    .rf-sidebar-brand span {
        font-weight: 800;
        font-size: 1.15rem;
        background: linear-gradient(90deg, #ff5b5b, #a06bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Status pill */
    .rf-pill {
        display: inline-block;
        width: 100%;
        text-align: center;
        padding: 0.45rem 0;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.4px;
        margin-bottom: 0.6rem;
    }
    .rf-pill-online { background: rgba(46, 204, 113, 0.14); color: #4fe08a; border: 1px solid rgba(46,204,113,0.35); }
    .rf-pill-offline { background: rgba(255, 71, 87, 0.14); color: #ff6b7a; border: 1px solid rgba(255,71,87,0.35); }
    .rf-pill-active { background: rgba(46, 204, 113, 0.14); color: #4fe08a; border: 1px solid rgba(46,204,113,0.35); }
    .rf-pill-paused { background: rgba(255, 183, 3, 0.14); color: #ffcf5c; border: 1px solid rgba(255,183,3,0.35); }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 0.5rem 0.7rem;
        margin-bottom: 0.4rem;
    }

    hr { border-color: rgba(255,255,255,0.08) !important; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #3a2a55; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

# ==============================================================================
# TELEMETRY HELPERS
# ==============================================================================
def get_bot_telemetry() -> dict:
    try:
        r = requests.get(
            f"{JSONBIN_URL}/latest",
            headers={"X-Master-Key": JSONBIN_MASTER_KEY, "Content-Type": "application/json"},
            timeout=8
        )
        if r.status_code == 200:
            record = r.json().get("record", {})
            heartbeat_str = record.get("last_heartbeat")
            if heartbeat_str:
                try:
                    hb_time = datetime.strptime(heartbeat_str, '%Y-%m-%d %H:%M:%S')
                    record["pc_online"] = (datetime.utcnow() - hb_time <= timedelta(seconds=20))
                except Exception:
                    record["pc_online"] = False
            else:
                record["pc_online"] = False
            return record
        else:
            st.sidebar.caption(f"⚠️ Telemetry fetch: HTTP {r.status_code}")
    except Exception as e:
        st.sidebar.caption(f"⚠️ Telemetry fetch failed: {e}")
    return {"bot_active": True, "account_equity": 0.0, "account_balance": 0.0, "open_trades_count": 0, "pc_online": False}

def set_bot_status(status: bool):
    try:
        current = get_bot_telemetry()
        current["bot_active"] = status
        requests.put(JSONBIN_URL, json=current, headers={"X-Master-Key": JSONBIN_MASTER_KEY, "Content-Type": "application/json"}, timeout=8)
    except Exception as e:
        st.error(f"Failed to update engine state: {e}")

# ==============================================================================
# SIDEBAR NAVIGATION & LIVE TELEMETRY
# ==============================================================================
st.sidebar.markdown("<div class='rf-sidebar-brand'>⚡ <span>RICHFOREVER AI</span></div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Home / Dashboard", "Single-Shot Analysis", "Multi-Timeframe Confluence"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🤖 Live MT5 Telemetry**")

telemetry = get_bot_telemetry()
pc_online = telemetry.get("pc_online", False)
bot_active = telemetry.get("bot_active", True)
equity = telemetry.get("account_equity", 0.0)
balance = telemetry.get("account_balance", 0.0)
open_count = telemetry.get("open_trades_count", 0)

if not pc_online:
    st.sidebar.markdown("<div class='rf-pill rf-pill-offline'>PC STATUS: OFFLINE 💀</div>", unsafe_allow_html=True)
    st.sidebar.caption("Run `RichforeverAI.py` on your PC to connect.")
else:
    st.sidebar.markdown("<div class='rf-pill rf-pill-online'>PC STATUS: CONNECTED 🟢</div>", unsafe_allow_html=True)
    c1, c2 = st.sidebar.columns(2)
    c1.metric("Equity", f"${equity:,.2f}")
    c2.metric("Balance", f"${balance:,.2f}")
    st.sidebar.metric("Active Positions", open_count)

    if bot_active:
        st.sidebar.markdown("<div class='rf-pill rf-pill-active'>ENGINE: ACTIVE 🟢</div>", unsafe_allow_html=True)
        if st.sidebar.button("🔴 PAUSE ENGINE", use_container_width=True):
            set_bot_status(False)
            st.rerun()
    else:
        st.sidebar.markdown("<div class='rf-pill rf-pill-paused'>ENGINE: PAUSED 🔴</div>", unsafe_allow_html=True)
        if st.sidebar.button("🟢 RESUME ENGINE", use_container_width=True):
            set_bot_status(True)
            st.rerun()

# ==============================================================================
# SHARED ICT ANALYSIS PROMPT
# ==============================================================================
ICT_PROMPT = """
You are an expert ICT (Inner Circle Trader) mentor and price action analyst.
Analyze the provided trading chart image using ICT concepts:
1. **Market Structure**: Identify BOS, CHoCH, and trend direction.
2. **Liquidity**: Pinpoint external/internal range liquidity sweeps.
3. **Imbalances**: Locate Fair Value Gaps (FVG) or Order Blocks.
4. **Confidence Level**: Provide a setup confidence rating (e.g., High, Medium, Low or percentage).
5. **Verdict**: Give a clean, zero-fluff directional bias and setup evaluation.
"""

# ==============================================================================
# PAGE 1: HOME / DASHBOARD
# ==============================================================================
if page == "Home / Dashboard":
    st.markdown("""
        <div class="rf-hero">
            <h1>⚡ RICHFOREVER AI</h1>
            <p>ICT Vision Confluence & Live MT5 Telemetry Hub</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="rf-card">
            <h4>📸 Single-Shot Analysis</h4>
            <p>Upload one chart screenshot for a fast ICT read: market structure, liquidity sweeps, FVGs, confidence level, and a directional bias verdict.</p>
        </div>
        <div class="rf-card">
            <h4>🔄 Multi-Timeframe Confluence</h4>
            <p>Blend a Higher Timeframe (H1) macro bias with a lower timeframe (5m) entry chart into one fused, zero-fluff verdict with a confidence rating.</p>
        </div>
    """, unsafe_allow_html=True)

    st.caption("Use the sidebar to switch modules or pause/resume the live MT5 engine.")

# ==============================================================================
# PAGE 2: SINGLE-SHOT ANALYSIS
# ==============================================================================
elif page == "Single-Shot Analysis":
    st.markdown("""
        <div class="rf-hero">
            <h1>📸 Single Chart Analysis</h1>
            <p>ICT Vision Confluence</p>
        </div>
    """, unsafe_allow_html=True)

    if not gemini_key:
        st.error("⚠️ GEMINI_API_KEY not found in secrets or environment.")
        st.stop()

    client = genai.Client(api_key=gemini_key)
    uploaded_file = st.file_uploader("Upload chart screenshot...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Active Chart Feed", use_container_width=True)
        user_query = st.text_input("Custom instructions:", value="Analyze this chart for FVG and setup viability.")

        if st.button("RUN PIXEL SCAN"):
            with st.spinner("Analyzing market structure..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[image, f"{ICT_PROMPT}\n\nUser Question: {user_query}"]
                    )
                    st.markdown("### 📊 Scan Report")
                    st.success("Scan complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Analysis error: {e}")

# ==============================================================================
# PAGE 3: MULTI-TIMEFRAME CONFLUENCE
# ==============================================================================
elif page == "Multi-Timeframe Confluence":
    st.markdown("""
        <div class="rf-hero">
            <h1>🔄 Multi-Timeframe Confluence</h1>
            <p>Multi-TF Fusion Scan</p>
        </div>
    """, unsafe_allow_html=True)

    if not gemini_key:
        st.error("⚠️ GEMINI_API_KEY not found in secrets or environment.")
        st.stop()

    client = genai.Client(api_key=gemini_key)
    uploaded_files = st.file_uploader("Upload multiple timeframe charts...", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 3))
        for i, f in enumerate(uploaded_files):
            with cols[i % len(cols)]:
                st.image(Image.open(f), caption=f.name, use_container_width=True)

        if st.button("RUN MULTI-TF CONFLUENCE SCAN"):
            with st.spinner("Blending multi-timeframe narrative..."):
                try:
                    prompt = """
                    You are the RichforeverAI Vision Engine using ICT concepts.
                    You are given multiple charts for the same asset across different timeframes (e.g., Higher Timeframe H1/15m macro bias combined with lower timeframe 5m entry).
                    Synthesize them together into a unified analysis. Keep your answer ultra-short and zero fluff.
                    Format your response strictly like this:
                    - **Timeframe/Context**: [Multi-TF H1 + 5m Fusion]
                    - **Bias**: [Bullish / Bearish]
                    - **Zone**: [Discount / Premium / FVG Level]
                    - **Confidence Level**: [High / Medium / Low or Percentage]
                    - **Verdict**: [TAKE TRADE / WAIT / NO SETUP]
                    - **Entry / SL / TP**: [Exact price levels if TAKE TRADE, else N/A]
                    - **Quick Note**: [One sentence maximum reason blending both timeframes]
                    """

                    content_payload = [prompt]
                    for f in uploaded_files:
                        content_payload.append(Image.open(f))

                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=content_payload
                    )
                    st.markdown("### 🌐 Confluence Report")
                    st.success("Multi-scan complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Confluence error: {e}")
