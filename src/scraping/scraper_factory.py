# src/scraping/scraper_factory.py

from .base_scraper import BaseScraper
from .amazon_scraper import AmazonScraper
from .hepsiburada_scraper import HepsiburadaScraper
from ..utils.exceptions import UnsupportedSiteError

def get_scraper(url: str) -> BaseScraper:
    """
    Verilen URL'nin domain'ine göre uygun Scraper sınıfını döndürür.

    :param url: Ürünün web adresi.
    :raises UnsupportedSiteError: Eğer URL desteklenen sitelerden birine ait değilse.
    :return: URL için uygun olan BaseScraper alt sınıfının bir örneği.
    """
    url_low = url.lower()

    if "amazon.com.tr" in url_low:
        return AmazonScraper(url)
    elif "hepsiburada.com" in url_low:
        return HepsiburadaScraper(url)
    # Gelecekte yeni siteler için buraya 'elif' blokları eklenecek
    # elif "trendyol.com" in url_low:
    #     return TrendyolScraper(url)
    
    else:
        raise UnsupportedSiteError(f"'{url}' adresine sahip site desteklenmiyor.")