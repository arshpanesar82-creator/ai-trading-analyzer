import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai

st.set_page_config(page_title="AI Trade Analyzer", layout="wide")
st.title("🚀 Free AI Trading Chart Analyzer")
st.caption("Entry | Stop Loss | Confidence % — Powered by Gemini 2.5 Flash")

gemini_key = st.text_input("Paste your Gemini API Key here", type="password")

ticker = st.text_input("Ticker (e.g. BTC-USD, AAPL, EURUSD=X)", "BTC-USD")
timeframe = st.selectbox("Timeframe", ["5d", "1mo", "3mo"])

uploaded_file = st.file_uploader("Or upload your own chart screenshot", type=["png", "jpg", "jpeg"])

if st.button("Analyze & Give Trade", type="primary"):
    if not gemini_key:
        st.error("Please enter your Gemini API key")
    else:
        with st.spinner("Fetching chart + AI analyzing..."):
            try:
                # Fetch data
                data = yf.download(ticker, period=timeframe, progress=False)
                
                if data.empty:
                    st.error("No data found. Try another ticker.")
                else:
                    # Show interactive chart to YOU
                    fig = go.Figure(data=[go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close']
                    )])
                    fig.update_layout(title=f"{ticker} {timeframe} Chart", height=600, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Current price for prompt
                    current_price = data['Close'][-1]
                    
                    # Prepare prompt (no image needed)
                    prompt = f"""
You are a professional technical analyst.
Analyze the {ticker} chart ({timeframe} timeframe).
Current price is approximately {current_price:.4f}.

Return ONLY in this exact format:

**Direction**: Buy or Sell
**Entry Price**: exact price
**Stop Loss (SL)**: exact price
**Confidence**: XX% (be honest, 0-100)
**Reasoning**: 2-3 short sentences (support/resistance, patterns, indicators)

If no clear setup, say: "No clear high-probability setup right now."
"""

                    # If user uploaded a screenshot, use it (Gemini loves images)
                    if uploaded_file is not None:
                        image = uploaded_file.getvalue()
                        contents = [prompt, {"mime_type": "image/png", "data": image}]
                    else:
                        contents = [prompt]

                    # Call Gemini
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(contents)
                    
                    st.subheader("🧠 AI Trade Signal")
                    st.markdown(response.text)
                    
                    st.warning("⚠️ Educational only. Not financial advice.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
