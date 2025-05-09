import requests
from bs4 import BeautifulSoup

from notifier import Notifier
from database import save_price, get_last_price


def fetch_minecraft_prices():
    url = 'https://www.minecraft.net/pt-br/store/minecraft-java-bedrock-edition-pc'
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception('Erro ao acessar o site do Minecraft')
    
    soup = BeautifulSoup(response.text, 'html.parser')
    prices = {}
    cards = soup.select('.MC_productHeroB_skuCard')

    for card in cards:
        header = card.select_one('.MC_productHeroB_skuCard_header .MC_Heading')
        if not header:
            continue
        edition = header.get_text(strip=True)

        price_span = card.select_one(
            '.MC_productHeroB_skuCard_priceContainer .MC_productHeroB_skuCard_price span'
        )
        if not price_span:
            continue
        texto = price_span.get_text(strip=True)
        price = float(
            texto
            .replace('R$', '')
            .replace('\u00A0', '')
            .replace('.', '')
            .replace(',', '.')
        )
        prices[edition] = price

    if not prices:
        raise Exception('Não foi possível encontrar preços no HTML do Minecraft.')
    return prices


def check_price_and_notify():
    current_prices = fetch_minecraft_prices()
    notifier = Notifier()
    promos = []

    for edition, current_price in current_prices.items():
        last_price = get_last_price(edition)
        save_price(edition, current_price)
        if last_price and current_price < last_price:
            promos.append((edition, last_price, current_price))

    if not promos:
        return

    lines = [f'- {ed}: caiu de R$ {old:.2f} para R$ {new:.2f}' for ed, old, new in promos]
    msg = 'Promoções Minecraft\n' + '\n'.join(lines)
    title = '🤑 PROMOÇÕES MINECRAFT: ' + ', '.join(ed.upper() for ed, *_ in promos)

    notifier.send_email(title, msg)
    notifier.send_whatsapp(msg)
