# src/scraping/base_scraper.py

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from ..utils.exceptions import ScraperError
import time # <-- BU SATIRI EKLEYİN

class BaseScraper(ABC):
    """
    Tüm scraper sınıfları için temel arayüzü ve ortak işlevleri tanımlar.
    """
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    # get_page_content METODUNU AŞAĞIDAKİ İLE DEĞİŞTİRİN
    def get_page_content(self) -> BeautifulSoup:
        """
        Belirtilen URL'nin HTML içeriğini çeker ve BeautifulSoup nesnesi olarak döndürür.
        Başarısız olursa birkaç kez tekrar dener.
        """
        retries = 3  # Toplam deneme hakkı
        timeout_seconds = 30 # Zaman aşımı süresini 30 saniyeye çıkardık

        for attempt in range(retries):
            try:
                print(f"  -> Sayfa içeriği getiriliyor (Deneme {attempt + 1}/{retries})...")
                response = self.session.get(self.url, timeout=timeout_seconds)
                response.raise_for_status() # HTTP 2xx dışında bir durum kodu varsa hata fırlatır
                return BeautifulSoup(response.content, 'html.parser')
            
            except requests.exceptions.RequestException as e:
                print(f"  -> Ağ hatası (Deneme {attempt + 1}): {e}")
                if attempt < retries - 1:
                    # Son deneme değilse, bir süre bekle ve tekrar dene
                    sleep_time = 5
                    print(f"  -> {sleep_time} saniye bekleniyor...")
                    time.sleep(sleep_time)
                else:
                    # Tüm denemeler başarısız olduysa, ana hatayı fırlat
                    raise ScraperError(f"Tüm denemelerden sonra URL'ye erişilemedi: {e}")

    @staticmethod
    def clean_price(price_text: str) -> float:
        """
        '1.499,90 TL' gibi metinleri 1499.90 gibi bir float sayıya dönüştürür.
        """
        # ... Bu metodun içeriği aynı kalacak ...
        if not price_text:
            return 0.0
        
        price_text = price_text.lower().replace('tl', '').replace('₺', '').strip()
        price_text = price_text.replace('.', '').replace(',', '.')
        
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