import os
import streamlit as st
import requests
from datetime import datetime, timedelta
from google import genai
from PIL import Image

# ==============================================================================
# CONFIGURATION & JSONBIN BRIDGE SETUP
# ==============================================================================
JSONBIN_BIN_ID = "6aa51966ffd5d16053fd7e2f"
JSONBIN_MASTER_KEY = "$2a$10$V..urr.HG8zrlXI7byY/veOBjNWADGHWbJsfbEB3HfLmoaiGJ74xi"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

st.set_page_config(
    page_title="RichforeverAI",
    page_icon="⚡",
    layout="centered"
)

# Custom mobile-first CSS styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #ff3333 !important; text-align: center; }
    .stButton>button { width: 100%; background-color: #ff3333; color: white; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ RICHFOREVER AI")
st.markdown("<p style='text-align: center; color: #888;'>ICT Vision Confluence & Live MT5 Telemetry</p>", unsafe_allow_html=True)
st.markdown("---")

# Safe Gemini API key loader (Works locally or on Streamlit Cloud without crashing)
gemini_key = None
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    gemini_key = os.getenv("GEMINI_API_KEY", "")

if not gemini_key:
    st.error("⚠️ GEMINI_API_KEY not found. Please add it to your Streamlit secrets or set it as a local environment variable.")
    st.stop()

client = genai.Client(api_key=gemini_key)

# ==============================================================================
# REMOTE TELEMETRY & BOT CONTROL HELPERS
# ==============================================================================
def get_bot_telemetry() -> dict:
    try:
        r = requests.get(
            f"{JSONBIN_URL}/latest", 
            headers={
                "X-Master-Key": JSONBIN_MASTER_KEY,
                "Content-Type": "application/json"
            }, 
            timeout=3
        )
        if r.status_code == 200:
            record = r.json().get("record", {})
            
            # Check if the local PC script is actively sending heartbeats
            heartbeat_str = record.get("last_heartbeat")
            if heartbeat_str:
                try:
                    hb_time = datetime.strptime(heartbeat_str, '%Y-%m-%d %H:%M:%S')
                    # If heartbeat is older than 20 seconds, PC is offline
                    if datetime.utcnow() - hb_time > timedelta(seconds=20):
                        record["pc_online"] = False
                    else:
                        record["pc_online"] = True
                except Exception:
                    record["pc_online"] = False
            else:
                record["pc_online"] = False
                
            return record
    except Exception:
        pass
    return {
        "bot_active": True, 
        "account_equity": 0.0, 
        "account_balance": 0.0, 
        "open_trades_count": 0, 
        "pc_online": False
    }

def set_bot_status(status: bool):
    try:
        current = get_bot_telemetry()
        current["bot_active"] = status
        requests.put(
            JSONBIN_URL, 
            json=current, 
            headers={
                "X-Master-Key": JSONBIN_MASTER_KEY,
                "Content-Type": "application/json"
            }, 
            timeout=3
        )
    except Exception as e:
        st.error(f"Failed to update engine state: {e}")

def render_bot_control_widget():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Live MT5 Telemetry")
    
    telemetry = get_bot_telemetry()
    pc_online = telemetry.get("pc_online", False)
    bot_active = telemetry.get("bot_active", True)
    equity = telemetry.get("account_equity", 0.0)
    balance = telemetry.get("account_balance", 0.0)
    open_count = telemetry.get("open_trades_count", 0)
    
    # Display real-time connection status
    if not pc_online:
        st.sidebar.error("PC Status: OFFLINE 💀")
        st.sidebar.caption("Run `RichforeverAI_2.py` on your PC.")
    else:
        st.sidebar.success("PC Status: CONNECTED 🟢")
        st.sidebar.metric("Account Equity", f"${equity:,.2f}")
        st.sidebar.metric("Account Balance", f"${balance:,.2f}")
        st.sidebar.metric("Active Positions", open_count)
        
        if bot_active:
            st.sidebar.success("Engine State: ACTIVE 🟢")
            if st.sidebar.button("🔴 PAUSE ENGINE", use_container_width=True):
                set_bot_status(False)
                st.rerun()
        else:
            st.sidebar.warning("Engine State: PAUSED 🔴")
            if st.sidebar.button("🟢 RESUME ENGINE", use_container_width=True):
                set_bot_status(True)
                st.rerun()

# ==============================================================================
# SIDEBAR NAVIGATION & CONTROLS
# ==============================================================================
mode = st.sidebar.selectbox("Select Scanning Mode", ["Single-Shot Analysis", "Multi-Timeframe Confluence"])
render_bot_control_widget()

ICT_PROMPT = """
You are an expert ICT (Inner Circle Trader) mentor and price action analyst. 
Analyze the provided trading chart image(s) using ICT concepts:
1. **Market Structure**: Identify BOS, CHoCH, and trend direction.
2. **Liquidity**: Pinpoint external/internal range liquidity sweeps.
3. **Imbalances**: Locate Fair Value Gaps (FVG) or Order Blocks.
4. **Verdict**: Give a clean, zero-fluff directional bias and setup evaluation.
"""

# ==============================================================================
# SCANNER APP MODES
# ==============================================================================
if mode == "Single-Shot Analysis":
    st.subheader("📸 Single Chart Analysis")
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
                    st.markdown("### 📊 SCAN REPORT")
                    st.success("Scan Complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Analysis Error: {e}")

else:
    st.subheader("🔄 Multi-Timeframe Confluence")
    uploaded_files = st.file_uploader("Upload multiple timeframe charts...", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        for f in uploaded_files:
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
                    st.markdown("### 🌐 CONFLUENCE REPORT")
                    st.success("Multi-Scan Complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Confluence Error: {e}")
