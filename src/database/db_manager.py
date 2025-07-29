# src/database/db_manager.py

import sqlite3
from pathlib import Path
from datetime import datetime

class DBManager:
    """
    SQLite veritabanı ile ilgili tüm işlemleri yöneten sınıf.
    (CRUD: Create, Read, Update, Delete)
    """

    def __init__(self, db_name="pricepal.db"):
        """
        Veritabanı bağlantısını başlatır ve tabloların var olduğundan emin olur.
        """
        # Projenin ana dizininde veritabanı dosyasını oluşturur
        self.db_path = Path(__file__).parent.parent.parent / db_name
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Sütunlara isimleriyle erişim imkanı sağlar (örn: row['name'])
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.setup_database()
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            raise

    def setup_database(self):
        """
        schema.sql dosyasını okur ve veritabanı şemasını (tabloları) oluşturur.
        """
        try:
            schema_path = Path(__file__).parent / "schema.sql"
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            self.cursor.executescript(sql_script)
            self.conn.commit()
        except FileNotFoundError:
            print(f"HATA: '{schema_path}' bulunamadı. Tablolar oluşturulamadı.")
        except sqlite3.Error as e:
            print(f"Veritabanı kurulum hatası: {e}")

    # --- Ürün Fonksiyonları ---

    def add_product(self, url: str, target_price: float, site: str) -> int:
        """
        Veritabanına yeni bir ürün ekler.
        :return: Eklenen ürünün ID'si.
        """
        sql = """
            INSERT INTO products (url, target_price, site, added_date, status)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            added_date = datetime.now().isoformat()
            self.cursor.execute(sql, (url, target_price, site, added_date, 'PENDING'))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Hata: Bu URL ({url}) zaten takip ediliyor.")
            return None

    def update_product(self, product_id: int, data: dict):
        """
        Belirtilen ID'ye sahip ürünün bilgilerini günceller.
        :param product_id: Güncellenecek ürünün ID'si.
        :param data: {'sütun_adı': yeni_değer} formatında bir sözlük.
        """
        if not data:
            return

        fields = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(product_id)

        sql = f"UPDATE products SET {fields} WHERE id = ?"
        self.cursor.execute(sql, values)
        self.conn.commit()

    def delete_product(self, product_id: int):
        """Bir ürünü ID'sine göre siler."""
        sql = "DELETE FROM products WHERE id = ?"
        self.cursor.execute(sql, (product_id,))
        self.conn.commit()

    def get_all_products(self) -> list[sqlite3.Row]:
        """Tüm ürünleri listeler."""
        sql = "SELECT * FROM products ORDER BY added_date DESC"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_active_products_for_check(self) -> list[sqlite3.Row]:
        """Sadece takibi aktif olan ürünleri listeler."""
        sql = "SELECT * FROM products WHERE is_active = 1"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_product_by_id(self, product_id: int) -> sqlite3.Row | None:
        """Tek bir ürünü ID'sine göre getirir."""
        sql = "SELECT * FROM products WHERE id = ?"
        self.cursor.execute(sql, (product_id,))
        return self.cursor.fetchone()

    # --- Ayar Fonksiyonları ---

    def get_setting(self, key: str) -> str | None:
        """Ayarlar tablosundan bir değeri okur."""
        sql = "SELECT value FROM settings WHERE key = ?"
        self.cursor.execute(sql, (key,))
        row = self.cursor.fetchone()
        return row['value'] if row else None

    def set_setting(self, key: str, value: str):
        """Ayarlar tablosuna bir değeri yazar veya günceller."""
        sql = "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)"
        self.cursor.execute(sql, (key, value))
        self.conn.commit()

    def close(self):
        """Veritabanı bağlantısını güvenli bir şekilde kapatır."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Nesne silindiğinde bağlantının kapandığından emin olur."""
        self.close()