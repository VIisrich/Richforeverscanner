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
    .rf-pill-maint {{ background: rgba(255, 157, 92, 0.14); color: #ff9d5c; border: 1px solid rgba(255,157,92,0.35); }}

    hr {{ border-color: rgba(255,255,255,0.08) !important; }}
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: #3a2a55; border-radius: 8px; }}

    .rf-verdict-banner {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.65rem;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 0.9rem 0 1.3rem 0;
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
# GLOBAL MAINTENANCE MODE & SECURE PASSCODE BYPASS
# ==============================================================================
MAINTENANCE_MODE = False

if "admin_unlocked" not in st.session_state:
    st.session_state["admin_unlocked"] = False

if MAINTENANCE_MODE and not st.session_state["admin_unlocked"]:
    st.sidebar.markdown("<div class='rf-sidebar-brand'>⚡ <span>RICHFOREVER AI</span></div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div class='rf-pill rf-pill-maint'>STATUS: MAINTENANCE 🛠️</div>", unsafe_allow_html=True)
    st.sidebar.caption("⚡ Estimated back online around 2:30 PM")

    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 1rem 1rem 0.5rem 1rem;">
            <div style="font-size: 3.5rem; margin-bottom: 0.6rem;">🛠️</div>
            <h1 style="font-size: 2.1rem; font-weight: 800; background: linear-gradient(90deg, #ff5b5b, #ff9d5c 45%, #a06bff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">SYSTEM MAINTENANCE</h1>
            <p style="color: #9a9fb5; font-size: 0.98rem; max-width: 480px; line-height: 1.5; margin-bottom: 1rem;">
                RichforeverAI is currently undergoing scheduled backend updates and scanner optimizations. All analysis suites are temporarily offline.
            </p>
            <div style="background: rgba(255,157,92,0.1); border: 1px solid rgba(255,157,92,0.35); border-radius: 14px; padding: 0.7rem 1.2rem; color: #ff9d5c; font-weight: 600; font-size: 0.92rem; margin-bottom: 1rem;">
                ⏳ Estimated Completion: Around <strong>2:30 PM</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("admin_login_form"):
            passcode_input = st.text_input("🔑 Admin Passcode", type="password", placeholder="Enter passcode to test...")
            submit_btn = st.form_submit_button("Unlock App for Testing")
            if submit_btn:
                if passcode_input == "richforever":
                    st.session_state["admin_unlocked"] = True
                    st.rerun()
                else:
                    st.error("Incorrect passcode.")

    st.stop()

# ==============================================================================
# OPENROUTER API CLIENT & VISION ENGINE
# ==============================================================================
def get_openrouter_client():
    api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))))
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
    api_key = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))))
    if not api_key:
        raise RuntimeError("OpenRouter API key not configured. Please add OPENROUTER_API_KEY to your Streamlit secrets.")

    client = get_openrouter_client()
    
    full_prompt = (
        prompt + 
        "\n\nSTRICT RULES:\n"
        "1. Follow ICT price action rules strictly (H1 macro bias, 15m equilibrium discount/premium, 5m FVG confluence, R:R >= 2.0R).\n"
        "2. Output must clearly state BUY, SELL, or WAIT.\n"
        "3. Provide exact Stop Loss (SL) and Take Profit (TP) levels if actionable.\n"
        "4. Keep reasons direct and concise (one sentence maximum)."
    )
    
    content_list = [{"type": "text", "text": full_prompt}]
    for img in images:
        data_uri = pil_image_to_base64_data_uri(img)
        content_list.append({
            "type": "image_url",
            "image_url": {"url": data_uri}
        })
    
    messages = [{"role": "user", "content": content_list}]
    
    # OpenRouter model endpoint rotation
    models_to_try = ["google/gemini-2.5-flash", "google/gemini-2.5-flash-preview", "google/gemini-flash-1.5"]
    
    last_exception = None
    for model_name in models_to_try:
        try:
            st.toast(f"Analyzing via OpenRouter ({model_name})", icon="⚡")
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
            
    raise Exception(f"All OpenRouter models are currently unavailable. Details: {last_exception}")

# ==============================================================================
# VERDICT EXTRACTION & URGENCY BANNER
# ==============================================================================
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
st.sidebar.caption("⚡ Powered by OpenRouter (google/gemini-2.5-flash)")

# ==============================================================================
# SHARED ICT ANALYSIS PROMPT
# ==============================================================================
ICT_PROMPT = """
ICT price action rules:
1. H1 Macro Bias.
2. 15m Equilibrium (Discount for Buys, Premium for Sells).
3. 5m FVG Confluence.
4. R:R >= 2.0R.
5. State BUY, SELL, or WAIT.
"""

# ==============================================================================
# PAGE 1: HOME / DASHBOARD
# ==============================================================================
if page == "Home / Dashboard":
    st.markdown("""
        <div class="rf-hero">
            <h1>⚡ RICHFOREVER AI</h1>
            <p>ICT Vision Confluence & Market Scanner Suite</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="rf-card">
            <h4>⚡ Live Bot Strategy Alignment</h4>
            <p>Scanner logic mirrors the automated execution engine: H1 structure bias, 15m equilibrium filters, and 5m FVG retracements.</p>
        </div>
        <div class="rf-card">
            <h4>📸 Single-Shot Analysis</h4>
            <p>Upload a standalone chart screenshot to scan for Fair Value Gaps, liquidity sweeps, and setup viability instantly.</p>
        </div>
        <div class="rf-card">
            <h4>🔄 Multi-Timeframe Confluence</h4>
            <p>Cross-examine multi-TF captures with strict >= 2.0R, TP, and SL rules.</p>
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

    uploaded_file = st.file_uploader("Upload chart screenshot...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = load_and_optimize_image(uploaded_file)
        st.image(image, caption="Optimized Chart Feed", use_container_width=True)
        user_query = st.text_input("Custom instructions:", value="Analyze this chart for FVG and setup viability.")

        if st.button("RUN PIXEL SCAN"):
            with st.spinner("Executing OpenRouter vision scan..."):
                try:
                    result_text = analyze_chart(
                        images=[image],
                        prompt=f"{ICT_PROMPT}\n\nUser Question: {user_query}"
                    )
                    st.markdown("### 📊 Scan Report")
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
            <h1>🔄 Multi-Timeframe Confluence</h1>
            <p>Multi-TF Fusion Scan</p>
        </div>
    """, unsafe_allow_html=True)

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
            with st.spinner("Processing multi-timeframe feed through OpenRouter..."):
                try:
                    prompt = """
                    Analyze multi-TF charts (H1, 15m, 5m) using strict ICT rules. Output ONLY these exact bullet points concisely:
                    - **Verdict**: [BUY / SELL / WAIT]
                    - **Target R:R**: [>= 2.0R or N/A]
                    - **Stop Loss (SL)**: [Price]
                    - **Take Profit (TP)**: [Price]
                    - **Reason**: [Exactly one sentence maximum]
                    """

                    result_text = analyze_chart(
                        images=optimized_images,
                        prompt=prompt
                    )
                    st.markdown("### 🌐 Confluence Report")
                    st.success("Multi-scan complete")
                    render_verdict_banner(result_text)
                    st.markdown(result_text)
                except Exception as e:
                    st.error(f"⚠️ {e}")
