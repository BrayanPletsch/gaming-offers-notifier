import pytest

import schedule

import main
from price_minecraft_checker import check_price_and_notify
from price_epic_checker import check_free_games_and_notify
from notifier import Notifier


class DummyScheduler:
    def __init__(self):
        self.jobs = []

    @property
    def hours(self):
        return self

    def do(self, fn):
        self.jobs.append(fn)
        return self


@pytest.fixture(autouse=True)
def stub_schedule(monkeypatch):
    dummy = DummyScheduler()
    monkeypatch.setattr(schedule, 'every', lambda *args, **kwargs: dummy)

    import types
    fake_time = types.SimpleNamespace(
        sleep=lambda x: (_ for _ in ()).throw(KeyboardInterrupt())
    )
    monkeypatch.setattr(main, 'time', fake_time)

    return dummy


def test_main_schedules_jobs(stub_schedule, monkeypatch):
    monkeypatch.setattr(main, 'fetch_minecraft_prices', lambda: {})
    monkeypatch.setattr(main, 'fetch_free_games',       lambda: [])
    called = {'init': False}

    class DummyNotifier:
        def __init__(self): pass
        def send_email(self, *args, **kwargs): pass
        def send_whatsapp(self, *args, **kwargs): pass
        def check_whatsapp_connection_and_notify(self): pass
    monkeypatch.setattr(main, 'Notifier', DummyNotifier)

    called = {'init': False}
    monkeypatch.setattr(main, 'init_db', lambda: called.__setitem__('init', True))

    with pytest.raises(KeyboardInterrupt):
        main.main()

    assert called['init'], "init_db() deve ser chamado ao iniciar"
    assert check_price_and_notify in stub_schedule.jobs, \
        "Função de checar preço deve ser agendada"
    assert check_free_games_and_notify in stub_schedule.jobs, \
        "Função de checar jogos grátis deve ser agendada"
    assert any(
        getattr(job, "__func__", job) is main.Notifier.check_whatsapp_connection_and_notify
        for job in stub_schedule.jobs
    ), "Função de checar conexão do WhatsApp deve ser agendada"