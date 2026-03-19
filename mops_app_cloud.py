import streamlit as st
import yfinance as yf

st.set_page_config(page_title="電信股監控", layout="wide")
st.title("電信三雄 & 權值股 訊息監控 (偵錯增強版)")

tickers = {
    "2412.TW": "中華電信",
    "3045.TW": "台灣大哥大",
    "4904.TW": "遠傳電信",
    "2317.TW": "鴻海",
    "8454.TW": "富邦媒"
}

if st.button('開始抓取並偵測資料格式'):
    cols = st.columns(len(tickers))
    
    for i, (symbol, name) in enumerate(tickers.items()):
        with cols[i]:
            st.subheader(name)
            try:
                stock = yf.Ticker(symbol)
                news = stock.news
                
                if news:
                    for item in news[:3]:
                        # --- 關鍵修正：嘗試多種可能的欄位名稱 ---
                        # 標題可能是 'title' 或 'content' 或 'summary'
                        title = item.get('title') or item.get('content', {}).get('title') or "無法取得標題"
                        
                        # 連結可能是 'link' 或 'url'
                        link = item.get('link') or item.get('url') or "#"
                        
                        # 來源可能是 'publisher' 或 'source'
                        pub = item.get('publisher') or item.get('source', '未知來源')

                        # 顯示新聞
                        with st.expander(title[:20] + "..." if title else "展開查看"):
                            st.write(f"完整標題: {title}")
                            st.write(f"來源: {pub}")
                            if link != "#":
                                st.link_button("👉 點此閱讀全文", link)
                            else:
                                st.warning("此訊息暫無外部連結")
                                
                        # --- 調試用：如果還是無標題，印出原始資料結構看看 ---
                        if title == "無法取得標題":
                            st.caption("偵錯資訊 (Raw Data):")
                            st.json(item)
                else:
                    st.write("目前無新聞")
            except Exception as e:
                st.error(f"錯誤: {e}")

st.divider()
st.info("💡 如果依然顯示『無法取得標題』，請查看下方的 JSON 框，那裡面藏著真正的欄位名稱。")
