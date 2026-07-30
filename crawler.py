import os
import time
import requests

# 嘗試讀取雲端環境變數 (本地測試若沒有會報錯，需手動填入)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# 這裡填入您想要「定時追蹤/更新」的公司 104 代碼清單
TARGET_COMPANIES = ["1a2x6bktd3", "2b3y7cmue4"]


def fetch_104_company(cust_no):
    """抓取 104 公司資料"""
    api_url = f"https://104.com.tw{cust_no}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://104.com.tw{cust_no}",
        "Accept": "application/json",
    }
    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code == 200:
            d = res.json().get("data", {})
            return {
                "cust_no": cust_no,
                "company_name": d.get("custName", "未提供"),
                "invoice_number": d.get("invoiceNumber", "未提供"),
                "employee_count": d.get("empNo", "未提供"),
                "address": (
                    f"{d.get('indcatRegionDesc', '')}{d.get('address', '')}"
                ),
                "contact_name": d.get("hrName", "未提供"),
                "contact_phone": d.get("phone", "未提供"),
            }
    except Exception as e:
        print(f"抓取 {cust_no} 失敗: {e}")
    return None


def save_to_supabase(data):
    """將資料寫入 Supabase (使用 Upsert 語法：若代碼已存在則更新，不存在則新增)"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("錯誤：找不到 Supabase 設定，無法寫入資料庫。")
        return

    url = f"{SUPABASE_URL}/rest/v1/company_info"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",  # 遇重複代碼時覆蓋更新
    }

    try:
        res = requests.post(url, json=data, headers=headers)
        if res.status_code in:
            print(f"成功寫入資料庫: {data['company_name']}")
        else:
            print(f"寫入資料庫失敗: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"資料庫連線錯誤: {e}")


if __name__ == "__main__":
    print("🚀 定時爬蟲任務開始...")
    for cust_no in TARGET_COMPANIES:
        info = fetch_104_company(cust_no)
        if info:
            save_to_supabase(info)
        time.sleep(3)  # 每次間隔 3 秒防封鎖
    print("✨ 所有任務執行完畢。")
