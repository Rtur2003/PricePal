# src/gui/main_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from PIL import Image, ImageTk
from pathlib import Path
import threading

from ..database.db_manager import DBManager
from ..core.config_manager import ConfigManager
from ..core.tracker import run_all_active_product_checks
from .add_product_dialog import AddProductDialog
from .settings_dialog import SettingsDialog
from ..utils import constants
from ..scraping.base_scraper import WebDriverManager 



class App(ttkb.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("PricePal - Fiyat Alarm Aracı")
        self.geometry("1200x600")

        self.db = DBManager()
        self.config = ConfigManager(self.db)

        self.icons = self._load_icons()
        self._create_widgets() # Create the widgets first
        self._setup_styles()   # Then apply styles to them
        self.refresh_product_list()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_styles(self):
        """Uygulama genelindeki özel stilleri tanımlar."""
        self.style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        
        # Durum etiketleri için stiller
        self.tree.tag_configure("price_alert", background=self.style.colors.success, font=('Helvetica', 9, 'bold'))
        self.tree.tag_configure("error", background=self.style.colors.danger)
        self.tree.tag_configure("pending", background=self.style.colors.warning)
        self.tree.tag_configure("tracking", foreground=self.style.colors.secondary) # Normal durum

    def _load_icons(self):
        icons = {}
        icon_path = Path(__file__).parent.parent.parent / "assets/icons"
        
        for name, filename in constants.ICONS.items():
            try:
                img = Image.open(icon_path / filename).resize((20, 20), Image.LANCZOS)
                icons[name] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                print(f"İkon bulunamadı: {filename}")
                icons[name] = None
        return icons

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=5)

        self.add_btn = ttk.Button(toolbar, text=" Yeni Ürün", image=self.icons.get("add"), compound=tk.LEFT, command=self.open_add_product_dialog)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        # ... (diğer butonlar aynı)

        self.refresh_btn = ttk.Button(toolbar, text=" Fiyatları Kontrol Et", image=self.icons.get("refresh"), compound=tk.LEFT, command=self.check_all_prices, style="info.TButton")
        self.refresh_btn.pack(side=tk.LEFT, padx=(20, 5))
        
        self.settings_btn = ttk.Button(toolbar, text=" Ayarlar", image=self.icons.get("settings"), compound=tk.LEFT, command=self.open_settings_dialog)
        self.settings_btn.pack(side=tk.RIGHT, padx=5)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("id", "status", "name", "target_price", "current_price", "site", "last_check")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # --- GÜNCELLENMİŞ SÜTUN AYARLARI ---
        self.tree.heading("id", text="ID", anchor=tk.CENTER)
        self.tree.heading("status", text="Durum", anchor=tk.W)
        self.tree.heading("name", text="Ürün Adı", anchor=tk.W)
        self.tree.heading("target_price", text="Hedef Fiyat", anchor=tk.E)
        self.tree.heading("current_price", text="Mevcut Fiyat", anchor=tk.E)
        self.tree.heading("site", text="Site", anchor=tk.CENTER)
        self.tree.heading("last_check", text="Son Kontrol", anchor=tk.CENTER)

        self.tree.column("id", width=40, anchor=tk.CENTER, stretch=False)
        self.tree.column("status", width=100, anchor=tk.W, stretch=False)
        self.tree.column("name", width=450, anchor=tk.W)
        self.tree.column("target_price", width=120, anchor=tk.E, stretch=False)
        self.tree.column("current_price", width=120, anchor=tk.E, stretch=False)
        self.tree.column("site", width=100, anchor=tk.CENTER, stretch=False)
        self.tree.column("last_check", width=150, anchor=tk.CENTER, stretch=False)
        # ------------------------------------

        # ... (kaydırma çubukları ve status_bar aynı) ...
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Hazır.")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)


    def refresh_product_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        products = self.db.get_all_products()
        for p in products:
            status = p['status'] or 'Bilinmiyor'
            tag = status.lower() if status in ['PRICE_ALERT', 'ERROR', 'PENDING', 'TRACKING'] else ''
            
            self.tree.insert("", tk.END, values=(
                p['id'],
                status,
                p['name'] or 'Henüz Getirilmedi',
                f"{p['target_price']:.2f} TL",
                f"{p['current_price']:.2f} TL" if p['current_price'] else "N/A",
                p['site'].capitalize(),
                p['last_check_date'][:16].replace('T', ' ') if p['last_check_date'] else "Hiç"
            ), tags=(tag,))
        self.update_status(f"{len(products)} ürün takip ediliyor.")

    def open_add_product_dialog(self):
        AddProductDialog(self, self.db, callback=self.refresh_product_list)

    def open_edit_product_dialog(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir ürün seçin.", parent=self)
            return
        
        product_id = self.tree.item(selected_item)['values'][0]
        AddProductDialog(self, self.db, callback=self.refresh_product_list, product_id=product_id)

    def delete_selected_product(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir ürün seçin.", parent=self)
            return
            
        product_id = self.tree.item(selected_item)['values'][0]
        product_name = self.tree.item(selected_item)['values'][2]

        if messagebox.askyesno("Onay", f"'{product_name}' ürününü silmek istediğinizden emin misiniz?", parent=self):
            self.db.delete_product(product_id)
            self.refresh_product_list()
            self.update_status(f"Ürün ID {product_id} silindi.")

    # src/gui/main_window.py dosyasında bu metodu GÜNCELLEYİN

    def _run_price_checks_thread(self):
        self.after(0, self.update_status, "Fiyatlar kontrol ediliyor...")
        self.after(0, self.refresh_btn.config, {"state": "disabled"})
        
        try:
            run_all_active_product_checks()
        except Exception as e:
            print(f"Fiyat kontrol thread'inde bir hata yakalandı: {e}")
        
        self.after(0, self.refresh_product_list)
        self.after(0, self.refresh_btn.config, {"state": "normal"})
        self.after(0, self.update_status, "Kontrol tamamlandı.")

    def check_all_prices(self):
        threading.Thread(target=self._run_price_checks_thread, daemon=True).start()

    def open_settings_dialog(self):
        SettingsDialog(self, self.config)

    def update_status(self, message):
        self.status_var.set(message)
    
    def _on_closing(self):
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinize emin misiniz?"):
            print("Uygulama kapatılıyor...")
            self.db.close()
            WebDriverManager.close_driver()
            self.destroy()