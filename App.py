import streamlit as st
import requests
from google import genai
from google.genai import types
from PIL import Image

# ==============================================================================
# CONFIGURATION & JSONBIN BRIDGE SETUP
# ==============================================================================
JSONBIN_BIN_ID = "6aa51966ffd5d16053fd7e2f"
JSONBIN_MASTER_KEY = "$2a$10$Y3Fbf1v.CPDuR99om8LN6Oxw4ZScyw0dD7aAk0KdZaSRaComfQe4a."
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

# Initialize Gemini Client securely using st.secrets
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Error: GEMINI_API_KEY is missing from Streamlit Secrets.")
    st.stop()

# ==============================================================================
# REMOTE TELEMETRY & BOT CONTROL HELPERS
# ==============================================================================
def get_bot_telemetry() -> dict:
    try:
        r = requests.get(f"{JSONBIN_URL}/latest", headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3)
        if r.status_code == 200:
            return r.json().get("record", {})
    except Exception:
        pass
    return {"bot_active": True, "account_equity": 0.0, "account_balance": 0.0, "open_trades_count": 0, "open_trades": []}

def set_bot_status(status: bool):
    try:
        current = get_bot_telemetry()
        current["bot_active"] = status
        requests.put(JSONBIN_URL, json=current, headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3)
    except Exception as e:
        st.error(f"Failed to update engine state: {e}")

def render_bot_control_widget():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Live MT5 Telemetry")
    
    telemetry = get_bot_telemetry()
    bot_active = telemetry.get("bot_active", True)
    equity = telemetry.get("account_equity", 0.0)
    balance = telemetry.get("account_balance", 0.0)
    open_count = telemetry.get("open_trades_count", 0)
    
    # Telemetry metrics display
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
                        model='gemini-2.5-flash',
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
            with st.spinner("Correlating multi-timeframe structure..."):
                try:
                    content_payload = [ICT_PROMPT, "Analyze these charts for top-down confluence:"]
                    for f in uploaded_files:
                        content_payload.append(Image.open(f))
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=content_payload
                    )
                    st.markdown("### 🌐 CONFLUENCE REPORT")
                    st.success("Multi-Scan Complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Confluence Error: {e}")
