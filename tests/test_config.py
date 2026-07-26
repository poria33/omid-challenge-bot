from app.core.config import get_settings


def test_settings_load() -> None:
    settings = get_settings()
    assert settings.app_name == "Challenge Omid"
    assert settings.max_users == 400
    assert settings.async_database_url.startswith(("sqlite+aiosqlite", "postgresql+asyncpg"))
