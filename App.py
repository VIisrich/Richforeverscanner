import os
import time
import streamlit as st
import requests
import base64
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

    /* Hero header */
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

    /* Section headers inside pages */
    h2, h3 {{ color: #f3f4fa !important; font-weight: 700 !important; }}

    /* Buttons */
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

    /* Cards */
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

    /* Sidebar */
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

    /* Status pill */
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

gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))

# ==============================================================================
# MULTI-PROVIDER VISION WRAPPER (Claude primary, Gemini fallback)
# ==============================================================================
# Gemini's 503 "high demand" errors have been persistent for a week+ (this is a
# widely-reported, ongoing issue on Google's side, not something client-side
# retries alone fix: https://discuss.ai.google.dev has many open threads on it).
# Claude Sonnet 5 supports vision and is used as the primary engine here, with
# Gemini kept only as an automatic fallback if Claude is unavailable or unset.

import io
try:
    import anthropic
except ImportError:
    anthropic = None


def _pil_to_b64_png(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _claude_generate(images: list, prompt: str, max_retries: int = 4):
    """Calls Claude Sonnet 5 vision with retry/backoff on overload (529) or rate limit (429)."""
    if not anthropic_key or anthropic is None:
        raise RuntimeError("Claude not configured")

    client = anthropic.Anthropic(api_key=anthropic_key)
    content = [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": _pil_to_b64_png(img)}}
        for img in images
    ]
    content.append({"type": "text", "text": prompt})

    last_err = None
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=1500,
                messages=[{"role": "user", "content": content}],
            )
            return "".join(block.text for block in resp.content if block.type == "text")
        except Exception as e:
            last_err = e
            err_str = str(e)
            print(f"[CLAUDE FAIL] attempt={attempt} error={err_str}")
            if "429" in err_str or "rate_limit" in err_str.lower():
                st.toast("Claude rate limit hit, backing off...", icon="⏳")
                wait = min(4 * (attempt + 1), 30)
            elif "529" in err_str or "overloaded" in err_str.lower():
                st.toast("Claude overloaded, retrying...", icon="⚡")
                wait = min(2 ** attempt, 20)
            else:
                raise e
            if attempt < max_retries - 1:
                time.sleep(wait)
                continue
            raise e
    raise last_err


def _gemini_generate(images: list, prompt: str, max_retries: int = 5):
    """Rotates through Gemini Flash models with real exponential backoff, and tells overload
    (503) apart from rate-limit/quota (429) so each gets the right kind of wait."""
    if not gemini_key:
        raise RuntimeError("Gemini not configured")

    client = genai.Client(api_key=gemini_key)
    # Newest model last: it's the most in-demand right now, so give the more
    # mature/less-congested models first crack at the request.
    models_pool = ["gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.8-flash"]
    contents = images + [prompt]

    last_err = None
    for attempt in range(max_retries):
        current_model = models_pool[attempt % len(models_pool)]
        try:
            resp = client.models.generate_content(model=current_model, contents=contents)
            return resp.text
        except Exception as e:
            last_err = e
            err_str = str(e)
            print(f"[GEMINI FAIL] model={current_model} attempt={attempt} error={err_str}")

            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                st.toast(f"Rate limit hit on {current_model}, backing off...", icon="⏳")
                wait = min(4 * (attempt + 1), 30)
            elif "503" in err_str or "UNAVAILABLE" in err_str or "timeout" in err_str.lower():
                st.toast(f"{current_model} overloaded, retrying...", icon="⚡")
                wait = min(2 ** attempt, 20)
            else:
                raise e

            if attempt < max_retries - 1:
                time.sleep(wait)
                continue
            raise e

    raise last_err or Exception("All Gemini endpoints are currently busy. Please try again.")


def analyze_chart(images: list, prompt: str) -> str:
    """Tries Claude first (primary), automatically falls back to Gemini if Claude
    is unset or fails after its own retries. Raises the last error if both fail."""
    errors = []
    if anthropic_key and anthropic is not None:
        try:
            st.toast("Analyzing with Claude...", icon="🧠")
            return _claude_generate(images, prompt)
        except Exception as e:
            errors.append(f"Claude: {e}")

    if gemini_key:
        try:
            st.toast("Analyzing with Gemini...", icon="⚡")
            return _gemini_generate(images, prompt)
        except Exception as e:
            errors.append(f"Gemini: {e}")

    if not errors:
        raise RuntimeError("No vision provider configured — set ANTHROPIC_API_KEY and/or GEMINI_API_KEY.")
    raise RuntimeError(" | ".join(errors))



def load_and_optimize_image(uploaded_file):
    """Resizes uploaded images to prevent payload bottlenecks and hanging."""
    img = Image.open(uploaded_file)
    img.thumbnail((1400, 1400))
    return img

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
st.sidebar.caption("⚡ Fast Flash Multi-Model Rotation")
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
            <h4>⚡ Ultra-Fast Flash Rotation</h4>
            <p>Optimized with instant failover across lightweight Flash endpoints to prevent long loading delays.</p>
        </div>
        <div class="rf-card">
            <h4>📸 Single-Shot Analysis</h4>
            <p>Upload one chart screenshot for a fast ICT read: market structure, liquidity sweeps, FVGs, confidence level, and directional bias.</p>
        </div>
        <div class="rf-card">
            <h4>🔄 Multi-Timeframe Confluence</h4>
            <p>Blend Higher and Lower timeframe charts into a single zero-fluff verdict with strict bot execution rules.</p>
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

    if not gemini_key and not anthropic_key:
        st.error("⚠️ No vision provider configured — set ANTHROPIC_API_KEY and/or GEMINI_API_KEY in secrets.")
        st.stop()

    uploaded_file = st.file_uploader("Upload chart screenshot...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = load_and_optimize_image(uploaded_file)
        st.image(image, caption="Optimized Chart Feed", use_container_width=True)
        user_query = st.text_input("Custom instructions:", value="Analyze this chart for FVG and setup viability.")

        if st.button("RUN PIXEL SCAN"):
            with st.spinner("Executing fast scan..."):
                try:
                    result_text = analyze_chart(
                        images=[image],
                        prompt=f"{ICT_PROMPT}\n\nUser Question: {user_query}"
                    )
                    st.markdown("### 📊 Scan Report")
                    st.success("Scan complete")
                    st.markdown(result_text)
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "rate_limit" in err_str.lower():
                        st.error("⚠️ Rate limit hit on all configured providers. Wait a minute and try again — or upgrade your API key's tier for higher limits.")
                    elif "503" in err_str or "UNAVAILABLE" in err_str or "529" in err_str or "overloaded" in err_str.lower():
                        st.error("⚠️ Vision provider(s) overloaded right now. This is temporary — please try again shortly.")
                    else:
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

    if not gemini_key and not anthropic_key:
        st.error("⚠️ No vision provider configured — set ANTHROPIC_API_KEY and/or GEMINI_API_KEY in secrets.")
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
            with st.spinner("Processing multi-timeframe confluence feed..."):
                try:
                    prompt = """
                    You are the RichforeverAI Vision Engine using exact ICT rules from the live execution bot.
                    Analyze the provided multi-timeframe charts (H1 macro, 15m equilibrium, 5m entry) using these strict rules:
                    1. **H1 Macro Bias**: Verify if price action is aligned with the 20 EMA trend direction.
                    2. **15m Equilibrium Filter**: For Buys, price must be in Discount. For Sells, price must be in Premium.
                    3. **5m FVG Retracement**: Price pulling back into an active Fair Value Gap.
                    4. **Dynamic R:R**: Minimum 2.0 R:R target.
                    
                    Format strictly like this:
                    - **Timeframe/Context**: [Multi-TF H1 + 15m + 5m Bot Alignment]
                    - **H1 Bias**: [Bullish / Bearish]
                    - **15m Equilibrium Zone**: [Discount / Premium]
                    - **5m FVG Status**: [Retracing to FVG / No Setup]
                    - **Confidence Level**: [High / Medium / Low]
                    - **Verdict**: [TAKE TRADE / WAIT / NO SETUP]
                    - **Target R:R**: [Must be >= 2.0R if TAKE TRADE, else N/A] (Include suggested SL and TP levels)
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
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "rate_limit" in err_str.lower():
                        st.error("⚠️ Rate limit hit on all configured providers. Wait a minute and try again — or upgrade your API key's tier for higher limits.")
                    elif "503" in err_str or "UNAVAILABLE" in err_str or "529" in err_str or "overloaded" in err_str.lower():
                        st.error("⚠️ Vision provider(s) overloaded right now. This is temporary — please try again shortly.")
                    else:
                        st.error(f"Confluence error: {e}")
