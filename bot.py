import feedparser
import requests
import yaml
import html
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from config import TOKEN

BASE_DIR = Path(__file__).parent

SENT_FILE = BASE_DIR / "sent.json"

# cargar enviados
if SENT_FILE.exists():
    sent = set(json.loads(SENT_FILE.read_text(encoding="utf-8")))
else:
    sent = set()

# cargar feeds
with open(BASE_DIR / "feeds.yaml", encoding="utf-8") as f:
    feeds_config = yaml.safe_load(f)

# cargar canales
with open(BASE_DIR / "channels.yaml", encoding="utf-8") as f:
    channels_config = yaml.safe_load(f)

channels = channels_config["channels"]

for feed_info in feeds_config["feeds"]:
    print(f"Checking: {feed_info['name']}")

    feed = feedparser.parse(feed_info["url"])
    hashtags = " ".join(
        [f"#{tag}" for tag in feed_info["tags"]]
    )
    chat_id = channels[feed_info["channel"]]

    for entry in reversed(feed.entries):
        link = entry.link
        if link in sent:
            continue
        title = entry.title
        import re

        summary = getattr(entry, "summary", "")
        # quitar HTML
        summary_html = getattr(entry, "summary", "")
        soup = BeautifulSoup(summary_html, "html.parser")
        p = soup.find("p")
        if p:
            summary = p.get_text(strip=True)
        else:
            summary = ""
        summary = p.get_text(" ", strip=True)
        summary = summary [:250]

        message = (
            f"<b>{html.escape(hashtags)}</b>\n"
            f"<b>{html.escape(title)}</b>\n"
            f"{html.escape(summary)}\n"
            f'<a href="{html.escape(link, quote=True)}">Read article</a>'
        )

        telegram_url = (
            f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        )

        response = requests.post(
            telegram_url,
            data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
        )

        print(response.status_code, title)

        sent.add(link)

# guardar enviados
SENT_FILE.write_text(
    json.dumps(list(sent), indent=2),
    encoding="utf-8"
)

print("Done.")