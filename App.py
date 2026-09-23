import os
import time
import streamlit as st
import requests
import base64
from datetime import datetime, timedelta
from PIL import Image
import io

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

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
# GLOBAL STYLE & IOS APP ICON INJECTION (BASE64 EMBEDDED)
# ==============================================================================
def get_base64_image(image_path: str) -> str:
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""

icon_data_uri = get_base64_image("logo.png")

st.markdown(f"""
    <link rel="apple-touch-icon" href="{icon_data_uri}">
    <link rel="apple-touch-icon-precomposed" href="{icon_data_uri}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="RichforeverAI">

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

    .stApp {{
        background: radial-gradient(circle at 15% 0%, #1a1030 0%, #0b0c14 45%, #08090f 100%);
        color: #eef0f6;
    }}

    .rf-hero {{
        text-align: center;
        padding: 1.4rem 1rem 1.6rem 1rem;
        margin-bottom: 1.2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(255,51,51,0.14), rgba(122,60,255,0.14));
        border: 1px solid rgba(255,255,255,0.07);
    }}
    .rf-hero h1 {{
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0;
        background: linear-gradient(90deg, #ff5b5b, #ff9d5c 45%, #a06bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .rf-hero p {{
        margin: 0.35rem 0 0 0;
        color: #9a9fb5;
        font-size: 0.92rem;
        letter-spacing: 0.3px;
    }}

    h2, h3 {{ color: #f3f4fa !important; font-weight: 700 !important; }}

    .stButton>button {{
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
    }}
    .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(255, 59, 59, 0.35);
    }}

    .rf-card {{
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.9rem;
    }}
    .rf-card h4 {{
        margin: 0 0 0.4rem 0;
        font-size: 1rem;
        color: #ff9d5c;
    }}
    .rf-card p {{ margin: 0; color: #c4c8da; font-size: 0.92rem; line-height: 1.5; }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #12101c 0%, #0b0c14 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }}
    .rf-sidebar-brand {{
        text-align: center;
        padding: 0.6rem 0 1rem 0;
    }}
    .rf-sidebar-brand span {{
        font-weight: 800;
        font-size: 1.15rem;
        background: linear-gradient(90deg, #ff5b5b, #a06bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .rf-pill {{
        display: inline-block;
        width: 100%;
        text-align: center;
        padding: 0.45rem 0;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.4px;
        margin-bottom: 0.6rem;
    }}
    .rf-pill-online {{ background: rgba(46, 204, 113, 0.14); color: #4fe08a; border: 1px solid rgba(46,204,113,0.35); }}
    .rf-pill-offline {{ background: rgba(255, 71, 87, 0.14); color: #ff6b7a; border: 1px solid rgba(255,71,87,0.35); }}
    .rf-pill-active {{ background: rgba(46, 204, 113, 0.14); color: #4fe08a; border: 1px solid rgba(46,204,113,0.35); }}
    .rf-pill-paused {{ background: rgba(255, 183, 3, 0.14); color: #ffcf5c; border: 1px solid rgba(255,183,3,0.35); }}

    div[data-testid="stMetric"] {{
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 0.5rem 0.7rem;
        margin-bottom: 0.4rem;
    }}

    hr {{ border-color: rgba(255,255,255,0.08) !important; }}
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: #3a2a55; border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

openrouter_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))

def _pil_to_b64_png(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def load_and_optimize_image(uploaded_file):
    """Aggressively compresses images to 900x900 to ensure lightweight payloads."""
    img = Image.open(uploaded_file)
    img.thumbnail((900, 900))
    return img

# ==============================================================================
# ROBUST OPENROUTER VISION ENGINE WITH FALLBACKS
# ==============================================================================
def analyze_chart(images: list, prompt: str) -> str:
    if not openrouter_key:
        raise RuntimeError("OpenRouter API key not configured. Please set OPENROUTER_API_KEY in secrets.")
    if OpenAI is None:
        raise RuntimeError("openai package is not installed.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key,
    )

    content_parts = []
    for img in images:
        b64_data = _pil_to_b64_png(img)
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64_data}"
            }
        })
    content_parts.append({
        "type": "text",
        "text": prompt
    })

    # Updated fallback pool with active free vision routers and models
    models_pool = [
        "openrouter/free",
        "google/gemma-4-31b-it:free",
        "nex-agi/nex-n2.5-mini:free"
    ]

    last_err = None
    for model in models_pool:
        try:
            st.toast(f"Analyzing via OpenRouter ({model})...", icon="⚡")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": content_parts
                    }
                ],
                max_tokens=1200
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
        except Exception as e:
            last_err = e
            continue

    raise last_err or Exception("All OpenRouter vision endpoints failed.")

# ==============================================================================
# TELEMETRY HELPERS
# ==============================================================================
def get_bot_telemetry() -> dict:
    try:
        r = requests.get(
            f"{JSONBIN_URL}/latest",
            headers={"X-Master-Key": JSONBIN_MASTER_KEY, "Content-Type": "application/json"},
            timeout=5
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
    except Exception:
        pass
    return {"bot_active": True, "account_equity": 0.0, "account_balance": 0.0, "open_trades_count": 0, "pc_online": False}

def set_bot_status(status: bool):
    try:
        current = get_bot_telemetry()
        current["bot_active"] = status
        requests.put(JSONBIN_URL, json=current, headers={"X-Master-Key": JSONBIN_MASTER_KEY, "Content-Type": "application/json"}, timeout=5)
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
st.sidebar.caption("⚡ Low-Overhead Compressed OpenRouter Engine")
st.sidebar.markdown("**🤖 Live MT5 Telemetry**")

telemetry = get_bot_telemetry()
pc_online = telemetry.get("pc_online", False)
bot_active = telemetry.get("bot_active", True)
equity = telemetry.get("account_equity", 0.0)
balance = telemetry.get("account_balance", 0.0)
open_count = telemetry.get("open_trades_count", 0)

if not pc_online:
    st.sidebar.markdown("<div class='rf-pill rf-pill-offline'>PC STATUS: OFFLINE 💀</div>", unsafe_allow_html=True)
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
4. **Confidence Level**: Provide a setup confidence rating.
5. **Verdict**: Give a clean, zero-fluff directional bias and setup evaluation.
"""

# ==============================================================================
# PAGE 1: HOME / DASHBOARD
# ==============================================================================
if page == "Home / Dashboard":
    st.markdown("""
        <div class="rf-hero">
            <h1>⚡ RICHFOREVER AI</h1>
            <p>ICT Vision Confluence & Live MT5 Telemetry Hub (OpenRouter Powered)</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="rf-card">
            <h4>⚡ Low-Overhead Compression Active</h4>
            <p>Images are automatically optimized to 900x900 resolution to ensure lightweight payloads.</p>
        </div>
        <div class="rf-card">
            <h4>📸 Single-Shot Analysis</h4>
            <p>Recommended during high-traffic periods for instant, reliable ICT chart reads via OpenRouter.</p>
        </div>
    """, unsafe_allow_html=True)

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

    if not openrouter_key:
        st.error("⚠️ No OpenRouter API key configured. Please add OPENROUTER_API_KEY to your Streamlit secrets.")
        st.stop()

    uploaded_file = st.file_uploader("Upload chart screenshot...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = load_and_optimize_image(uploaded_file)
        st.image(image, caption="Optimized Chart Feed", use_container_width=True)
        user_query = st.text_input("Custom instructions:", value="Analyze this chart for FVG and setup viability.")

        if st.button("RUN PIXEL SCAN"):
            with st.spinner("Executing optimized scan..."):
                try:
                    result_text = analyze_chart(
                        images=[image],
                        prompt=f"{ICT_PROMPT}\n\nUser Question: {user_query}"
                    )
                    st.markdown("### 📊 Scan Report")
                    st.success("Scan complete")
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"⚠️ {e}")

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

    if not openrouter_key:
        st.error("⚠️ No OpenRouter API key configured. Please add OPENROUTER_API_KEY to your Streamlit secrets.")
        st.stop()

    uploaded_files = st.file_uploader("Upload multiple timeframe charts...", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 3))
        optimized_images = []
        for i, f in enumerate(uploaded_files):
            opt_img = load_and_optimize_image(f)
            optimized_images.append(opt_img)
            with cols[i % len(cols)]:
                st.image(opt_img, caption=f.name, use_container_width=True)

        if st.button("RUN MULTI-TF CONFLUENCE SCAN"):
            with st.spinner("Processing compressed multi-timeframe feed..."):
                try:
                    prompt = """
                    You are the RichforeverAI Vision Engine using exact ICT rules from the live execution bot.
                    Analyze the provided multi-timeframe charts (H1 macro, 15m equilibrium, 5m entry) using strict ICT rules.
                    
                    Format strictly like this:
                    - **Timeframe/Context**: [Multi-TF Alignment]
                    - **H1 Bias**: [Bullish / Bearish]
                    - **15m Equilibrium Zone**: [Discount / Premium]
                    - **5m FVG Status**: [Retracing to FVG / No Setup]
                    - **Confidence Level**: [High / Medium / Low]
                    - **Verdict**: [TAKE TRADE / WAIT / NO SETUP]
                    - **Target R:R**: [Must be >= 2.0R if TAKE TRADE, else N/A]
                    - **Quick Note**: [One sentence maximum reason]
                    """

                    result_text = analyze_chart(
                        images=optimized_images,
                        prompt=prompt
                    )
                    st.markdown("### 🌐 Confluence Report")
                    st.success("Multi-scan complete")
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"⚠️ {e}")
