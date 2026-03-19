import streamlit as st
import pandas as pd
import requests
import io

st.title("電信三雄 & momo 重大訊息 (穩定版)")

# 1. 改用政府開放平台提供的 CSV 資源連結 (通常比較不會檔 IP)
# 這是上市公司重大訊息的 CSV 接口
csv_url = "https://openapi.twse.com.tw/v1/opendata/t187ap04_L"

my_stocks = ["2412", "3045", "4904", "8454"]

if st.button('抓取今日公告'):
    with st.spinner('嘗試從開放平台通道抓取...'):
        try:
            # 2. 我們不抓 JSON 了，改抓原始內容並嘗試解析
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(csv_url, headers=headers, verify=False, timeout=15)
            
            # 3. 檢查抓到的到底是 JSON 還是被擋掉的 HTML
            content_type = response.headers.get('Content-Type', '')
            
            if 'html' in content_type.lower():
                st.error("❌ 警告：伺服器還是給了網頁而不是數據。")
                st.info("這代表該 API 目前對雲端 IP 限制極嚴。")
            else:
                # 試著讀取 JSON (因為這個 URL 原則上回傳 JSON)
                df = pd.DataFrame(response.json())
                
                # 過濾代號
                df['公司代號'] = df['公司代號'].astype(str)
                result = df[df['公司代號'].isin(my_stocks)]
                
                if not result.empty:
                    st.success(f"成功找到 {len(result)} 則訊息！")
                    st.dataframe(result[['公司代號', '公司名稱', '發言日期', '主旨']])
                else:
                    st.warning("今日名單內的公司尚無公告。")
                    
        except Exception as e:
            st.error(f"連線異常：{e}")
            st.info("這通常是伺服器拒絕了雲端主機的連線。")

# 4. 備案：如果還是被擋，提供手動查看連結
st.markdown("---")
st.caption("如果自動抓取失效，代表伺服器目前封鎖了 Streamlit IP。")
st.link_button("前往觀測站手動查看", "https://mops.twse.com.tw/mops/web/t05sr01_1")
