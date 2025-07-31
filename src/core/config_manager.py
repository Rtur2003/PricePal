# src/core/config_manager.py

import keyring
from ..database.db_manager import DBManager
from ..utils import constants

class ConfigManager:
    """
    Uygulama ayarlarını ve hassas kimlik bilgilerini yönetir.
    Ayarları veritabanından, şifreleri ise işletim sisteminin
    güvenli anahtar zincirinden (keyring) okur/yazar.
    """

    def __init__(self, db_manager: DBManager):
        """
        ConfigManager'ı bir DBManager örneği ile başlatır.
        :param db_manager: Kullanılacak DBManager nesnesi.
        """
        self.db = db_manager

    def get(self, key: str, default: str = None) -> str:
        """
        Veritabanından belirli bir ayarı okur. Bulunamazsa varsayılan değeri döndürür.
        """
        value = self.db.get_setting(key)
        return value if value is not None else default

    def set(self, key: str, value: str):
        """Veritabanına bir ayar yazar."""
        self.db.set_setting(key, value)

    def set_email_credentials(self, email: str, password: str) -> bool:
        """
        E-posta bilgilerini güvenli bir şekilde kaydeder.
        E-posta adresi veritabanına, şifre ise keyring'e yazılır.
        :return: İşlemin başarılı olup olmadığını belirten boolean.
        """
        try:
            self.set('user_email', email)
            keyring.set_password(constants.SERVICE_ID, email, password)
            print("E-posta kimlik bilgileri güvenli bir şekilde kaydedildi.")
            return True
        except Exception as e:
            print(f"Keyring'e şifre kaydedilirken hata oluştu: {e}")
            return False

    def get_email_password(self) -> str | None:
        """
        Kaydedilmiş e-posta şifresini keyring'den güvenli bir şekilde alır.
        :return: Kayıtlı şifre veya bulunamazsa None.
        """
        email = self.get('user_email')
        if not email:
            return None
        try:
            return keyring.get_password(constants.SERVICE_ID, email)
        except Exception as e:
            print(f"Keyring'den şifre okunurken hata oluştu: {e}")
            return None