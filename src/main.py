import time

import schedule

from price_minecraft_checker import check_price_and_notify, fetch_minecraft_prices, save_price
from price_epic_checker import check_free_games_and_notify, fetch_free_games, save_free_games
from notifier import Notifier
from database import init_db


def main():
    init_db()
    notifier = Notifier()

    try:
        prices = fetch_minecraft_prices()
        for ed, pr in prices.items():
            save_price(ed, pr)
    except Exception as e:
        notifier.send_email(
            "❌ Erro no scraping inicial do Minecraft",
            f"Ocorreu um erro ao buscar preços no Minecraft:\n{e}"
        )
        prices = {}

    try:
        games = fetch_free_games()
        save_free_games(games)
    except Exception as e:
        notifier.send_email(
            "❌ Erro no scraping inicial da Epic",
            f"Ocorreu um erro ao buscar jogos grátis na Epic:\n{e}"
        )
        games = []

    lines = ["Serviço conectado e scraping inicial:"]
    lines.append("\n💰 Minecraft:")
    for edition, price in prices.items():
        lines.append(f"- {edition}: R$ {price:.2f}")

    lines.append("\n🎁 Epic Free Games:")
    if games:
        for title, url, start, end in games:
            lines.append(f"- {title} ({start} → {end}): https://store.epicgames.com{url}")
    else:
        lines.append("- Nenhum jogo gratuito no momento")

    body = "\n".join(lines)
    notifier.send_email("✅ Serviço conectado", body)
    notifier.send_whatsapp(body)
    schedule.every(6).hours.do(check_price_and_notify)
    schedule.every(6).hours.do(check_free_games_and_notify)
    schedule.every(1).hours.do(notifier.check_whatsapp_connection_and_notify)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()