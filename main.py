# main.py

import ttkbootstrap as ttk
from src.gui.main_window import App
from src.core.config_manager import ConfigManager
from src.database.db_manager import DBManager

def main():
    """Uygulamanın ana başlangıç fonksiyonu."""
    # Önce ayarları yükleyerek temayı belirle
    try:
        db = DBManager()
        config = ConfigManager(db)
        theme = config.get('theme', 'litera') # Varsayılan tema
        db.close() # main'in db ile işi bitti
    except Exception as e:
        print(f"Başlangıçta veritabanı/yapılandırma hatası: {e}")
        theme = 'litera' # Hata durumunda varsayılan tema

    # Ana uygulamayı oluştur ve başlat
    app = App(themename=theme)
    app.mainloop()

if __name__ == "__main__":
    main()