from sqlalchemy.engine import make_url

from app.config import Settings


def test_postgres_parts_escape_special_characters_in_password():
    raw = "p@ss:w/rd#1?%"
    url = Settings(database_url=None, postgres_host="db", postgres_password=raw).sqlalchemy_url
    parsed = make_url(url.render_as_string(hide_password=False))
    assert parsed.password == raw
    assert (parsed.host, parsed.port, parsed.database) == ("db", 5432, "resume_analyzer")


def test_database_url_takes_precedence_and_sqlite_is_default():
    assert Settings(database_url="sqlite:///x.db", postgres_host="db").sqlalchemy_url.database == "x.db"
    assert Settings(database_url=None, postgres_host=None).sqlalchemy_url.get_backend_name() == "sqlite"
