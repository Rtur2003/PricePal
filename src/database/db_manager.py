# src/database/db_manager.py (Kavramsal İskelet)
import sqlite3

class DBManager:
    def __init__(self, db_path='database.db'):
        # Veritabanı bağlantısını kurar
        pass

    def setup_database(self):
        # schema.sql dosyasını okur ve tabloları oluşturur
        pass

    # --- Ürün Fonksiyonları (CRUD) ---
    def add_product(self, url, target_price, site):
        # Yeni bir ürün ekler
        pass

    def update_product(self, product_id, data: dict):
        # Bir ürünün bilgilerini günceller (örn: current_price, status)
        pass

    def delete_product(self, product_id):
        # Bir ürünü siler
        pass

    def get_all_products(self):
        # Arayüzde göstermek için tüm ürünleri döner
        pass

    def get_active_products_for_check(self):
        # Arka plan denetleyicisinin kontrol edeceği aktif ürünleri döner
        pass

    # --- Ayar Fonksiyonları ---
    def get_setting(self, key):
        # Belirli bir ayarı döner
        pass

    def set_setting(self, key, value):
        # Bir ayarı kaydeder veya günceller
        pass