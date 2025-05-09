import pytest

from price_minecraft_checker import fetch_minecraft_prices


class FakeResp:
    status_code = 200

    def __init__(self, text):
        self.text = text


def test_fetch_minecraft_price_success(monkeypatch, sample_minecraft_html):
    monkeypatch.setattr(
        'price_minecraft_checker.requests.get',
        lambda *args, **kw: FakeResp(sample_minecraft_html)
    )
    prices = fetch_minecraft_prices()
    assert isinstance(prices, dict)
    assert 'Edição Standard' in prices
    assert 'Deluxe Collection' in prices
    assert prices['Edição Standard'] == 99.00
    assert prices['Deluxe Collection'] == 199.00


def test_fetch_minecraft_price_no_element(monkeypatch):
    monkeypatch.setattr(
        'price_minecraft_checker.requests.get',
        lambda *args, **kw: FakeResp('<html></html>')
    )
    with pytest.raises(Exception):
        fetch_minecraft_prices()