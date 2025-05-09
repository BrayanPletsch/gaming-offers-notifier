from datetime import datetime

import requests
from bs4 import BeautifulSoup

from database import save_free_games, get_last_free_games
from notifier import Notifier


URL = "https://store.epicgames.com/pt-BR/free-games"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_free_games():
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar Epic Games Store: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    offers = []

    cards = soup.select("div[data-component='FreeOfferCard'] a.css-g3jcms")
    for a in cards:
        title_el = a.select_one("h6")
        title = title_el.text.strip() if title_el else "—"

        href = a.get("href", "")
        link = "https://store.epicgames.com" + href

        span = a.select_one("p span")
        times = span.find_all("time") if span else []

        if len(times) == 1:
            start_iso = times[0]["datetime"]
            end_iso = None
        elif len(times) >= 2:
            start_iso = times[0]["datetime"]
            end_iso   = times[1]["datetime"]
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