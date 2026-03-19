# --- 第一部分：載入工具 (Import) ---
import streamlit as st
import yfinance as yf

# --- 第二部分：設定網頁門面 (UI) ---
st.title("我的電信股分析工具")
st.subheader("歡迎回來，這是您的專屬數據看板")

# --- 第三部分：邏輯運算 (Logic) ---
stock_id = st.text_input("請輸入股票代號", "2412.TW")

# --- 第四部分：顯示結果 (Display) ---
if st.button("點我抓取數據"):
    data = yf.download(stock_id, period="1mo")
    st.line_chart(data['Close']) # 直接畫出收盤價折線圖
