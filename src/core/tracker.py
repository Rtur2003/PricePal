# src/core/tracker.py

from datetime import datetime
import sqlite3
from ..scraping.base_scraper import WebDriverManager
from ..database.db_manager import DBManager
from ..core.config_manager import ConfigManager
from ..scraping import scraper_factory
from ..notifications import email_sender
from ..utils.exceptions import ScraperError

def check_single_product(product: sqlite3.Row, db: DBManager, config: ConfigManager):
    """
    Tek bir ürünün fiyatını kontrol eder, veritabanını günceller ve
    gerekirse bildirim gönderir.
    """
    print(f"Kontrol ediliyor: {product['url'][:70]}...")
    update_data = {
        'last_check_date': datetime.now().isoformat()
    }

    try:
        # 1. Scraper'ı al ve veriyi çek
        scraper = scraper_factory.get_scraper(product['url'])
        scraped_data = scraper.scrape()
        current_price = scraped_data['price']

        # YENİ EKLENEN SATIR: Fiyat geçmişini kaydet
        if current_price > 0:
            db.add_price_history(product['id'], current_price)

        # Ürün adı ilk kez çekiliyorsa veya değişmişse güncelle
        if product['name'] is None or product['name'] != scraped_data['name']:
            update_data['name'] = scraped_data['name']
        
        update_data['current_price'] = current_price
        
        # 2. Fiyatı karşılaştır (Bu kısım aynı kalıyor)
        if current_price > 0 and current_price <= product['target_price']:
            print(f"  -> FİYAT DÜŞTÜ! Yeni Fiyat: {current_price} TL")
            update_data['status'] = 'PRICE_ALERT'
            
            # 3. Bildirim gönder
            user_email = config.get('user_email')
            password = config.get_email_password()
            smtp_host = config.get('smtp_host', 'smtp.gmail.com')
            smtp_port = int(config.get('smtp_port', 587))
            
            if email_sender.send_price_alert_email(
                sender_email=user_email, password=password, recipient_email=user_email,
                smtp_host=smtp_host, smtp_port=smtp_port,
                product_name=scraped_data['name'], new_price=current_price, product_url=product['url']
            ):
                # E-posta başarıyla gönderilirse, tekrar bildirim gitmemesi için takibi pasif yap
                update_data['is_active'] = 0
        else:
            print(f"  -> Fiyat hala yüksek: {current_price} TL")
            update_data['status'] = 'TRACKING'

    except ScraperError as e:
        print(f"  -> HATA (Scraper): {e}")
        update_data['status'] = 'ERROR'
    except Exception as e:
        print(f"  -> GENEL HATA: {e}")
        update_data['status'] = 'ERROR'
    
    finally:
        # 4. Veritabanını her durumda güncelle
        db.update_product(product['id'], update_data)

# src/core/tracker.py dosyasının en altına eklenecek YENİ fonksiyon


def run_all_active_product_checks():
    db = None
    try:
        print("Thread-uyumlu kontrol işlemi başlatılıyor...")
        db = DBManager()
        config = ConfigManager(db)
        products_to_check = db.get_active_products_for_check()
        if not products_to_check:
            print("Kontrol edilecek aktif ürün bulunamadı.")
            return

        for product in products_to_check:
            check_single_product(product, db, config)
    except Exception as e:
        print(f"run_all_active_product_checks içinde hata oluştu: {e}")
    finally:
        if db:
            db.close()
        # İŞLEM BİTTİĞİNDE TARAYICIYI KAPAT
        WebDriverManager.close_driver() 
        print("Thread-uyumlu kontrol işlemi bitti, kaynaklar serbest bırakıldı.")