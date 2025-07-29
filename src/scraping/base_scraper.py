# src/scraping/base_scraper.py

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from ..utils.exceptions import ScraperError

class BaseScraper(ABC):
    """
    Tüm scraper sınıfları için temel arayüzü ve ortak işlevleri tanımlar.
    """
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        # Bot olarak algılanmamak için standart bir tarayıcı kimliği gönderiyoruz.
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_page_content(self) -> BeautifulSoup:
        """
        Belirtilen URL'nin HTML içeriğini çeker ve BeautifulSoup nesnesi olarak döndürür.
        """
        try:
            response = self.session.get(self.url, timeout=15)
            # HTTP 2xx dışında bir durum kodu varsa hata fırlatır (örn: 404, 503)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            raise ScraperError(f"URL'ye erişim sırasında bir ağ hatası oluştu: {e}")

    @staticmethod
    def clean_price(price_text: str) -> float:
        """
        '1.499,90 TL' gibi metinleri 1499.90 gibi bir float sayıya dönüştürür.
        """
        if not price_text:
            return 0.0
        
        # Para birimi, boşluklar ve binlik ayraçlarını temizle
        price_text = price_text.lower().replace('tl', '').replace('₺', '').strip()
        price_text = price_text.replace('.', '').replace(',', '.') # Önce binlik, sonra ondalık
        
        # Sadece sayısal karakterler ve nokta kalmalı
        valid_chars = "0123456789."
        cleaned_price = "".join(c for c in price_text if c in valid_chars)
        
        try:
            return float(cleaned_price)
        except (ValueError, TypeError):
            return 0.0

    @abstractmethod
    def scrape(self) -> dict:
        """
        Bu metot, her alt sınıf tarafından kendi sitesine özel olarak
        uygulanmalıdır. Ürün adı ve fiyatını kazımalıdır.
        :return: {'name': str, 'price': float} formatında bir sözlük.
        """
        pass