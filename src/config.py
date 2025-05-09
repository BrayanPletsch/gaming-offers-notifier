import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv


env_file = find_dotenv()
load_dotenv(env_file)

BASE_DIR = Path(__file__).resolve().parent.parent

# Banco de dados
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "history.db"

# WhatsApp Web (Selenium)
WHATSAPP_PROFILE = BASE_DIR / "whatsapp_profile"
WHATSAPP_PROFILE.mkdir(parents=True, exist_ok=True)

#.env
ENABLE_EMAIL = os.getenv('ENABLE_EMAIL') == '1'
ENABLE_WHATSAPP = os.getenv('ENABLE_WHATSAPP') == '1'
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE')
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT')