import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
from PIL import Image
import io

# MUST be the VERY FIRST Streamlit command
st.set_page_config(page_title="AI Trade Analyzer", layout="wide")

st.title("🚀 Free AI Trading Chart Analyzer")
st.caption("Entry | Stop Loss | Confidence % — Powered by Gemini")

# Gemini Key (use Secrets later for production)
gemini_key = st.text_input("Paste your Gemini API Key here (only you can see it)", type="password")

ticker = st.text_input("Ticker (e.g. BTC-USD, AAPL, EURUSD=X)", "BTC-USD")
timeframe = st.selectbox("Timeframe", ["5d", "1mo", "3mo"])

if st.button("Analyze Chart & Give Trade", type="primary"):
    if not gemini_key:
        st.error("Please enter your Gemini API key")
    else:
        with st.spinner("Fetching data + AI analyzing..."):
            try:
                data = yf.download(ticker, period=timeframe, progress=False)
                
                if data.empty:
                    st.error("No data for this ticker. Try another (e.g. BTC-USD)")
                else:
                    # Candlestick chart
                    fig = go.Figure(data=[go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close']
                    )])
                    fig.update_layout(title=f"{ticker} Chart", height=500, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Convert chart to image for Gemini
                    buf = io.BytesIO()
                    fig.write_image(buf, format="png")
                    buf.seek(0)
                    chart_img = Image.open(buf)
                    
                    # Configure Gemini
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    prompt = f"""
You are a professional technical trader. Analyze this {ticker} chart.

Return ONLY in this format (be realistic with confidence):

**Direction**: Buy / Sell
**Entry Price**: exact price
**Stop Loss (SL)**: exact price
**Confidence**: XX% (0-100)
**Reasoning**: 2-3 short sentences (support/resistance, patterns, indicators)

Current price ≈ {data['Close'][-1]:.4f}
If no good setup, say "No clear high-probability setup right now."
"""
                    
                    response = model.generate_content([prompt, chart_img])
                    st.subheader("🧠 AI Trade Signal")
                    st.markdown(response.text)
                    
                    st.warning("⚠️ Educational only. Not financial advice. Trade at your own risk.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
