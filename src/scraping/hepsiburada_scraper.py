# src/scraping/hepsiburada_scraper.py

from .base_scraper import BaseScraper
from ..utils.exceptions import ProductNameNotFoundError, PriceNotFoundError

class HepsiburadaScraper(BaseScraper):
    """Hepsiburada.com için veri kazıma işlemlerini gerçekleştirir."""

    def scrape(self) -> dict:
        soup = self.get_page_content()

        # Ürün Adını Bul
        # Hepsiburada'da ürün adı genellikle bir h1 etiketindedir.
        name_element = soup.find("h1", id="product-name")
        if not name_element:
            # Alternatif olarak, sayfa yapısı değişmişse data-testId kullanılabilir
            name_element = soup.find(attrs={'data-testId': 'product-name'})
            if not name_element:
                raise ProductNameNotFoundError("Hepsiburada: Ürün adı bulunamadı.")
        
        product_name = name_element.get_text(strip=True)

        # Fiyatı Bul
        # Fiyat genellikle özel bir id veya class içinde bulunur.
        price_element = soup.find(attrs={'data-testId': 'price-current-price'})
        if not price_element:
            raise PriceNotFoundError("Hepsiburada: Fiyat bulunamadı.")

        price_text = price_element.get_text(strip=True)
        product_price = self.clean_price(price_text)

        return {'name': product_name, 'price': product_price}