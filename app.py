import time
import pandas as pd
import requests
import streamlit as st

# 設定網頁標題與圖示
st.set_page_config(page_title="104 公司資料抓取工具", page_icon="🔍")


def fetch_104_company_info(cust_no):
    """根據 104 的公司代碼抓取詳細資料"""
    api_url = f"https://104.com.tw{cust_no}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://104.com.tw{cust_no}",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            return {
                "公司代碼": cust_no,
                "公司名稱": data.get("custName", "未提供"),
                "統一編號": data.get("invoiceNumber", "未提供"),
                "員工人數": data.get("empNo", "未提供"),
                "公司地址": (
                    f"{data.get('indcatRegionDesc', '')}{data.get('address', '')}"
                ),
                "聯絡人姓名": data.get("hrName", "未提供"),
                "聯絡電話": data.get("phone", "未提供"),
            }
    except Exception:
        pass
    return None


# 網頁視覺介面
st.title("🔍 104 網頁爬蟲資料抓取工具")
st.write("請在下方輸入 104 公司網址或公司代碼，系統將自動解析並提供 Excel 下載。")

# 區塊一：單筆或多筆輸入
input_data = st.text_area(
    "請輸入 104 公司網址或代碼（每行一筆）",
    placeholder="https://104.com.tw1a2x6bktd3\n1a2x6bktd3",
    height=150,
)

# 開始執行按鈕
if st.button("開始抓取資料", type="primary"):
    if not input_data.strip():
        st.warning("⚠️ 請先輸入網址或公司代碼！")
    else:
        # 解析使用者輸入的每一行
        lines = input_data.strip().split("\n")
        cust_nos = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 自動判斷是完整網址還是純代碼
            if "company/" in line:
                parts = line.split("company/")
                if len(parts) > 1:
                    # 移除網址後續可能帶有的參數（如 ?jobsource=...）
                    code = parts[1].split("?")[0].split("/")[0]
                    cust_nos.append(code)
            else:
                cust_nos.append(line)

        # 移除重複的代碼
        cust_nos = list(set(cust_nos))

        if not cust_nos:
            st.error("❌ 無法從輸入的內容中解析出有效的公司代碼。")
        else:
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            # 開始跑爬蟲迴圈
            for index, cust_no in enumerate(cust_nos):
                status_text.text(
                    f"正在抓取第 ({index+1}/{len(cust_nos)}) 筆代碼: {cust_no}..."
                )

                info = fetch_104_company_info(cust_no)
                if info:
                    results.append(info)
                else:
                    results.append(
                        {
                            "公司代碼": cust_no,
                            "公司名稱": "抓取失敗或代碼錯誤",
                            "統一編號": "-",
                            "員工人數": "-",
                            "公司地址": "-",
                            "聯絡人姓名": "-",
                            "聯絡電話": "-",
                        }
                    )

                # 更新進度條
                progress_bar.progress((index + 1) / len(cust_nos))

                # 批次抓取時防封鎖延遲
                if len(cust_nos) > 1 and index < len(cust_nos) - 1:
                    time.sleep(2)

            status_text.text("✨ 資料抓取完成！")

            # 將結果轉換為表格
            df = pd.DataFrame(results)

            # 在網頁上呈現資料表格
            st.subheader("📊 抓取結果預覽")
            st.dataframe(df)

            # 將資料轉換成 Excel 二進位檔供瀏覽器下載
            import io

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="公司資料")
            buffer.seek(0)

            # 顯示 Excel 下載按鈕
            st.download_button(
                label="📥 下載 Excel 檔案",
                data=buffer,
                file_name="104_company_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
