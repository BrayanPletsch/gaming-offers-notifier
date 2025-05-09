import price_epic_checker
from database import init_db, get_last_free_games


class FakeRespEpic:
    status_code = 200
    def __init__(self, text):
        self.text = text


def test_fetch_free_games_empty(monkeypatch, sample_epic_html):
    monkeypatch.setattr(price_epic_checker.requests, 'get',
                        lambda *args, **kw: FakeRespEpic('<html></html>'))
    games = price_epic_checker.fetch_free_games()
    assert games == []


def test_fetch_free_games_success(monkeypatch, sample_epic_html):
    monkeypatch.setattr(price_epic_checker.requests, 'get',
                        lambda *args, **kw: FakeRespEpic(sample_epic_html))
    games = price_epic_checker.fetch_free_games()
    assert isinstance(games, list)
    for title, link, start, end in games:
        assert title != ""
        assert link.startswith('https://store.epicgames.com')


def test_notify_on_new_free_games(monkeypatch, sample_epic_html):
    init_db()
    assert get_last_free_games() == []

    monkeypatch.setattr(price_epic_checker.requests, 'get',
                        lambda *args, **kw: FakeRespEpic(sample_epic_html))

    sent = []
    class DummyNotifier:
        def __init__(self): pass
        def send_email(self, subj, body):  sent.append(('email', subj, body))
        def send_whatsapp(self, body):   sent.append(('whatsapp', body))
    monkeypatch.setattr(price_epic_checker, 'Notifier', DummyNotifier)

    price_epic_checker.check_free_games_and_notify()
    assert any(kind == 'email' for kind, *rest in sent)
    assert any(kind == 'whatsapp' for kind, *rest in sent)