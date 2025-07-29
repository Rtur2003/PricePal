# src/scraping/scraper_factory.py (Kavramsal İskelet)
from .amazon_scraper import AmazonScraper
from .hepsiburada_scraper import HepsiburadaScraper
from ..utils.exceptions import UnsupportedSiteError

def get_scraper(url: str):
    """
    Verilen URL'ye göre uygun scraper nesnesini döndürür.
    """
    if "amazon.com.tr" in url:
        return AmazonScraper(url)
    elif "hepsiburada.com" in url:
        return HepsiburadaScraper(url)
    # ... gelecekte yeni siteler buraya eklenecek
    else:
        raise UnsupportedSiteError(f"'{url}' adresi desteklenmiyor.")