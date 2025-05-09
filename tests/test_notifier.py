import smtplib

import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException

import config
from notifier import Notifier


smtp_instances = []

class FakeSMTP:
    def __init__(self, host, port):
        smtp_instances.append(self)
    def starttls(self): pass
    def login(self, user, pwd): pass
    def send_message(self, msg): self.sent_msg = msg
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): pass


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    smtp_instances.clear()
    monkeypatch.setattr(config, 'ENABLE_EMAIL', True)
    monkeypatch.setattr(config, 'ENABLE_WHATSAPP', False)
    monkeypatch.setenv('SMTP_USER', 'user')
    monkeypatch.setenv('SMTP_PASS', 'pass')
    monkeypatch.setattr(smtplib, 'SMTP', FakeSMTP)


def test_send_email_active():
    nt = Notifier()
    try:
        nt.send_email('Subject', 'Body')
    except Exception as e:
        pytest.fail(f'send_email lançou exceção: {e}')


def test_send_email_inactive(monkeypatch):
    monkeypatch.setattr(config, 'ENABLE_EMAIL', False)
    nt = Notifier()
    try:
        nt.send_email('X', 'Y')
    except Exception as e:
        pytest.fail(f'send_email lançou exceção com ENABLE_EMAIL=False: {e}')


def test_check_whatsapp_connection_disconnected(monkeypatch):
    nt = object.__new__(Notifier)
    nt.enable_whatsapp = True
    nt.enable_email = True
    nt.email_host = 'smtp.example.com'
    nt.email_port = 587
    nt.email_user = 'user'
    nt.email_pass = 'pass'
    nt.recipient = 'test@example.com'
    nt.driver = None

    monkeypatch.setattr('selenium.webdriver.support.ui.WebDriverWait.until',
                        lambda self, cond: (_ for _ in ()).throw(TimeoutException()))

    nt.check_whatsapp_connection_and_notify()
    assert len(smtp_instances) == 1, "Deve instanciar SMTP ao detectar desconexão"
    sent = smtp_instances[0].sent_msg
    assert sent['Subject'] == "⚠️ WhatsApp Web desconectado"


def test_check_whatsapp_connection_driver_error():
    nt = object.__new__(Notifier)
    nt.enable_whatsapp = True
    nt.enable_email = True
    nt.email_host = 'smtp.example.com'
    nt.email_port = 587
    nt.email_user = 'user'
    nt.email_pass = 'pass'
    nt.recipient = 'test@example.com'

    class DummyDriver:
        def quit(self): pass
    nt.driver = DummyDriver()
    nt.driver.get = lambda url: (_ for _ in ()).throw(WebDriverException("fail"))

    nt.check_whatsapp_connection_and_notify()
    assert len(smtp_instances) == 1, "Deve instanciar SMTP ao ocorrer erro no driver"
    sent = smtp_instances[-1].sent_msg
    assert sent['Subject'].startswith("❌ Erro no driver Selenium")
