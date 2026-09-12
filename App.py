import os
import streamlit as st
import requests
import urllib3
from datetime import datetime, timedelta
from google import genai
from PIL import Image

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# CONFIGURATION & JSONBIN BRIDGE SETUP
# ==============================================================================
JSONBIN_BIN_ID = "6aa51966ffd5d16053fd7e2f"
JSONBIN_MASTER_KEY = "$2a$10$Y3Fbf1v.CPDuR99om8LN6Oxw4ZScyw0dD7aAk0KdZaSRaComfQe4a."
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

st.set_page_config(
    page_title="RichforeverAI",
    page_icon="logo.png",
    layout="centered"
)

# Custom mobile-first futuristic styling matching the sleek card aesthetic
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    h1, h2, h3 { color: #ff3333 !important; text-align: center; }
    
    /* Futuristic Card Container */
    .bot-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .bot-title {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #ffffff;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    
    .metric-container {
        background: #090d12;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid #21262d;
    }
    
    .stButton>button { 
        width: 100%; 
        background-color: #ff3333; 
        color: white; 
        font-weight: bold; 
        border-radius: 10px; 
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #e02b2b;
    }
    </style>
""", unsafe_allow_html=True)

# Safe Gemini API key loader
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
        r = requests.get(f"{JSONBIN_URL}/latest", headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3, verify=False)
        if r.status_code == 200:
            record = r.json().get("record", {})
            heartbeat_str = record.get("last_heartbeat")
            if heartbeat_str:
                try:
                    hb_time = datetime.strptime(heartbeat_str, '%Y-%m-%d %H:%M:%S')
                    if abs((datetime.now() - hb_time).total_seconds()) > 25:
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
        "open_trades": [],
        "pc_online": False
    }

def set_bot_status(status: bool):
    try:
        current = get_bot_telemetry()
        current["bot_active"] = status
        requests.put(JSONBIN_URL, json=current, headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3, verify=False)
    except Exception as e:
        st.error(f"Failed to update engine state: {e}")

# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.title("⚡ Navigation")
app_mode = st.sidebar.selectbox("Select Page", ["RichforeverScanner", "Richforever"])

ICT_PROMPT = """
You are an expert ICT (Inner Circle Trader) mentor and price action analyst. 
Analyze the provided trading chart image(s) using ICT concepts:
1. **Market Structure**: Identify BOS, CHoCH, and trend direction.
2. **Liquidity**: Pinpoint external/internal range liquidity sweeps.
3. **Imbalances**: Locate Fair Value Gaps (FVG) or Order Blocks.
4. **Verdict**: Give a clean, zero-fluff directional bias and setup evaluation.
"""

# ==============================================================================
# PAGE 1: RICHFOREVERSCANNER
# ==============================================================================
if app_mode == "RichforeverScanner":
    st.title("⚡ RICHFOREVER SCANNER")
    st.markdown("<p style='text-align: center; color: #888;'>ICT Vision Confluence & Pixel Scanner</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    scan_mode = st.selectbox("Scanning Mode", ["Single-Shot Analysis", "Multi-Timeframe Confluence"])

    if scan_mode == "Single-Shot Analysis":
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

# ==============================================================================
# PAGE 2: RICHFOREVER (Live Bot Telemetry Card UI)
# ==============================================================================
else:
    telemetry = get_bot_telemetry()
    pc_online = telemetry.get("pc_online", False)
    bot_active = telemetry.get("bot_active", True)
    equity = telemetry.get("account_equity", 0.0)
    balance = telemetry.get("account_balance", 0.0)
    open_count = telemetry.get("open_trades_count", 0)
    open_trades = telemetry.get("open_trades", [])

    st.markdown("""
        <div class="bot-card">
            <div style="font-size: 40px; margin-bottom: 5px;">⚡🤖</div>
            <div class="bot-title">RichforeverAI</div>
    """, unsafe_allow_html=True)

    if pc_online:
        st.markdown("<p style='color: #00ff66; font-size: 14px; font-weight: bold;'>● PC STATUS: CONNECTED</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #ff4444; font-size: 14px; font-weight: bold;'>● PC STATUS: OFFLINE</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="metric-container">
            <div style="display: flex; justify-content: space-between; color: #aaa; font-size: 13px;">
                <span>EQUITY: <b>${equity:,.2f}</b></span>
                <span>BALANCE: <b>${balance:,.2f}</b></span>
                <span>ACTIVE POS: <b>{open_count}</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if pc_online:
        if bot_active:
            if st.button("🔴 PAUSE EXECUTION ENGINE"):
                set_bot_status(False)
                st.rerun()
        else:
            if st.button("🟢 RESUME EXECUTION ENGINE"):
                set_bot_status(True)
                st.rerun()
    else:
        st.info("Start your local engine script on your PC to enable remote start/pause control buttons.")

    st.markdown("---")
    st.subheader("📋 Active Positions Monitor")
    if open_trades:
        for trade in open_trades:
            st.markdown(f"- **#{trade.get('ticket')}** | {trade.get('symbol')} ({trade.get('type')}) | P/L: **${trade.get('profit', 0.0):,.2f}**")
    else:
        st.caption("No active trades currently open.")
