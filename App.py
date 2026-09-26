import os
import streamlit as st
import base64
from PIL import Image
import io
import re
from openai import OpenAI

# ==============================================================================
# CONFIG & SECRETS
# ==============================================================================
st.set_page_config(
    page_title="RichforeverAI - Technical Analysis Scanner",
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

    .rf-disclaimer-card {{
        background: rgba(255, 59, 59, 0.05);
        border: 1px solid rgba(255, 59, 59, 0.2);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.9rem;
        font-size: 0.85rem;
        color: #d1d5db;
        line-height: 1.5;
    }}
    .rf-disclaimer-card b {{ color: #ff6a6a; }}

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

    .rf-bias-pill {{
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.9rem;
        letter-spacing: 0.6px;
        margin-bottom: 0.8rem;
    }}
    .rf-bias-bullish {{ background: rgba(46, 204, 113, 0.15); color: #4fe08a; border: 1px solid rgba(46,204,113,0.45); }}
    .rf-bias-bearish {{ background: rgba(255, 59, 59, 0.15); color: #ff6a6a; border: 1px solid rgba(255,59,59,0.45); }}

    .rf-verdict-banner {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.65rem;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0 1.3rem 0;
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-align: center;
    }}
    .rf-verdict-icon {{ font-size: 1.5rem; line-height: 1; }}
    .rf-verdict-sub {{
        display: block;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        opacity: 0.75;
        margin-top: 0.15rem;
    }}

    .rf-levels-row {{
        display: flex;
        gap: 0.8rem;
        margin: -0.4rem 0 1.3rem 0;
    }}
    .rf-level-card {{
        flex: 1;
        border-radius: 12px;
        padding: 0.75rem 0.9rem;
        text-align: center;
    }}
    .rf-level-label {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.35rem;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        opacity: 0.85;
        margin-bottom: 0.3rem;
    }}
    .rf-level-value {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 0.3px;
    }}
    .rf-level-sl {{ background: rgba(255, 59, 59, 0.12); border: 1px solid rgba(255, 59, 59, 0.4); color: #ff6a6a; }}
    .rf-level-tp {{ background: rgba(46, 204, 113, 0.12); border: 1px solid rgba(46, 204, 113, 0.4); color: #4fe08a; }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# OPENROUTER API CLIENT & VISION ENGINE
# ==============================================================================
def get_openrouter_client():
    api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def load_and_optimize_image(uploaded_file):
    img = Image.open(uploaded_file)
    img.thumbnail((800, 800))
    if img.mode != "RGB":
        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        else:
            img = img.convert("RGB")
    return img

def pil_image_to_base64_data_uri(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

def analyze_chart(images: list, prompt: str) -> str:
    api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    if not api_key:
        raise RuntimeError("OpenRouter API key not configured. Please add OPENROUTER_API_KEY to your Streamlit secrets.")

    client = get_openrouter_client()
    
    content_list = [{"type": "text", "text": prompt}]
    for img in images:
        data_uri = pil_image_to_base64_data_uri(img)
        content_list.append({
            "type": "image_url",
            "image_url": {"url": data_uri}
        })
    
    messages = [{"role": "user", "content": content_list}]
    models_to_try = ["google/gemini-2.5-flash", "google/gemini-2.5-flash-preview", "google/gemini-flash-1.5"]
    
    last_exception = None
    for model_name in models_to_try:
        try:
            st.toast(f"Analyzing via RichforeverAI Engine...", icon="⚡")
            response = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
        except Exception as e:
            last_exception = e
            if "503" in str(e) or "UNAVAILABLE" in str(e) or "NOT_FOUND" in str(e) or "404" in str(e) or "rate_limit" in str(e):
                continue
            raise e
            
    raise Exception(f"All scanner nodes currently busy. Details: {last_exception}")

# ==============================================================================
# PARSING & BANNER RENDERING
# ==============================================================================
def extract_bias(text: str):
    match = re.search(r"bias[^\n]{0,50}?\b(BULLISH|BEARISH)\b", text, re.IGNORECASE)
    if not match:
        match = re.search(r"\b(BULLISH|BEARISH)\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else None

def extract_verdict(text: str):
    match = re.search(r"verdict[^\n]{0,80}?\b(BUY|SELL|WAIT)\b", text, re.IGNORECASE)
    if not match:
        match = re.search(r"\b(BUY|SELL|WAIT)\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else None

def extract_level(text: str, keyword_pattern: str):
    match = re.search(rf"{keyword_pattern}[^:\n]*:\s*\*{{0,2}}([^\n*]+)", text, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip(" *_-")
    if not value or value.upper() in ("N/A", "NA", "NONE"):
        return None
    return value

def render_verdict_banner(text: str):
    bias = extract_bias(text)
    if bias:
        bias_class = "rf-bias-bullish" if bias == "BULLISH" else "rf-bias-bearish"
        bias_icon = "📈" if bias == "BULLISH" else "📉"
        st.markdown(f"""
            <div style="text-align: center;">
                <span class="rf-bias-pill {bias_class}">{bias_icon} BIAS: {bias}</span>
            </div>
        """, unsafe_allow_html=True)

    verdict = extract_verdict(text)
    if not verdict:
        return

    config = {
        "BUY":  {"color": "#2ecc71", "bg": "rgba(46, 204, 113, 0.16)",  "border": "rgba(46, 204, 113, 0.60)",  "icon": "🟢", "label": "BUY",  "sub": "ENTER LONG"},
        "SELL": {"color": "#ff3b3b", "bg": "rgba(255, 59, 59, 0.16)",   "border": "rgba(255, 59, 59, 0.60)",   "icon": "🔴", "label": "SELL", "sub": "ENTER SHORT"},
        "WAIT": {"color": "#9a9fb5", "bg": "rgba(154, 159, 181, 0.14)", "border": "rgba(154, 159, 181, 0.45)", "icon": "⚪", "label": "WAIT", "sub": "NO SETUP YET"},
    }[verdict]

    st.markdown(f"""
        <div class="rf-verdict-banner" style="
            background:{config['bg']};
            border:2px solid {config['border']};
            color:{config['color']};
        ">
            <span class="rf-verdict-icon">{config['icon']}</span>
            <span>{config['label']}<span class="rf-verdict-sub">{config['sub']}</span></span>
        </div>
    """, unsafe_allow_html=True)

    if verdict in ("BUY", "SELL"):
        sl = extract_level(text, r"stop\s*loss(?:\s*\(sl\))?")
        tp = extract_level(text, r"take\s*profit(?:\s*\(tp\))?")
        if sl or tp:
            sl_html = f"""
                <div class="rf-level-card rf-level-sl">
                    <div class="rf-level-label">🛑 STOP LOSS</div>
                    <div class="rf-level-value">{sl or '—'}</div>
                </div>""" if sl else ""
            tp_html = f"""
                <div class="rf-level-card rf-level-tp">
                    <div class="rf-level-label">🎯 TAKE PROFIT</div>
                    <div class="rf-level-value">{tp or '—'}</div>
                </div>""" if tp else ""
            st.markdown(f"""<div class="rf-levels-row">{sl_html}{tp_html}</div>""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR NAVIGATION & LEGAL FOOTER
# ==============================================================================
st.sidebar.markdown("<div class='rf-sidebar-brand'>⚡ <span>RICHFOREVER AI</span></div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Home / Dashboard", "Single-Shot Analysis", "Multi-Timeframe Confluence"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div class='rf-pill rf-pill-online'>SCANNER ENGINE: ONLINE 🟢</div>", unsafe_allow_html=True)
st.sidebar.caption("⚡ Powered by RichforeverAI Core")
st.sidebar.markdown("""
<div style="font-size: 0.73rem; color: #8a8f9d; line-height: 1.4; margin-top: 0.8rem; padding: 0.4rem 0;">
    <b>Risk Disclaimer:</b> Trading involves substantial risk of loss and is not suitable for every investor. RichforeverAI is an educational and analytical charting tool. Past performance does not guarantee future results. By using this software, you agree to our Terms of Service and use this tool entirely at your own risk.
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# PAGE 1: HOME / DASHBOARD
# ==============================================================================
if page == "Home / Dashboard":
    st.markdown("""
        <div class="rf-hero">
            <h1>⚡ RICHFOREVER AI</h1>
            <p>Advanced Technical Chart Scanner Suite</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="rf-card">
            <h4>📊 Automated Technical Processing</h4>
            <p>Process single and multi-timeframe charts seamlessly using advanced computer vision models, institutional price action frameworks, and dynamic risk-reward parameters.</p>
        </div>
        <div class="rf-card">
            <h4>📸 Single-Shot Analysis</h4>
            <p>Scan execution charts instantly for structural confirmation, key swing levels, and optimized target metrics.</p>
        </div>
        <div class="rf-card">
            <h4>🔄 Multi-Timeframe Confluence</h4>
            <p>Cross-examine multi-timeframe market feeds for structural alignment, zone testing, and high-probability setup verification.</p>
        </div>
        <div class="rf-disclaimer-card">
            <b>⚠️ Terms of Service & Legal Notice:</b> Trading involves substantial risk of loss. RichforeverAI is an analytical tool provided strictly for educational and informational purposes. The creator accepts zero liability for any financial or trading losses incurred.
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# PAGE 2: SINGLE-SHOT ANALYSIS
# ==============================================================================
elif page == "Single-Shot Analysis":
    st.markdown("""
        <div class="rf-hero">
            <h1>📸 Single Chart Technical Scanner</h1>
            <p>Multi-Factor Price Action & Structure Review</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload chart screenshot...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = load_and_optimize_image(uploaded_file)
        st.image(image, caption="Optimized Chart Feed", use_container_width=True)
        user_query = st.text_input("Custom notes / Asset name (e.g., NAS100 or XAUUSD):", value="NAS100")

        if st.button("RUN TECHNICAL SCAN"):
            with st.spinner("Analyzing chart parameters..."):
                try:
                    prompt = f"""
                    You are an expert quantitative technical analyst. Analyze this chart strictly using professional market structure rules:
                    1. **Trend Bias**: Evaluate momentum and recent structure (BULLISH or BEARISH).
                    2. **Zone Filtering**: Check key equilibrium zones and discount/premium positioning.
                    3. **Volatility Check**: Verify candle range expansion relative to average market noise.
                    4. **Trigger Evaluation**: Confirm if price is currently mitigating a valid zone aligned with bias.
                    5. **Risk Management**: Minimum R:R >= 2.0. Stop loss placed beyond recent swing high/low with floor constraints. Take profit targeting primary liquidity pools.

                    Output ONLY these exact bullet points concisely, with no extra paragraphs:
                    - **Bias**: [BULLISH / BEARISH]
                    - **Verdict**: [BUY / SELL / WAIT]
                    - **Confidence**: [High / Medium / Low with % e.g., High (85%)]
                    - **Target R:R**: [>= 2.0R or N/A]
                    - **Stop Loss (SL)**: [Exact Price]
                    - **Take Profit (TP)**: [Exact Price]
                    - **Reason**: [Concise technical rationale: state trend bias, zone position, trigger status, and target].
                    
                    Asset / User Notes: {user_query}
                    """

                    result_text = analyze_chart(images=[image], prompt=prompt)
                    st.markdown("### 📊 Technical Scan Report")
                    st.success("Scan complete")
                    render_verdict_banner(result_text)
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"⚠️ {e}")

# ==============================================================================
# PAGE 3: MULTI-TIMEFRAME CONFLUENCE
# ==============================================================================
elif page == "Multi-Timeframe Confluence":
    st.markdown("""
        <div class="rf-hero">
            <h1>🔄 Multi-Timeframe Confluence Scan</h1>
            <p>Multi-Horizon Structure & Zone Alignment</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload multi-timeframe charts...", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 3))
        optimized_images = []
        for i, f in enumerate(uploaded_files):
            opt_img = load_and_optimize_image(f)
            optimized_images.append(opt_img)
            with cols[i % len(cols)]:
                st.image(opt_img, caption=f.name, use_container_width=True)

        if st.button("RUN MULTI-TF CONFLUENCE SCAN"):
            with st.spinner("Cross-examining multi-timeframe feeds..."):
                try:
                    prompt = """
                    You are an expert multi-timeframe technical analyst. Cross-examine these chart captures using strict multi-horizon rules:
                    1. **Higher TF Bias**: Establish structural direction via momentum and moving averages.
                    2. **Mid TF Zone Filter**: Ensure proper premium/discount positioning.
                    3. **Lower TF Confluence**: Check for overlapping zone mitigations and triggers.
                    4. **Execution & R:R**: Validate minimum 2.0R, swing SL, and liquidity pool TP targets.

                    Output ONLY these exact bullet points concisely:
                    - **Bias**: [BULLISH / BEARISH]
                    - **Verdict**: [BUY / SELL / WAIT]
                    - **Confidence**: [High / Medium / Low with % e.g., High (85%)]
                    - **Target R:R**: [>= 2.0R or N/A]
                    - **Stop Loss (SL)**: [Exact Price]
                    - **Take Profit (TP)**: [Exact Price]
                    - **Reason**: [Concise cross-TF rationale: higher TF bias + zone position + confluence + target].
                    """

                    result_text = analyze_chart(images=optimized_images, prompt=prompt)
                    st.markdown("### 🌐 Multi-TF Confluence Report")
                    st.success("Multi-scan complete")
                    render_verdict_banner(result_text)
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"⚠️ {e}")
