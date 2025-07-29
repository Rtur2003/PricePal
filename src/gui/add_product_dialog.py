# src/gui/add_product_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
import threading
from ..database.db_manager import DBManager
from ..scraping import scraper_factory
from ..utils.exceptions import ScraperError

class AddProductDialog(ttkb.Toplevel):
    def __init__(self, parent, db: DBManager, callback, product_id=None):
        super().__init__(parent)
        self.db = db
        self.callback = callback
        self.product_id = product_id
        
        self.title("Yeni Ürün Ekle" if not product_id else "Ürünü Düzenle")
        self.geometry("600x250")
        self.transient(parent)

        self._create_widgets()

        if self.product_id:
            self._load_product_data()
            
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL
        url_label = ttk.Label(main_frame, text="Ürün URL'si:")
        url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.url_entry.bind("<FocusOut>", self.fetch_product_name_event)

        # Otomatik Çekilen Ürün Adı
        self.name_status_var = tk.StringVar(value="URL'den ürün adı çekilecek...")
        name_status_label = ttk.Label(main_frame, textvariable=self.name_status_var, font="-size 10")
        name_status_label.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

        # Hedef Fiyat
        price_label = ttk.Label(main_frame, text="Hedef Fiyat (TL):")
        price_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(main_frame, textvariable=self.price_var)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky="e")
        
        self.save_button = ttk.Button(button_frame, text="Kaydet", command=self._save, style="success.TButton")
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="İptal", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def _load_product_data(self):
        product = self.db.get_product_by_id(self.product_id)
        if product:
            self.url_var.set(product['url'])
            self.price_var.set(str(product['target_price']))
            self.name_status_var.set(f"Mevcut Ürün: {product['name']}")

    def fetch_product_name_event(self, event=None):
        url = self.url_var.get()
        if url:
            self.name_status_var.set("Ürün adı getiriliyor, lütfen bekleyin...")
            threading.Thread(target=self._fetch_product_name_thread, args=(url,), daemon=True).start()

    def _fetch_product_name_thread(self, url):
        try:
            scraper = scraper_factory.get_scraper(url)
            data = scraper.scrape()
            self.after(0, self.name_status_var.set, f"✓ Bulunan Ürün: {data['name'][:50]}...")
        except ScraperError as e:
            self.after(0, self.name_status_var.set, f"✗ Hata: {e}")
        except Exception:
            self.after(0, self.name_status_var.set, "✗ Ürün adı getirilemedi. URL'yi kontrol edin.")

    def _save(self):
        url = self.url_var.get().strip()
        target_price_str = self.price_var.get().strip()

        if not url or not target_price_str:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.", parent=self)
            return

        try:
            target_price = float(target_price_str.replace(',', '.'))
        except ValueError:
            messagebox.showerror("Hata", "Lütfen hedef fiyat için geçerli bir sayı girin.", parent=self)
            return
        
        try:
            domain = url.split('/')[2].replace('www.', '')
            site = domain.split('.')[0] # 'amazon', 'hepsiburada' vs.
        except IndexError:
            messagebox.showerror("Hata", "Geçersiz URL formatı.", parent=self)
            return

        if self.product_id:
            # Düzenleme modu
            self.db.update_product(self.product_id, {'url': url, 'target_price': target_price})
        else:
            # Ekleme modu
            self.db.add_product(url, target_price, site)

        self.callback() # Ana penceredeki listeyi yenile
        self.destroy()