import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config


class Notifier:
    def __init__(self):
        self.enable_email = config.ENABLE_EMAIL
        self.enable_whatsapp = config.ENABLE_WHATSAPP
        self.phone = config.WHATSAPP_PHONE

        self.email_host = config.SMTP_HOST
        self.email_port = config.SMTP_PORT
        self.email_user = config.SMTP_USER
        self.email_pass = config.SMTP_PASS
        self.recipient = config.EMAIL_RECIPIENT
        
        if self.enable_whatsapp:
            chrome_opts = Options()
            chrome_opts.add_argument(f'--user-data-dir={config.WHATSAPP_PROFILE}')
            # modo headless: após login inicial, remova se precisar ver o QR code
            # chrome_opts.add_argument('--headless=new')  
            chrome_opts.add_argument('--no-sandbox')
            chrome_opts.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=chrome_opts)


    def send_email(self, subject: str, body: str):
        if not self.enable_email:
            return
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.email_user
        msg['To'] = self.recipient
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP(self.email_host, self.email_port) as server:
            server.starttls()
            server.login(self.email_user, self.email_pass)
            server.send_message(msg)


    def send_whatsapp(self, message: str):
        if not self.enable_whatsapp:
            return
        
        driver = self.driver
        driver.get('https://web.whatsapp.com/')
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='chat-list']"))
            )
        except:
            print('Abra o WhatsApp Web localmente e escaneie o QR code aqui:')
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='chat-list']"))
            )
        url = f'https://web.whatsapp.com/send?phone={self.phone}&text={message}'
        driver.get(url)
        send_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_btn.click()
        time.sleep(5)
        print('Mensagem enviada no WhatsApp!')
    
    
    def send_startup_notification(self):
        subject = "✅ Serviço conectado"
        body = "O Bot subiu com sucesso e está operacional."
        self.send_email(subject, body)
        self.send_whatsapp(body)


    def check_whatsapp_connection_and_notify(self):
        if not self.enable_whatsapp:
            return

        driver = getattr(self, 'driver', None)
        if driver is None:
            title = "⚠️ WhatsApp Web desconectado"
            msg = (
                "O WhatsApp Web não carregou a lista de conversas. "
                "Provavelmente você foi desconectado.\n"
                "Reabra o QR-code e escaneie novamente."
            )
            self.send_email(title, msg)
            return

        try:
            driver.get("https://web.whatsapp.com/")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='chat-list']"))
            )
        except TimeoutException:
            title = "⚠️ WhatsApp Web desconectado"
            msg = (
                "O WhatsApp Web não carregou a lista de conversas. "
                "Provavelmente você foi desconectado.\n"
                "Reabra o QR-code e escaneie novamente."
            )
            self.send_email(title, msg)
        except WebDriverException as e:
            title = "❌ Erro no driver Selenium"
            msg = f"Erro ao iniciar o ChromeDriver para checar o WhatsApp Web:\n{e}"
            self.send_email(title, msg)
        finally:
            try:
                driver.quit()
            except:
                pass
    

    def __del__(self):
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass