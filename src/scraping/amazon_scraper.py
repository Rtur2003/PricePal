# src/scraping/amazon_scraper.py

from .base_scraper import BaseScraper
from ..utils.exceptions import ProductNameNotFoundError, PriceNotFoundError

class AmazonScraper(BaseScraper):
    """Amazon.com.tr için veri kazıma işlemlerini gerçekleştirir."""

    def scrape(self) -> dict:
        soup = self.get_page_content()

        # Ürün Adını Bul
        name_element = soup.find("span", id="productTitle")
        if not name_element:
            raise ProductNameNotFoundError("Amazon: Ürün adı bulunamadı. (id='productTitle')")
        product_name = name_element.get_text(strip=True)

        # Fiyatı Bul (Amazon'da fiyat birkaç farklı yapıda olabilir)
        price_element = soup.select_one('span.a-price-whole')
        price_fraction_element = soup.select_one('span.a-price-fraction')

        if not price_element or not price_fraction_element:
             # Bazen fiyat farklı bir yapıda olabilir
            price_element = soup.select_one('span.a-offscreen')
            if not price_element:
                raise PriceNotFoundError("Amazon: Fiyat bulunamadı.")
            price_text = price_element.get_text(strip=True)
        else:
            price_text = f"{price_element.get_text(strip=True)}{price_fraction_element.get_text(strip=True)}"

        product_price = self.clean_price(price_text)
        
        return {'name': product_name, 'price': product_price}