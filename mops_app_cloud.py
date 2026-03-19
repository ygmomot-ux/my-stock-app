import streamlit as st
import requests
import pandas as pd

# 設定網頁標題
st.title("電信三雄 & momo 重大訊息監控")

# 你的目標股票清單
my_stocks = ["2412", "3045", "4904", "8454", "2330", "2317"]

# 1. API 網址 (上市公司每日重大訊息)
api_url = "https://openapi.twse.com.tw/v1/opendata/t187ap04_L"

if st.button('整理今日重大訊息'):
    with st.spinner('正在從證交所抓取資料...'):
        # 2. 發送請求 (像服務生一樣去廚房拿菜)
        response = requests.get(api_url)
        
        if response.status_code == 200:
            # 3. 把抓到的資料變成表格 (DataFrame)
            all_data = pd.DataFrame(response.json())
            
            # 4. 過濾出你想要的股票 (欄位名稱通常是 '公司代號')
            # 注意：API 回傳的代號可能是字串，我們確保比對正確
            filtered_data = all_data[all_data['公司代號'].isin(my_stocks)]
            
            if not filtered_data.empty:
                st.success(f"找到 {len(filtered_data)} 則相關訊息！")
                # 5. 顯示結果：只顯示我們想看的欄位
                display_cols = ['公司代號', '公司名稱', '發言日期', '發言時間', '主旨']
                st.table(filtered_data[display_cols])
            else:
                st.warning("今日這幾家公司目前尚無重大訊息公告。")
        else:
            st.error("連線到證交所 API 失敗，請稍後再試。")
