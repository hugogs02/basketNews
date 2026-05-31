import sqlite3

DB = "feeds.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            link TEXT PRIMARY KEY,
            title TEXT,
            source TEXT,
            published TEXT
        )
    """)

    conn.commit()
    conn.close()


def exists(link):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT 1 FROM news WHERE link = ?", (link,))
    row = c.fetchone()

    conn.close()
    return row is not None


def save(link, title, source, published):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT OR IGNORE INTO news VALUES (?, ?, ?, ?)
    """, (link, title, source, published))

    conn.commit()
    conn.close()