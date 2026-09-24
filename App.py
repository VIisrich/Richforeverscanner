import os
import streamlit as st
import base64
from PIL import Image
import io

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ==============================================================================
# CONFIG & SECRETS
# ==============================================================================
st.set_page_config(
    page_title="RichforeverAI - ICT Scanner",
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
# RELIABLE OPENROUTER VISION ENGINE (GEMINI 2.5 FLASH)
# ==============================================================================
def analyze_chart(images: list, prompt: str) -> str:
    if not openrouter_key:
        raise RuntimeError("OpenRouter API key not configured. Please set OPENROUTER_API_KEY in secrets.")
    if OpenAI is None:
        raise RuntimeError("openai package is not installed.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_key,
        default_headers={
            "HTTP-Referer": "https://richforever.ai",
            "X-Title": "RichforeverAI"
        }
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

    st.toast("Analyzing via Gemini 2.5 Flash...", icon="⚡")
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
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

    raise Exception("OpenRouter vision request returned empty response.")

# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown("<div class='rf-sidebar-brand'>⚡ <span>RICHFOREVER AI</span></div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Home / Dashboard", "Single-Shot Analysis", "Multi-Timeframe Confluence"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='rf-pill rf-pill-online'>SCANNER STATUS: ONLINE 🟢</div>", unsafe_allow_html=True)
st.sidebar.caption("⚡ Powered by Gemini 2.5 Flash via OpenRouter")

# ==============================================================================
# ALGORITHMIC ICT STRATEGY PROMPTS
# ==============================================================================
ICT_PROMPT = """
You are the RichforeverAI algorithmic vision engine. Analyze the provided chart using your strict mechanical ICT strategy rules:
1. **H1 Bias**: Check 20 EMA and recent candle closes (Must be explicitly Bullish or Bearish).
2. **15m Equilibrium**: Determine if price is in Premium (above 50% midpoint) or Discount (below 50% midpoint). Sells only in Premium; Buys only in Discount.
3. **5m FVG & Confluence**: Locate active Fair Value Gaps and structural swing points (5-candle high/low for SL).
4. **Risk-to-Reward (R:R)**: Calculate potential target against liquidity pools (BSL/SSL). Must be >= 2.0R.
5. **Verdict**: Output must be strict: ENTER TRADE, WAIT, or NO SETUP.
"""

MULTI_TF_PROMPT = """
You are the RichforeverAI Multi-TF Confluence Engine. Analyze the H1, 15m, and 5m charts together using these exact mechanical rules:
- **H1 Bias**: [Bullish / Bearish]
- **15m Equilibrium Zone**: [Discount / Premium — Must match direction: Buy in Discount, Sell in Premium]
- **5m FVG Status**: [Mitigating FVG / No Setup]
- **Confidence Level**: [High / Medium / Low]
- **Verdict**: [ENTER TRADE / WAIT / NO SETUP]
- **Target R:R**: [Must be >= 2.0R if ENTER TRADE, else N/A]
- **Stop Loss (SL)**: [Exact structural anchor + ATR buffer]
- **Take Profit (TP)**: [Exact liquidity target / FVG pool]
- **Quick Note**: [Strict mechanical reason based on FVG & Equilibrium]
"""

# ==============================================================================
# PAGE 1: HOME / DASHBOARD
# ==============================================================================
if page == "Home / Dashboard":
    st.markdown("""
        <div class="rf-hero">
            <h1>⚡ RICHFOREVER AI</h1>
            <p>Algorithmic ICT Vision Confluence & Market Scanner Suite</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="rf-card">
            <h4>⚡ Algorithmic Execution Rules Active</h4>
            <p>Scans charts using your exact backtest parameters: H1 trend bias, 15m Premium/Discount equilibrium filters, and strict 2.0R FVG targets.</p>
        </div>
        <div class="rf-card">
            <h4>📸 Single-Shot Analysis</h4>
            <p>Upload a standalone chart screenshot to scan for Fair Value Gaps, structural swing points, and setup viability.</p>
        </div>
        <div class="rf-card">
            <h4>🔄 Multi-Timeframe Confluence</h4>
            <p>Cross-examine multiple timeframe captures (Macro H1, Equilibrium 15m, Execution 5m) before taking action.</p>
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# PAGE 2: SINGLE-SHOT ANALYSIS
# ==============================================================================
elif page == "Single-Shot Analysis":
    st.markdown("""
        <div class="rf-hero">
            <h1>📸 Single Chart Analysis</h1>
            <p>Algorithmic ICT Vision Feed</p>
        </div>
    """, unsafe_allow_html=True)

    if not openrouter_key:
        st.error("⚠️ No OpenRouter API key configured. Please add OPENROUTER_API_KEY to your Streamlit secrets.")
        st.stop()

    uploaded_file = st.file_uploader("Upload chart screenshot...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = load_and_optimize_image(uploaded_file)
        st.image(image, caption="Optimized Chart Feed", use_container_width=True)
        user_query = st.text_input("Custom instructions:", value="Evaluate this chart against ICT FVG and equilibrium rules.")

        if st.button("RUN PIXEL SCAN"):
            with st.spinner("Executing Gemini vision scan..."):
                try:
                    result_text = analyze_chart(
                        images=[image],
                        prompt=f"{ICT_PROMPT}\n\nUser Question: {user_query}"
                    )
                    st.markdown("### 📊 Algorithmic Scan Report")
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
            with st.spinner("Processing multi-timeframe feed through Gemini..."):
                try:
                    result_text = analyze_chart(
                        images=optimized_images,
                        prompt=MULTI_TF_PROMPT
                    )
                    st.markdown("### 🌐 Confluence Report")
                    st.success("Multi-scan complete")
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"⚠️ {e}")
