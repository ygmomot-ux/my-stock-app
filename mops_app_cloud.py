import streamlit as st
import yfinance as yf
import pandas as pd

st.title("電信三雄 & momo 訊息監控 (國際橋接版)")

# 股票代號清單 (Yahoo Finance 格式需要加 .TW)
tickers = {
    "2412.TW": "中華電信",
    "3045.TW": "台灣大哥大",
    "4904.TW": "遠傳電信",
    "2317.TW": "鴻海",
    "8454.TW": "富邦媒 (momo)"
}

st.info("💡 透過 Yahoo Finance 獲取數據，能避開政府網站對雲端 IP 的封鎖。")

if st.button('獲取最新重大訊息與新聞'):
    for symbol, name in tickers.items():
        st.subheader(f"【{symbol} {name}】")
        
        try:
            # 使用 yfinance 獲取股票物件
            stock = yf.Ticker(symbol)
            
            # 抓取新聞 (Yahoo 的新聞包含了官方重大訊息與媒體報導)
            news = stock.news
            
            if news:
                for item in news[:10]:  # 只顯示最新的 10 則
                    # 轉換時間戳記 (Optional)
                    with st.container():
                        st.markdown(f"**[{item['publisher']}]** {item['title']}")
                        st.caption(f"連結: [點此閱讀]({item['link']})")
                        st.divider()
            else:
                st.write("目前暫無最新訊息。")
                
        except Exception as e:
            st.error(f"抓取 {name} 時發生錯誤: {e}")

st.markdown("---")
st.caption("註：Yahoo Finance 提供的訊息整合了官方公告與財經新聞，適合日常監控。")
