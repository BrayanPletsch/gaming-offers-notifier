from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(ROOT))
import config


@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    temp_db = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_FILE", temp_db)
    temp_db.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("ENABLE_EMAIL", "0")
    monkeypatch.setenv("ENABLE_WHATSAPP", "0")

    yield


@pytest.fixture
def sample_minecraft_html():
    path = Path(__file__).parent / "fixtures" / "minecraft.html"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def sample_epic_html():
    path = Path(__file__).parent / "fixtures" / "epic_free_games.html"
    return path.read_text(encoding="utf-8")