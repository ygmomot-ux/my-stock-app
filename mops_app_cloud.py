import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="電信與權值股監控", layout="wide")
st.title("電信三雄 & 權值股 訊息監控 (國際橋接版)")

# 股票代號清單 (加入鴻海 2317)
tickers = {
    "2412.TW": "中華電信",
    "3045.TW": "台灣大哥大",
    "4904.TW": "遠傳電信",
    "2317.TW": "鴻海",
    "8454.TW": "富邦媒 (momo)"
}

st.info("💡 透過 Yahoo Finance 獲取數據，能避開政府網站對雲端 IP 的封鎖。")

if st.button('獲取最新重大訊息與新聞'):
    # 使用 Streamlit 的欄位佈局，讓畫面更美觀
    cols = st.columns(len(tickers))
    
    for i, (symbol, name) in enumerate(tickers.items()):
        with cols[i % len(tickers)]:
            st.subheader(f"{name}")
            st.caption(f"代號: {symbol}")
            
            try:
                stock = yf.Ticker(symbol)
                news = stock.news
                
                if news:
                    for item in news[:5]: # 顯示最新的 5 則
                        # --- 核心修正處：使用 .get() 避免報錯 ---
                        publisher = item.get('publisher', '新聞來源')
                        title = item.get('title', '無標題')
                        link = item.get('link', '#')
                        
                        with st.expander(title):
                            st.write(f"來源: {publisher}")
                            st.markdown(f"[點此閱讀全文]({link})")
                else:
                    st.write("目前暫無最新訊息。")
                    
            except Exception as e:
                st.error(f"連線失敗: {e}")

st.divider()
st.caption("註：Yahoo Finance 提供的訊息整合了官方公告與財經新聞。")
