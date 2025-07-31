# src/scraping/hepsiburada_scraper.py (YENİ VE GÜVENİLİR HALİ)

import json
from .base_scraper import BaseScraper
from ..utils.exceptions import ProductNameNotFoundError, PriceNotFoundError, ScraperError

class HepsiburadaScraper(BaseScraper):
    """
    Hepsiburada.com için veri kazıma işlemlerini, sayfa içine gömülü
    JSON verisini okuyarak gerçekleştirir. Bu yöntem, HTML değişikliklerine
    karşı daha dayanıklıdır.
    """

    def scrape(self) -> dict:
        soup = self.get_page_content()

        # 1. Sayfa içindeki veri bloğunu (JSON) içeren script etiketini bul.
        # Bu etiket genellikle "reduxStore" veya benzeri bir ID'ye sahiptir.
        script_tag = soup.find("script", id="reduxStore")

        if not script_tag:
            raise ScraperError("Hepsiburada: Ürün verisini içeren 'reduxStore' script'i bulunamadı.")

        # 2. Script içeriğini JSON olarak ayrıştır.
        try:
            data = json.loads(script_tag.string)
        except json.JSONDecodeError:
            raise ScraperError("Hepsiburada: 'reduxStore' içeriği JSON formatında değil.")

        # 3. JSON verisi içinden ürün adını ve fiyatını al.
        # Bu anahtarlar sitenin veri yapısına göre değişebilir.
        try:
            product_data = data.get('productState', {}).get('product', {})
            
            product_name = product_data.get('name')
            if not product_name:
                raise ProductNameNotFoundError("Hepsiburada: JSON verisi içinde ürün adı ('name') bulunamadı.")

            prices = product_data.get('prices', [])
            if not prices:
                raise PriceNotFoundError("Hepsiburada: JSON verisi içinde fiyat bilgisi ('prices') bulunamadı.")
            
            # Fiyat genellikle bir liste içinde ilk elemandır.
            product_price = prices[0].get('value')
            if product_price is None:
                raise PriceNotFoundError("Hepsiburada: JSON verisi içinde fiyat değeri ('value') bulunamadı.")

            print(f"  -> JSON'dan bulundu: '{product_name[:30]}...', Fiyat: {product_price}")
            
            # Fiyatı float'a çeviriyoruz, zaten sayısal olduğu için clean_price'a gerek yok.
            return {'name': product_name, 'price': float(product_price)}

        except (KeyError, IndexError, TypeError) as e:
            raise ScraperError(f"Hepsiburada: JSON veri yapısı beklenenden farklı, anahtar hatası: {e}")