import streamlit as st
import pandas as pd
import plotly.express as px
import socket
import qrcode
from PIL import Image
import io

# 1. 取得本機 IP 地址的函數 (備用)
@st.cache_data
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# 2. 建立所有連線共用的全域變數
@st.cache_resource
def get_global_votes():
    return {"立體綠廊": 0, "平面綠園道": 0}

votes = get_global_votes()

st.set_page_config(page_title="綠園道設計民意調查", page_icon="🗳️", layout="centered")

st.title("🗳️ 台南綠園道設計：民意模擬投票")
st.markdown("這是一個讓課堂同學們共同參與的即時投票系統！")

# 3. 投票按鈕介面 (學生只看得到這裡)
st.markdown("### 請選擇您支持的設計方案：")
col1, col2 = st.columns(2)

with col1:
    if st.button("🌟 支持【立體綠廊】", use_container_width=True):
        votes["立體綠廊"] += 1
        st.success("投票成功！您投給了「立體綠廊」")
        st.balloons()

with col2:
    if st.button("🌳 支持【平面綠園道】", use_container_width=True):
        votes["平面綠園道"] += 1
        st.success("投票成功！您投給了「平面綠園道」")
        st.snow()

# 4. 管理員介面與結果顯示 (側邊欄登入)
st.sidebar.title("👨‍🏫 管理員介面")
admin_password = st.sidebar.text_input("請輸入管理員密碼", type="password")

if admin_password == "admin123":
    st.sidebar.success("登入成功！")
    
    # QR Code 產生器
    st.sidebar.markdown("---")
    st.sidebar.subheader("📱 產生 QR Code")
    st.sidebar.markdown("請將 `localtunnel` 產生的公開網址貼在下方，系統會自動轉換為 QR Code 供學生掃描。")
    public_url = st.sidebar.text_input("請貼上公開網址:", "")
    if public_url:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(public_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.sidebar.image(buf, caption="請學生掃描此 QR Code 投票", use_container_width=True)

    # 管理功能
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 系統管理")
    if st.sidebar.button("⚠️ 重設所有投票數據 (歸零)"):
        votes["立體綠廊"] = 0
        votes["平面綠園道"] = 0
        st.rerun()

    # 顯示投票結果
    st.divider()
    st.subheader("📊 投票結果 (僅管理員可見)")
    total_votes = sum(votes.values())
    
    col_title, col_refresh = st.columns([3, 1])
    with col_title:
        st.markdown(f"**目前總票數：{total_votes} 票**")
    with col_refresh:
        if st.button("🔄 即時更新結果"):
            st.rerun()

    if total_votes > 0:
        df = pd.DataFrame({
            "方案": list(votes.keys()),
            "票數": list(votes.values())
        })
        df['百分比'] = (df['票數'] / total_votes * 100).round(1)
        
        fig = px.pie(df, values='票數', names='方案', 
                     title="方案支持度分佈",
                     color_discrete_sequence=['#4C78A8', '#72B7B2'],
                     hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label', 
                          hovertemplate='<b>%{label}</b><br>票數: %{value}<br>比例: %{percent}')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**詳細數據：**")
        st.dataframe(df.style.format({'百分比': '{:.1f}%'}), use_container_width=True, hide_index=True)
    else:
        st.info("目前尚無投開票紀錄。")
else:
    st.sidebar.warning("請輸入正確密碼以解鎖結果與管理功能。")
