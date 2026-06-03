import yaml
import requests
import html
import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import TOKEN
from db import init_db, exists, save
from sources.dispatcher import get_source

init_db()

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

#Logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

handler = RotatingFileHandler(
    LOG_DIR / "bot.log", 
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=2,
    encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[handler]
)

# Configurations
with open("feeds.yaml", "r", encoding="utf-8") as f:
    FEEDS = yaml.safe_load(f)

with open("channels.yaml", "r", encoding="utf-8") as f:
    CHANNELS = yaml.safe_load(f)["channels"]


# Telegram sender
def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    r = requests.post(BASE_URL, data=payload)
    logging.info(f"Telegram: {r.status_code} | {text[:80]}")


# Format Telegram message
def format_message(tags, title, summary, link):
    hashtags = " ".join(f"#{t.replace(' ', '')}" for t in tags)

    return (
        f"<b>{html.escape(hashtags)}</b>\n"
        f"<b>{html.escape(title)}</b>\n"
        f"{html.escape(summary)}\n"
        f'<a href="{html.escape(link, quote=True)}">Read article</a>'
    )


# Process articles
def process_articles(articles, feed_name, chat_id, tags):
    for a in articles:
        link = a["link"]

        if exists(link): continue

        message = format_message(tags, a["title"], a["summary"], link)
        send_message(chat_id, message)
        save(link, a["title"], feed_name, a["published"])


def main():
    for feed in FEEDS:
        name = feed["name"]
        url = feed["url"]
        feed_type = feed["type"]
        layout = feed.get("layout", "generic")

        chat_id = CHANNELS[feed["channel"]]
        tags = feed.get("tags", [])

        fetcher = get_source(feed_type)
        articles = fetcher(url, layout)
        articles = list(reversed(articles))

        logging.info(f"Checking: {name}")
        process_articles(articles, name, chat_id, tags)


if __name__ == "__main__":
    main()