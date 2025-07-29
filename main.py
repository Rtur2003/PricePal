# main.py
from src.gui.main_window import App
from ttkbootstrap import Style

def main():
    # Uygulamayı başlat
    # ttkbootstrap stilini kullanarak bir pencere oluştur
    # Örnek: style = Style(theme='litera')
    # app = App(style=style)
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()