import streamlit as st
import requests
import pandas as pd
import urllib3

# 1. 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.title("電信三雄 & momo 重大訊息監控")

my_stocks = ["2412", "3045", "4904", "8454"]
api_url = "https://openapi.twse.com.tw/v1/opendata/t187ap04_L"

# 2. 幫程式碼「戴面具」：偽裝成 Chrome 瀏覽器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

if st.button('整理今日重大訊息'):
    with st.spinner('正在從證交所抓取資料...'):
        try:
            # 3. 加上 headers 重新抓取
            response = requests.get(api_url, headers=headers, verify=False, timeout=10)
            
            # 先檢查是否有內容
            if not response.text.strip():
                st.error("伺服器回傳了空的內容，可能是暫時連線不穩。")
            elif response.status_code == 200:
                # 嘗試讀取 JSON
                all_data = pd.DataFrame(response.json())
                
                # 過濾資料
                filtered_data = all_data[all_data['公司代號'].isin(my_stocks)]
                
                if not filtered_data.empty:
                    st.success(f"找到 {len(filtered_data)} 則相關訊息！")
                    display_cols = ['公司代號', '公司名稱', '發言日期', '發言時間', '主旨']
                    st.table(filtered_data[display_cols])
                else:
                    st.warning("今日這幾家公司目前尚無重大訊息公告。")
            else:
                st.error(f"連線失敗，錯誤代碼：{response.status_code}")
                
        except ValueError: # JSON 解析失敗會跳到這裡
            st.error("資料解析失敗：伺服器回傳的不是正確的資料格式。")
            # 顯示前 100 個字元幫助 debug
            st.code(response.text[:100], language='text')
        except Exception as e:
            st.error(f"發生非預期錯誤：{e}")
