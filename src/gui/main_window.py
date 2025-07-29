# src/gui/main_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from PIL import Image, ImageTk
from pathlib import Path
import threading
from ..core.tracker import check_single_product, run_all_active_product_checks
from ..database.db_manager import DBManager
from ..core.config_manager import ConfigManager
from ..core.tracker import check_single_product
from .add_product_dialog import AddProductDialog
from .settings_dialog import SettingsDialog

class App(ttkb.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("PricePal - Fiyat Alarm Aracı")
        self.geometry("1200x600")

        # Backend bileşenlerini başlat
        self.db = DBManager()
        self.config = ConfigManager(self.db)

        # İkonları yükle
        self.icons = self._load_icons()

        self._create_widgets()
        self.refresh_product_list()
        
        # Pencere kapatıldığında veritabanı bağlantısını kapat
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_icons(self):
        icons = {}
        icon_files = {"add": "add.png", "edit": "edit.png", "delete": "delete.png", 
                      "refresh": "refresh.png", "settings": "settings.png"}
        icon_path = Path(__file__).parent.parent.parent / "assets/icons"
        
        for name, filename in icon_files.items():
            try:
                img = Image.open(icon_path / filename).resize((24, 24), Image.LANCZOS)
                icons[name] = ImageTk.PhotoImage(img)
            except FileNotFoundError:
                print(f"İkon bulunamadı: {filename}")
                icons[name] = None
        return icons

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Araç Çubuğu
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=5)

        self.add_btn = ttk.Button(toolbar, text=" Yeni Ürün", image=self.icons.get("add"), compound=tk.LEFT, command=self.open_add_product_dialog)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.edit_btn = ttk.Button(toolbar, text=" Düzenle", image=self.icons.get("edit"), compound=tk.LEFT, command=self.open_edit_product_dialog)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = ttk.Button(toolbar, text=" Sil", image=self.icons.get("delete"), compound=tk.LEFT, command=self.delete_selected_product, style="danger.TButton")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(toolbar, text=" Fiyatları Kontrol Et", image=self.icons.get("refresh"), compound=tk.LEFT, command=self.check_all_prices, style="info.TButton")
        self.refresh_btn.pack(side=tk.LEFT, padx=(20, 5))
        
        self.settings_btn = ttk.Button(toolbar, text=" Ayarlar", image=self.icons.get("settings"), compound=tk.LEFT, command=self.open_settings_dialog)
        self.settings_btn.pack(side=tk.RIGHT, padx=5)

        # Ürün Listesi (Treeview)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("id", "status", "name", "target_price", "current_price", "site", "last_check")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun Başlıkları
        self.tree.heading("id", text="ID")
        self.tree.heading("status", text="Durum")
        self.tree.heading("name", text="Ürün Adı")
        self.tree.heading("target_price", text="Hedef Fiyat")
        self.tree.heading("current_price", text="Mevcut Fiyat")
        self.tree.heading("site", text="Site")
        self.tree.heading("last_check", text="Son Kontrol")

        # Sütun Genişlikleri
        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("status", width=100)
        self.tree.column("name", width=400)
        self.tree.column("target_price", width=100, anchor=tk.E)
        self.tree.column("current_price", width=100, anchor=tk.E)
        self.tree.column("site", width=100)
        self.tree.column("last_check", width=150)
        
        # Renk etiketleri
        self.tree.tag_configure("price_alert", background=self.style.colors.success)
        self.tree.tag_configure("error", background=self.style.colors.danger)
        self.tree.tag_configure("pending", background=self.style.colors.warning)

        # Kaydırma çubukları
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Durum Çubuğu
        self.status_var = tk.StringVar(value="Hazır.")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)

    def refresh_product_list(self):
        # Önce mevcut listeyi temizle
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Veritabanından tüm ürünleri çek ve listeye ekle
        products = self.db.get_all_products()
        for p in products:
            tag = p['status'].lower() if p['status'] in ['PRICE_ALERT', 'ERROR', 'PENDING'] else ''
            self.tree.insert("", tk.END, values=(
                p['id'],
                p['status'] or 'Bilinmiyor',
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
            # Kendi veritabanı bağlantısını yöneten, thread-uyumlu fonksiyonu çağır
            run_all_active_product_checks()
        except Exception as e:
            # Bu bloğun çalışması beklenmez ama her ihtimale karşı
            print(f"Fiyat kontrol thread'inde bir hata yakalandı: {e}")
        
        # İşlem bittiğinde arayüzü ana thread üzerinden güvenle güncelle
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
            self.db.close()
            self.destroy()