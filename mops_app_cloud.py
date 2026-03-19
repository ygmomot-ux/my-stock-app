import streamlit as st
import requests
import pandas as pd
import urllib3

# 關閉 SSL 警告訊息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.title("電信三雄 & momo 重大訊息監控")

my_stocks = ["2412", "3045", "4904", "8454"]
api_url = "https://openapi.twse.com.tw/v1/opendata/t187ap04_L"

if st.button('整理今日重大訊息'):
    with st.spinner('正在從證交所抓取資料...'):
        try:
            # 加入 verify=False 繞過憑證檢查
            response = requests.get(api_url, verify=False)
            
            if response.status_code == 200:
                all_data = pd.DataFrame(response.json())
                filtered_data = all_data[all_data['公司代號'].isin(my_stocks)]
                
                if not filtered_data.empty:
                    st.success(f"找到 {len(filtered_data)} 則相關訊息！")
                    display_cols = ['公司代號', '公司名稱', '發言日期', '發言時間', '主旨']
                    st.table(filtered_data[display_cols])
                else:
                    st.warning("今日這幾家公司目前尚無重大訊息公告。")
            else:
                st.error(f"連線失敗，錯誤代碼：{response.status_code}")
        except Exception as e:
            st.error(f"發生錯誤：{e}")
