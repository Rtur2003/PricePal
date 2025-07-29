# background_checker.py

import time
from src.database.db_manager import DBManager
from src.core.config_manager import ConfigManager
from src.core.tracker import check_single_product

def run_checks():
    """
    Veritabanındaki tüm aktif ürünleri döngüye alarak fiyatlarını kontrol eder.
    """
    print("="*50)
    print(f"Arka Plan Fiyat Kontrolü Başladı - {time.ctime()}")
    print("="*50)

    db = None
    try:
        db = DBManager()
        config = ConfigManager(db)

        active_products = db.get_active_products_for_check()

        if not active_products:
            print("Takip edilen aktif ürün bulunmuyor.")
            return

        print(f"Kontrol edilecek {len(active_products)} adet aktif ürün bulundu.")
        for product in active_products:
            check_single_product(product, db, config)
            # Web sitelerine karşı nazik olmak ve engellenmemek için istekler arasına bir bekleme koyuyoruz.
            time.sleep(5) 
        
    except Exception as e:
        print(f"Arka plan denetleyicisinde beklenmedik bir hata oluştu: {e}")
    finally:
        if db:
            db.close()
        print("\nFiyat kontrolü tamamlandı.")
        print("="*50)


if __name__ == "__main__":
    run_checks()