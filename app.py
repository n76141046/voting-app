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

# 2. 建立所有連線共用的全域變數 (改為陣列紀錄每一筆評分)
@st.cache_resource
def get_global_votes():
    return []

votes_record = get_global_votes()

st.set_page_config(page_title="綠園道設計民意調查", page_icon="🗳️", layout="centered")

st.title("🗳️ 台南綠園道設計：民意模擬投票")
st.markdown("這是一個讓課堂同學們共同參與的即時投票與回饋系統！")

# 3. 投票介面 (學生只看得到這裡)
st.markdown("### 📝 請填寫您的回饋與評分：")

with st.form("vote_form"):
    st.markdown("#### 1. 您對本方案的理解程度？")
    score_understand = st.slider("🧠 理解程度 (1非常不了解 ~ 5非常了解)", min_value=1, max_value=5, value=3, step=1)
    
    st.markdown("#### 2. 請為以下立場給分 (1~5分)：")
    score_support = st.slider("🌟 支持立體綠廊", min_value=1, max_value=5, value=3, step=1)
    score_unsupport = st.slider("❌ 不支持立體綠廊", min_value=1, max_value=5, value=3, step=1)
    
    st.markdown("#### 3. 您的意見與回饋：")
    comment = st.text_area("寫下您的看法 (自由選填，最多50字)：", max_chars=50)
    
    submitted = st.form_submit_button("送出評分", use_container_width=True)
    
    if submitted:
        # 將紀錄加入全域變數
        votes_record.append({
            "理解程度": score_understand,
            "支持立體綠廊": score_support,
            "不支持立體綠廊": score_unsupport,
            "意見": comment
        })
        st.success("🎉 評分送出成功！感謝您的參與。")
        st.balloons()

# 4. 管理員介面與結果顯示 (側邊欄登入)
st.sidebar.title("👨‍🏫 管理員介面")
admin_password = st.sidebar.text_input("請輸入管理員密碼", type="password")

if admin_password == "admin123":
    st.sidebar.success("登入成功！")
    
    # QR Code 產生器
    st.sidebar.markdown("---")
    st.sidebar.subheader("📱 產生 QR Code")
    st.sidebar.markdown("請將公開網址貼在下方，系統會自動轉換為 QR Code 供學生掃描。")
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
    if st.sidebar.button("⚠️ 重設所有評分數據 (歸零)"):
        votes_record.clear() # 清空陣列
        st.rerun()

    # 顯示投票結果
    st.divider()
    st.subheader("📊 評分結果與意見回饋 (僅管理員可見)")
    total_votes = len(votes_record)
    
    col_title, col_refresh = st.columns([3, 1])
    with col_title:
        st.markdown(f"**目前總參與人數：{total_votes} 人**")
    with col_refresh:
        if st.button("🔄 即時更新結果"):
            st.rerun()

    if total_votes > 0:
        df = pd.DataFrame(votes_record)
        
        # 繪製圓餅圖 (比較 支持 vs 不支持 的總分比例)
        total_support = df["支持立體綠廊"].sum()
        total_unsupport = df["不支持立體綠廊"].sum()
        
        df_pie = pd.DataFrame({
            "選項": ["支持立體綠廊", "不支持立體綠廊"],
            "總得分": [total_support, total_unsupport]
        })
        
        fig = px.pie(df_pie, values='總得分', names='選項', 
                     title="全班支持度比例 (依給分總和計算)",
                     color_discrete_sequence=['#4C78A8', '#E15759'],
                     hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label', 
                          hovertemplate='<b>%{label}</b><br>總分: %{value}<br>比例: %{percent}')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"*(註：全班平均理解程度為 **{df['理解程度'].mean():.1f}** 分)*")

        # 顯示所有意見與評分明細
        st.markdown("### 📝 詳細意見與評分紀錄")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("目前尚無投開票紀錄。")
else:
    st.sidebar.warning("請輸入正確密碼以解鎖結果與管理功能。")
