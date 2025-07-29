# src/utils/exceptions.py

class ScraperError(Exception):
    """
    Web scraping (veri kazıma) işlemi sırasında genel bir hata oluştuğunda
    tetiklenir. Tüm diğer scraper hatalarının temel sınıfıdır.
    """
    pass

class PriceNotFoundError(ScraperError):
    """
    Bir web sayfasının HTML'i içinde ürün fiyatını içeren etiket
    bulunamadığında tetiklenir.
    """
    pass

class ProductNameNotFoundError(ScraperError):
    """
    Bir web sayfasının HTML'i içinde ürün adını içeren etiket
    bulunamadığında tetiklenir.
    """
    pass

class UnsupportedSiteError(Exception):
    """
    Takip edilmeye çalışılan URL'nin, sistem tarafından desteklenmeyen
    bir web sitesine ait olması durumunda tetiklenir.
    """
    pass