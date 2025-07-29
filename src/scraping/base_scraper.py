# src/scraping/base_scraper.py (Kavramsal İskelet)
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, url):
        self.url = url
        # User-Agent gibi ortak başlıkları burada tanımla
        self.headers = {'User-Agent': 'PricePal/1.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    @abstractmethod
    def scrape_price(self) -> float:
        # Bu metot, alt sınıflar tarafından mutlaka yazılmalıdır.
        # Sayfadan fiyatı çekip float olarak döndürmelidir.
        pass

    @abstractmethod
    def scrape_product_name(self) -> str:
        # Bu metot, alt sınıflar tarafından mutlaka yazılmalıdır.
        # Sayfadan ürün adını çekip string olarak döndürmelidir.
        pass

    def get_data(self) -> dict:
        # Tüm scraper'lar için ortak çalışacak metot
        # scrape_price ve scrape_product_name'i çağırır ve bir sözlük döndürür.
        # Hata yönetimi (try-except) burada yapılabilir.
        return {
            "name": self.scrape_product_name(),
            "price": self.scrape_price(),
            "currency": "TL" # Şimdilik sabit, ileride dinamik olabilir
        }