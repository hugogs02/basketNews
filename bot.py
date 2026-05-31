import yaml
import requests
import html
import logging
from pathlib import Path

from config import TOKEN
from db import init_db, exists, save
from sources.dispatcher import get_source

init_db()

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


# ---------------- LOGGING ----------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# ---------------- CONFIG ----------------
with open("feeds.yaml", "r", encoding="utf-8") as f:
    FEEDS = yaml.safe_load(f)

with open("channels.yaml", "r", encoding="utf-8") as f:
    CHANNELS = yaml.safe_load(f)["channels"]


# ---------------- TELEGRAM ----------------
def send_message(chat_id, text):

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    r = requests.post(BASE_URL, data=payload)
    logging.info(f"Telegram: {r.status_code} | {text[:80]}")


# ---------------- FORMAT ----------------
def format_message(tags, title, summary, link):

    hashtags = " ".join(f"#{t.replace(' ', '_')}" for t in tags)

    return (
        f"<b>{html.escape(hashtags)}</b>\n"
        f"<b>{html.escape(title)}</b>\n"
        f"{html.escape(summary)}\n"
        f'<a href="{html.escape(link, quote=True)}">Read article</a>'
    )


# ---------------- PROCESS ----------------
def process_articles(articles, feed_name, chat_id, tags):

    for a in articles:

        link = a["link"]

        if exists(link):
            continue

        message = format_message(
            tags,
            a["title"],
            a["summary"],
            link
        )

        send_message(chat_id, message)

        save(link, a["title"], feed_name, a["published"])


# ---------------- MAIN ----------------
def main():

    for feed in FEEDS:

        name = feed["name"]
        url = feed["url"]
        feed_type = feed["type"]
        layout = feed.get("layout", "generic")

        chat_id = CHANNELS[feed["channel"]]
        tags = feed.get("tags", [])

        fetcher = get_source(feed_type)

        logging.info(f"Checking: {name}")

        articles = fetcher(url, layout)

        process_articles(
            articles,
            name,
            chat_id,
            tags
        )


if __name__ == "__main__":
    main()