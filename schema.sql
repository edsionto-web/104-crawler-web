CREATE TABLE IF NOT EXISTS company_info (
    id SERIAL PRIMARY KEY,
    cust_no VARCHAR(50) UNIQUE,        -- 公司代碼（唯一值，避免重複寫入）
    company_name VARCHAR(255),         -- 公司名稱
    invoice_number VARCHAR(50),        -- 統一編號
    employee_count VARCHAR(50),        -- 員工人數
    address TEXT,                      -- 公司地址
    contact_name VARCHAR(100),         -- 聯絡人姓名
    contact_phone VARCHAR(100),        -- 聯絡電話
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() -- 抓取時間
);
