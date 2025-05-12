from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from database import save_free_games, get_last_free_games
from notifier import Notifier


URL = "https://store.epicgames.com/pt-BR/free-games"


def fetch_free_games():
    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    driver.get(URL)
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-component='FreeOfferCard']"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    offers = []

    for a in soup.select("div[data-component='FreeOfferCard'] a.css-g3jcms"):
        title_el = a.select_one("h6")
        title = title_el.text.strip() if title_el else "—"
        href = a.get("href", "")
        link = "https://store.epicgames.com" + href

        times = a.select("time")
        if len(times) == 1:
            start_iso, end_iso = times[0]["datetime"], None
        elif len(times) >= 2:
            start_iso, end_iso = times[0]["datetime"], times[1]["datetime"]
        else:
            start_iso = end_iso = None

        offers.append((title, link, start_iso, end_iso))
    return offers


def check_free_games_and_notify():
    current = fetch_free_games()
    last = get_last_free_games()
    new_games = [g for g in current if g not in last]
    if new_games:
        save_free_games(current)
        notifier = Notifier()
        mensagens = []
        for title, link, start, end in new_games:
            periodo = (
                datetime.fromisoformat(start).strftime("%d/%m/%Y %H:%M")
                + (" até " + datetime.fromisoformat(end).strftime("%d/%m/%Y %H:%M") if end else "")
            ) if start else "Período desconhecido"
            mensagens.append(f"{title}\n{periodo}\n{link}")

        title = 'NOVOS JOGOS GRATUITOS NA EPIC GAMES'
        msg = '🎮 Novos jogos grátis na Epic Games:\n\n' + '\n\n'.join(mensagens)
        notifier.send_email(title, msg)
        notifier.send_whatsapp(msg)