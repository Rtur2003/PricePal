-- database/schema.sql

-- Takip edilen ürünleri saklayan ana tablo
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    name TEXT,
    target_price REAL NOT NULL,
    current_price REAL,
    currency TEXT,
    site TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    status TEXT DEFAULT 'PENDING', -- PENDING, TRACKING, PRICE_ALERT, ERROR
    last_check_date TEXT,
    added_date TEXT NOT NULL
);

-- Uygulama ayarlarını saklayan tablo
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- İlk ayarları ekleyelim (varsa)
INSERT OR IGNORE INTO settings (key, value) VALUES ('language', 'tr');
INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'litera'); -- ttkbootstrap teması
INSERT OR IGNORE INTO settings (key, value) VALUES ('user_email', '');
INSERT OR IGNORE INTO settings (key, value) VALUES ('smtp_host', 'smtp.gmail.com');
INSERT OR IGNORE INTO settings (key, value) VALUES ('smtp_port', '587');


-- Her ürünün fiyat geçmişini tutan tablo
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    price REAL NOT NULL,
    check_date TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);