import yaml
import feedparser
import requests
import html
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from config import TOKEN
from db import init_db, exists, save

init_db()

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
MAX_LEN = 250

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# LOAD CONFIG
with open("feeds.yaml", "r", encoding="utf-8") as f:
    FEEDS = yaml.safe_load(f)

with open("channels.yaml", "r", encoding="utf-8") as f:
    CHANNELS = yaml.safe_load(f)


# TELEGRAM SEND
def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    r = requests.post(BASE_URL, data=payload)
    logging.info(f"Telegram response: {r.status_code} | {text[:80]}")


# FORMAT MESSAGE
def format_message(hashtags, title, summary, link):
    return (
        f"<b>{html.escape(hashtags)}</b>\n"
        f"<b>{html.escape(title)}</b>\n"
        f"{html.escape(summary)}\n"
        f'<a href="{html.escape(link, quote=True)}">Read article</a>'
    )


# FETCH FEED
def fetch_feed(feed_name, feed_url, chat_id, tags):
    logging.info(f"Checking: {feed_name}")
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        link = entry.get("link", "")
        title = entry.get("title", "No title")
        published = entry.get("published")
        if not published:
            published = datetime.now().strftime("%Y-%m-%d %H:%M")

        summary = entry.get("summary", "") or entry.get("description", "")
        summary = BeautifulSoup(summary,"html.parser").get_text(" ", strip=True)
        summary = summary[:MAX_LEN] + "..." if len(summary) > MAX_LEN else summary

        hashtags = " ".join(f"#{tag.replace(' ', '_')}" for tag in tags)

        if exists(link):
            continue

        message = format_message(hashtags=hashtags, title=title, summary=summary, link=link)

        send_message(chat_id, message)

        save(link, title, feed_name, published)


# MAIN LOOP
def main():
    for feed in FEEDS:
        name = feed["name"]
        url = feed["url"]
        chat_id = CHANNELS[feed["channel"]]
        tags = feed.get("tags", [])

        fetch_feed(name, url, chat_id, tags)

if __name__ == "__main__":
    main()