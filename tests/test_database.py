import sqlite3

import config
from database import (
    init_db,
    save_price,
    get_last_price,
    save_free_games,
    get_last_free_games,
)


def test_init_db_creates_tables(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_FILE", tmp_path / "db.sqlite")
    init_db()
    conn = sqlite3.connect(str(config.DB_FILE))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('prices','free_games')"
    )
    tables = {row[0] for row in cursor.fetchall()}
    assert 'prices' in tables and 'free_games' in tables
    conn.close()


def test_price_storage_and_retrieval_single_edition():
    init_db()
    assert get_last_price('Edição Standard') is None
    save_price('Edição Standard', 10.5)
    save_price('Edição Standard', 20.0)
    assert get_last_price('Edição Standard') == 20.0
    assert get_last_price('Deluxe Collection') is None


def test_price_storage_and_retrieval_multiple_editions():
    init_db()
    save_price('Edição Standard', 50.0)
    save_price('Deluxe Collection', 100.0)
    assert get_last_price('Edição Standard') == 50.0
    assert get_last_price('Deluxe Collection') == 100.0


def test_free_games_storage_and_retrieval():
    init_db()
    games = [('A', 'url', '2025-01-01T00:00:00+00:00', '2025-01-07T00:00:00+00:00')]
    save_free_games(games)
    assert get_last_free_games() == games
    new = [('B', 'url2', None, None)]
    save_free_games(new)
    assert get_last_free_games() == new