# src/notifications/email_sender.py

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_price_alert_email(
    sender_email: str,
    password: str,
    recipient_email: str,
    smtp_host: str,
    smtp_port: int,
    product_name: str,
    new_price: float,
    product_url: str,
) -> bool:
    """
    Kullanıcıya fiyat alarmı e-postası gönderir.

    :return: E-postanın başarıyla gönderilip gönderilmediğini belirten boolean.
    """
    if not all([sender_email, password, recipient_email]):
        print("Hata: E-posta göndermek için gerekli kimlik bilgileri eksik.")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = f"💸 Fiyat Alarmı! '{product_name}' için harika fırsat!"
    message["From"] = sender_email
    message["To"] = recipient_email

    # E-posta içeriğini oluştur (HTML formatında)
    html_body = f"""
    <html>
      <body>
        <h2>Fiyat Alarmı!</h2>
        <p>Merhaba,</p>
        <p>Takip ettiğiniz <b>{product_name}</b> ürününün fiyatı, belirlediğiniz hedefin altına düştü!</p>
        <p style="font-size: 24px; font-weight: bold; color: #28a745;">
          Yeni Fiyat: {new_price:,.2f} TL
        </p>
        <p>Fırsatı kaçırmamak için hemen ürünü inceleyin:</p>
        <p>
          <a href="{product_url}" style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">
            Ürüne Git
          </a>
        </p>
        <hr>
        <p><small>Bu e-posta PricePal tarafından otomatik olarak gönderilmiştir.</small></p>
      </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html"))

    # Güvenli SSL bağlantısı oluştur ve e-postayı gönder
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print(f"Fiyat alarmı e-postası '{recipient_email}' adresine başarıyla gönderildi.")
        return True
    except smtplib.SMTPAuthenticationError:
        print("E-posta gönderilemedi. SMTP kimlik doğrulama hatası. Lütfen e-posta ve uygulama şifrenizi kontrol edin.")
        return False
    except Exception as e:
        print(f"E-posta gönderilirken bir hata oluştu: {e}")
        return False