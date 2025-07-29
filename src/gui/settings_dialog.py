# src/gui/settings_dialog.py

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
import webbrowser
import threading

from ..core.config_manager import ConfigManager
from ..notifications import email_sender

class SettingsDialog(ttkb.Toplevel):
    def __init__(self, parent, config: ConfigManager, **kwargs):
        super().__init__(parent, **kwargs)
        self.title("Ayarlar")
        self.geometry("500x350")
        self.transient(parent) # Ana pencerenin üzerinde kalmasını sağlar

        self.config = config
        self.parent = parent

        self._create_widgets()
        self._load_settings()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Genel Ayarlar Sekmesi
        general_tab = ttk.Frame(notebook, padding=10)
        notebook.add(general_tab, text="Genel")
        
        theme_label = ttk.Label(general_tab, text="Uygulama Teması:")
        theme_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(general_tab, textvariable=self.theme_var,
                                        values=['litera', 'darkly', 'superhero', 'flatly', 'journal'])
        self.theme_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # E-posta Ayarları Sekmesi
        email_tab = ttk.Frame(notebook, padding=10)
        notebook.add(email_tab, text="E-posta Bildirimleri")
        
        email_label = ttk.Label(email_tab, text="E-posta Adresiniz:")
        email_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(email_tab, textvariable=self.email_var)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        pass_label = ttk.Label(email_tab, text="Uygulama Şifresi:")
        pass_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.pass_var = tk.StringVar()
        self.pass_entry = ttk.Entry(email_tab, textvariable=self.pass_var, show="*")
        self.pass_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        help_text = "Not: Güvenlik için e-posta hesabınızın şifresini değil, Google/Outlook gibi servislerden alacağınız 'Uygulamaya Özel Şifre'yi kullanın."
        help_label = ttk.Label(email_tab, text=help_text, wraplength=350, font="-size 10")
        help_label.grid(row=2, column=0, columnspan=2, pady=(10, 5))
        
        self.test_button = ttk.Button(email_tab, text="Test E-postası Gönder", command=self.send_test_email)
        self.test_button.grid(row=3, column=1, pady=10, sticky="e")

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        save_button = ttk.Button(button_frame, text="Kaydet", command=self._save_settings, style="success.TButton")
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="İptal", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

    def _load_settings(self):
        self.theme_var.set(self.config.get('theme', 'litera'))
        self.email_var.set(self.config.get('user_email', ''))
        # Şifre güvenlik nedeniyle yüklenmez, kullanıcı her seferinde girebilir veya keyring'de saklanır
        # Buraya keyring'den okuma eklenebilir ama ayar ekranında göstermek riskli olabilir.

    def _save_settings(self):
        # Tema ayarını kaydet
        new_theme = self.theme_var.get()
        if self.config.get('theme') != new_theme:
            self.config.set('theme', new_theme)
            messagebox.showinfo("Yeniden Başlatma Gerekli", "Tema değişikliğinin uygulanması için lütfen uygulamayı yeniden başlatın.", parent=self)

        # E-posta ayarlarını kaydet
        email = self.email_var.get()
        password = self.pass_var.get()

        if email and password:
            self.config.set_email_credentials(email, password)
        elif email: # Sadece email girildiyse
            self.config.set('user_email', email)
        
        messagebox.showinfo("Başarılı", "Ayarlar başarıyla kaydedildi.", parent=self)
        self.destroy()

    def _send_test_email_thread(self):
        email = self.email_var.get()
        password = self.pass_var.get()
        if not email or not password:
            messagebox.showwarning("Eksik Bilgi", "Lütfen e-posta ve şifre alanlarını doldurun.", parent=self)
            self.test_button.config(state="normal")
            return

        success = email_sender.send_price_alert_email(
            sender_email=email, password=password, recipient_email=email,
            smtp_host=self.config.get('smtp_host', 'smtp.gmail.com'),
            smtp_port=int(self.config.get('smtp_port', 587)),
            product_name="Test Ürünü", new_price=99.99, product_url="https://github.com/Rtur2003/PricePal"
        )
        
        if success:
            messagebox.showinfo("Başarılı", f"Test e-postası '{email}' adresine gönderildi. Gelen kutunuzu kontrol edin.", parent=self)
        else:
            messagebox.showerror("Hata", "Test e-postası gönderilemedi. Lütfen ayarlarınızı ve internet bağlantınızı kontrol edin.", parent=self)
        
        self.test_button.config(state="normal")

    def send_test_email(self):
        self.test_button.config(state="disabled")
        threading.Thread(target=self._send_test_email_thread, daemon=True).start()