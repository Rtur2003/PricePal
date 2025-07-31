# src/scraping/base_scraper.py (YENİ HALİ)

from abc import ABC, abstractmethod
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from ..utils.exceptions import ScraperError
from ..utils import constants   

class WebDriverManager:
    """
    Selenium WebDriver'ı tek bir örnek (singleton) olarak yönetir.
    Uygulama boyunca sadece bir tarayıcı penceresi açılmasını sağlar.
    """
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            print("WebDriver başlatılıyor...")
            options = Options()
            options.add_argument("--headless")  # Tarayıcıyı arayüz olmadan (arka planda) çalıştırır
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled") # Bot tespitini zorlaştırır
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument(f"user-agent={constants.DEFAULT_USER_AGENT}")
            options.add_argument('--log-level=3')   
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            # ---------------------
            try:
                service = ChromeService(ChromeDriverManager().install())
                cls._driver = webdriver.Chrome(service=service, options=options)
                cls._driver.set_page_load_timeout(45) # Sayfa yükleme zaman aşımını artırdık
                print("WebDriver başarıyla başlatıldı.")
            except Exception as e:
                print(f"WebDriver başlatılamadı: {e}")
                raise ScraperError(f"WebDriver başlatılamadı: {e}")
        return cls._driver

    @classmethod
    def close_driver(cls):
        if cls._driver is not None:
            print("WebDriver kapatılıyor...")
            cls._driver.quit()
            cls._driver = None
            print("WebDriver kapatıldı.")


class BaseScraper(ABC):
    """
    Tüm scraper sınıfları için Selenium tabanlı yeni temel arayüz.
    """
    def __init__(self, url: str):
        self.url = url
        self.driver = WebDriverManager.get_driver()

    def get_page_content(self) -> BeautifulSoup:
        """
        Belirtilen URL'nin HTML içeriğini Selenium ile çeker ve BeautifulSoup nesnesi olarak döndürür.
        """
        retries = 2
        for attempt in range(retries):
            try:
                print(f"  -> Sayfa yükleniyor (Deneme {attempt + 1}/{retries})...")
                self.driver.get(self.url)
                # Sayfanın dinamik içeriğinin yüklenmesi için bir süre bekleyelim
                time.sleep(5) 
                return BeautifulSoup(self.driver.page_source, 'html.parser')
            except Exception as e:
                print(f"  -> Sayfa yükleme hatası (Deneme {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    raise ScraperError(f"Tüm denemelerden sonra URL yüklenemedi: {self.url}")

    # ... clean_price metodu aynı kalıyor ...
    @staticmethod
    def clean_price(price_text: str) -> float:
        if not price_text: return 0.0
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
        pass