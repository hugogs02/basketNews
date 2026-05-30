import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "feeds.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS sent_articles (
        link TEXT PRIMARY KEY,
        title TEXT,
        feed_name TEXT,
        published_date TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def exists(link: str) -> bool:
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT 1 FROM sent_articles WHERE link=?", (link,))
    result = c.fetchone()

    conn.close()
    return result is not None


def save(link: str, title: str, feed_name: str, published_date: str):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT OR IGNORE INTO sent_articles 
        (link, title, feed_name, published_date)
        VALUES (?, ?, ?, ?)
    """, (link, title, feed_name, published_date))

    conn.commit()
    conn.close()