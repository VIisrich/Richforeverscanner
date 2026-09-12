import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# Securely load the API key from Streamlit secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Page Config for mobile dark-mode aesthetic
st.set_page_config(page_title="RichforeverAI", page_icon="⚡", layout="centered")

# Custom CSS for slick dark styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #ff3333 !important; text-align: center; }
    .stButton>button { width: 100%; background-color: #ff3333; color: white; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>RICHFOREVER AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>ICT Vision Confluence & Execution Panel</p>", unsafe_allow_html=True)
st.markdown("---")

# Mode Selector
mode = st.radio("Select Scan Type", ["Single-Shot Quick Scan", "Multi-Timeframe Session (H1 + 5m)"], horizontal=True)

if mode == "Single-Shot Quick Scan":
    uploaded_file = st.file_uploader("Upload Single Chart Screenshot", type=["png", "jpg", "jpeg"], key="single")
    tf_note = st.selectbox("Timeframe Context", ["1H Chart / Macro Bias", "15m Equilibrium Array", "5m Execution FVG", "1m Scalp Setup"], key="tf_single")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Active Chart Feed", use_container_width=True)
        
        if st.button("RUN PIXEL SCAN"):
            with st.spinner("Analyzing market structure & liquidity..."):
                prompt = f"""
                You are the RichforeverAI Vision Engine using ICT concepts. 
                This chart context is: "{tf_note}".
                Analyze it with extreme precision. Keep your answer ultra-short and zero fluff.
                Format your response strictly like this:
                - **Timeframe/Context**: [H1 Bias / 15m Equilibrium / 5m Entry]
                - **Bias**: [Bullish / Bearish]
                - **Zone**: [Discount / Premium / FVG Level]
                - **Verdict**: [TAKE TRADE / WAIT / NO SETUP]
                - **Entry / SL / TP**: [Exact price levels if TAKE TRADE, else N/A]
                - **Quick Note**: [One sentence maximum reason]
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[image, prompt],
                        config=types.GenerateContentConfig(temperature=0.2)
                    )
                    
                    st.markdown("### 📊 CONFLUENCE REPORT")
                    st.success("Scan Complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"❌ API Error: {e}")

else:
    # Multi-Timeframe Mode allowing multiple image selections
    uploaded_files = st.file_uploader("Upload Multiple Charts (e.g., H1 first, then 5m execution)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="multi")
    
    if uploaded_files:
        images = []
        for file in uploaded_files:
            img = Image.open(file)
            images.append(img)
            st.image(img, caption=f"Loaded: {file.name}", use_container_width=True)
            
        if st.button("RUN MULTI-TF CONFLUENCE SCAN"):
            with st.spinner("Blending multi-timeframe narrative..."):
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
                
                # Bundle prompt text and all uploaded images into contents list
                contents = images + [prompt]
                
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(temperature=0.2)
                    )
                    
                    st.markdown("### 📊 MULTI-TF CONFLUENCE REPORT")
                    st.success("Multi-Scan Complete")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"❌ API Error: {e}")
