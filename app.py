import os
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="104 企業資料庫管理系統", page_icon="🗄️")

# 讀取 Streamlit 的 Secrets 設定
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

st.title("🗄️ 104 企業歷史資料庫")
st.write("此網頁與雲端資料庫同步，展示 GitHub Actions 每日定時抓取的最新資料。")


def load_data_from_supabase():
    """從資料庫撈取所有資料"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ 尚未設定資料庫連線變數！")
        return pd.DataFrame()

    # 排序：依據最後更新時間由新到舊
    url = f"{SUPABASE_URL}/rest/v1/company_info?select=*&order=updated_at.desc"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return pd.DataFrame(res.json())
    except Exception as e:
        st.error(f"資料庫讀取失敗: {e}")
    return pd.DataFrame()


# 載入並呈現資料
df = load_data_from_supabase()

if not df.empty:
    # 調整欄位名稱讓網頁更好看
    df_show = df.rename(
        columns={
            "company_name": "公司名稱",
            "invoice_number": "統一編號",
            "employee_count": "員工人數",
            "address": "公司地址",
            "contact_name": "聯絡人姓名",
            "contact_phone": "聯絡電話",
            "updated_at": "最後更新時間",
        }
    )

    # 隱藏不需要展示的資料庫 ID 與代碼
    df_show = df_show.drop(columns=["id", "cust_no"], errors="ignore")

    st.subheader(f"📊 目前資料庫總計: {len(df_show)} 筆公司資料")
    st.dataframe(df_show, use_container_width=True)

    # Excel 下載功能
    import io

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_show.to_excel(writer, index=False, sheet_name="104定時備份")
    buffer.seek(0)

    st.download_button(
        label="📥 下載完整資料庫 Excel",
        data=buffer,
        file_name="104_database_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("💡 目前資料庫尚無資料，請等待定時任務執行，或檢查連線設定。")
