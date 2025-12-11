import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1. 忽略 SSL 警告 (這是解決紅色錯誤的關鍵)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 設定頁面與 CSS (Apple 風格) ---
st.set_page_config(page_title="重大訊息觀測站", layout="centered")

apple_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #F5F5F7;
        color: #1D1D1F;
    }
    h1 {
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #1D1D1F;
        padding-bottom: 20px;
    }
    .stDataFrame, .element-container, .stMarkdown {
        background: white;
        border-radius: 18px;
        padding: 2px;
    }
    .stTextInput input, .stNumberInput input {
        border-radius: 12px;
        border: 1px solid #D2D2D7;
        background-color: rgba(255, 255, 255, 0.8);
        padding: 10px;
    }
    .stButton > button {
        background-color: #0071E3;
        color: white;
        border-radius: 980px;
        padding: 10px 24px;
        font-size: 17px;
        font-weight: 500;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 113, 227, 0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #0077ED;
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(0, 113, 227, 0.3);
    }
    .result-card {
        background-color: #FFFFFF;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: translateY(-2px);
    }
    .stock-tag {
        background-color: #F2F2F7;
        color: #86868B;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    .news-title {
        font-size: 16px;
        font-weight: 600;
        color: #1D1D1F;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    .news-date {
        font-size: 12px;
        color: #86868B;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(apple_css, unsafe_allow_html=True)

# --- 爬蟲邏輯 (戰鬥版：Session + Retry) ---
def get_mops_data(co_id, days_back, debug=False):
    url = "https://mops.twse.com.tw/mops/web/ajax_t05st01"
    
    # 使用 Session 保持連線狀態，模擬真實使用者行為
    session = requests.Session()
    
    # 設定重試機制，防止網路瞬斷
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://mops.twse.com.tw/mops/web/t05st01',
        'Origin': 'https://mops.twse.com.tw',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    current_roc_year = end_date.year - 1911
    current_month = end_date.month
    
    months_to_query = [(current_roc_year, current_month)]
    if start_date.month != end_date.month:
        prev_month_date = end_date.replace(day=1) - timedelta(days=1)
        months_to_query.append((prev_month_date.year - 1911, prev_month_date.month))
    
    all_data = []

    for year, month in months_to_query:
        # 雙重掃描：上市(sii) 與 上櫃(otc)
        market_types = ['sii', 'otc'] 
        found_in_month = False 

        for mk_type in market_types:
            if found_in_month: 
                break 

            payload = {
                'encodeURIComponent': '1',
                'step': '1',
                'firstin': '1',
                'off': '1',
                'keyword4': '',
                'code1': '',
                'TYPEK': mk_type, 
                'checkbtn': '',
                'queryName': 'co_id',
                'inpuType': 'co_id',
                'TYPEK2': '',
                'co_id': co_id,
                'year': str(year),
                'month': str(month),
                'day': '' 
            }
            
            try:
                # 使用 session.post
                r = session.post(url, data=payload, headers=headers, timeout=15, verify=False)
                r.encoding = 'utf8'
                
                if debug:
                    st.text(f"[{co_id}] {year}/{month} ({mk_type}) -> HTTP {r.status_code}, Length: {len(r.text)}")
                    # 檢查是否被擋 IP 的特徵
                    if len(r.text) < 1000 or "Access Denied" in r.text:
                        st.error(f"⚠️ 警告：MOPS 可能正在封鎖此雲端主機 IP。")
                
                soup = BeautifulSoup(r.text, 'html.parser')
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 4:
                            date_str = cols[2].text.strip()
                            title = cols[4].text.strip()
                            name = cols[1].text.strip()
                            
                            if not name or "主旨" in title:
                                continue

                            try:
                                parts = date_str.split('/')
                                if len(parts) == 3:
                                    y, m, d = map(int, parts)
                                    msg_date = datetime(y + 1911, m, d)
                                    
                                    if start_date <= msg_date <= end_date:
                                        all_data.append({
                                            "Stock": co_id,
                                            "Name": name,
                                            "Date": date_str,
                                            "Title": title,
                                            "RawDate": msg_date 
                                        })
                                        found_in_month = True 
                            except ValueError:
                                continue 
                
                time.sleep(0.5) 
            except Exception as e:
                if debug:
                    st.error(f"連線錯誤: {e}")
                pass
            
    return all_data

# --- UI 佈局 ---

st.title("📊 重大訊息監控儀表板")
st.markdown("連線至公開資訊觀測站 (MOPS)，即時追蹤上市櫃公司動態。")

with st.sidebar:
    st.header("設定 Settings")
    
    st.warning("⚠️ **重要提示**：\n若搜尋結果為空，極可能是 MOPS 封鎖了雲端主機的 IP。\n\n**最終解決方案**：請下載此程式碼，在您自己的電腦上執行 (Local Run)，保證 100% 成功。")
    
    debug_mode = st.checkbox("開啟除錯模式 (Debug Mode)", value=False)
    
    st.subheader("搜尋範圍")
    days_lookback = st.number_input("往前抓取天數", min_value=1, max_value=90, value=7, step=1)
    
    st.subheader("額外股票代碼")
    extra_1 = st.text_input("代碼 1", placeholder="例如: 2330", max_chars=10)
    extra_2 = st.text_input("代碼 2", placeholder="例如: 2303", max_chars=10)
    extra_3 = st.text_input("代碼 3", placeholder="例如: 2603", max_chars=10)
    
    st.markdown("---")
    st.caption("資料來源: 公開資訊觀測站")

default_stocks = ['2412', '3045', '4904', '8454']
extra_stocks = [s for s in [extra_1, extra_2, extra_3] if s]
target_stocks = list(set(default_stocks + extra_stocks))

st.markdown(f"### 🎯 監控清單 ({len(target_stocks)} 家公司)")
st.write(f"目前追蹤: {', '.join(target_stocks)}")
st.write(f"日期範圍: 過去 {days_lookback} 天")

if st.button("開始搜尋", key="search_btn"):
    
    with st.spinner('正在連線至公開資訊觀測站抓取資料...'):
        all_results = []
        progress_bar = st.progress(0)
        
        for i, stock_id in enumerate(target_stocks):
            data = get_mops_data(stock_id, days_lookback, debug=debug_mode)
            all_results.extend(data)
            progress_bar.progress((i + 1) / len(target_stocks))
            
        progress_bar.empty()

    if not all_results:
        st.warning("在此日期範圍內查無重大訊息。")
        if not debug_mode:
            st.markdown("🔍 **沒看到資料？** 請嘗試在左側開啟「除錯模式」查看連線狀況。若顯示 `HTTP 200` 但無內容，代表被 MOPS 擋 IP 了。")
    else:
        all_results.sort(key=lambda x: x['RawDate'], reverse=True)
        st.success(f"搜尋完成！共找到 {len(all_results)} 筆資料。")
        
        for item in all_results:
            st.markdown(f"""
            <div class="result-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <span class="stock-tag">{item['Stock']} {item['Name']}</span>
                        <div class="news-title">{item['Title']}</div>
                    </div>
                    <div class="news-date" style="text-align: right; min-width: 80px;">
                        📅 {item['Date']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("查看詳細數據表格"):
            df = pd.DataFrame(all_results)
            if not df.empty:
                df = df.drop_duplicates(subset=['Stock', 'Date', 'Title'])
                df_display = df.drop(columns=['RawDate'])
                st.dataframe(df_display, use_container_width=True)
