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
    page_icon="📈",
    layout="centered"
)

st.title("📈 RichforeverAI Scanner")
st.markdown("### ICT Multi-Timeframe Confluence & Chart Analyzer")

# Initialize Gemini Client securely using st.secrets
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Error: GEMINI_API_KEY is missing from Streamlit Secrets. Please check your cloud settings.")
    st.stop()

# ==============================================================================
# REMOTE BOT CONTROL HELPERS
# ==============================================================================
def get_bot_status() -> bool:
    try:
        r = requests.get(f"{JSONBIN_URL}/latest", headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3)
        if r.status_code == 200:
            return r.json().get("record", {}).get("bot_active", True)
    except Exception:
        pass
    return True

def set_bot_status(status: bool):
    try:
        requests.put(JSONBIN_URL, json={"bot_active": status}, headers={"X-Master-Key": JSONBIN_MASTER_KEY}, timeout=3)
    except Exception as e:
        st.error(f"Failed to update engine state: {e}")

def render_bot_control_widget():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Live MT5 Engine")
    
    bot_active = get_bot_status()
    
    if bot_active:
        st.sidebar.success("State: ACTIVE 🟢")
        st.sidebar.caption("PC engine is scanning & trading.")
        if st.sidebar.button("🔴 PAUSE ENGINE", use_container_width=True):
            set_bot_status(False)
            st.rerun()
    else:
        st.sidebar.warning("State: PAUSED 🔴")
        st.sidebar.caption("Execution engine is on standby.")
        if st.sidebar.button("🟢 RESUME ENGINE", use_container_width=True):
            set_bot_status(True)
            st.rerun()

# ==============================================================================
# SIDEBAR NAVIGATION & CONTROLS
# ==============================================================================
mode = st.sidebar.selectbox("Select Scanning Mode", ["Single-Shot Analysis", "Multi-Timeframe Confluence"])

# Render the live MT5 engine control switch right below in the sidebar
render_bot_control_widget()

# System Instruction for ICT analysis
ICT_PROMPT = """
You are an expert ICT (Inner Circle Trader) mentor and price action analyst. 
Analyze the provided trading chart image(s) using ICT concepts:
1. **Market Structure**: Identify BOS (Break of Structure), CHoCH (Change of Character), and overall trend direction.
2. **Liquidity**: Pinpoint external/internal range liquidity sweeps or pools.
3. **Imbalances**: Locate Fair Value Gaps (FVG) or Order Blocks (OB) currently in play.
4. **Power of 3 / Setup**: Evaluate if a valid setup (e.g., OTE, Killzone model) is present and give a clear directional bias.
Keep the breakdown structured, professional, and actionable.
"""

# ==============================================================================
# SCANNER MODES LOGIC
# ==============================================================================
if mode == "Single-Shot Analysis":
    st.subheader("📸 Single Chart Analysis")
    uploaded_file = st.file_uploader("Upload your NAS100 or Forex chart screenshot...", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Chart", use_container_width=True)
        
        user_query = st.text_input("Custom instructions (optional):", value="Analyze this chart for immediate FVG and market structure.")
        
        if st.button("Run ICT Scan"):
            with st.spinner("Analyzing market structure and liquidity..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, f"{ICT_PROMPT}\n\nUser Question: {user_query}"]
                    )
                    st.markdown("### 📊 Scan Results")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")

elif mode == "Multi-Timeframe Confluence":
    st.subheader("🔄 Multi-Timeframe Confluence Scan")
    st.markdown("Upload multiple timeframe screenshots (e.g., Daily, 4H, 15M) to check for alignment.")
    
    uploaded_files = st.file_uploader("Upload charts...", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} chart(s) for confluence review.")
        for f in uploaded_files:
            st.image(Image.open(f), caption=f.name, use_container_width=True)
            
        if st.button("Analyze Confluence"):
            with st.spinner("Correlating multi-timeframe structure and bias..."):
                try:
                    content_payload = [ICT_PROMPT, "Analyze these multiple timeframe charts together for top-down confluence:"]
                    for f in uploaded_files:
                        content_payload.append(Image.open(f))
                        
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=content_payload
                    )
                    st.markdown("### 🌐 Confluence Breakdown")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"An error occurred during confluence analysis: {e}")
