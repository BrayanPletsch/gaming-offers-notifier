import sqlite3
from datetime import datetime, timezone

import config


def init_db():
    conn = sqlite3.connect(config.DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edition TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS free_games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            start TEXT,
            end TEXT,
            date_added TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_price(edition: str, price: float):
    conn = sqlite3.connect(config.DB_FILE)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute(
        "INSERT INTO prices (edition, price, timestamp) VALUES (?, ?, ?)",
        (edition, price, now)
    )
    conn.commit()
    conn.close()


def get_last_price(edition: str):
    conn = sqlite3.connect(config.DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT price FROM prices WHERE edition = ? ORDER BY id DESC LIMIT 1",
        (edition,)
    )
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def save_free_games(games: list):
    conn = sqlite3.connect(config.DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM free_games")
    now = datetime.now(timezone.utc).isoformat()
    for title, url, start, end in games:
        c.execute(
            "INSERT INTO free_games (title, url, start, end, date_added) VALUES (?, ?, ?, ?, ?)",
            (title, url, start, end, now)
        )
    conn.commit()
    conn.close()


def get_last_free_games():
    conn = sqlite3.connect(config.DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT title, url, start, end FROM free_games"
    )
    rows = c.fetchall()
    conn.close()
    return rows