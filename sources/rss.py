import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup

MAX_LEN = 250

def normalize_date(date_str):
    try:
        return parsedate_to_datetime(date_str).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_articles(url, layout=None):
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        link = entry.get("link", "")
        title = entry.get("title", "No title")
        summary = entry.get("summary", "") or entry.get("description", "")
        summary = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)
        published = normalize_date(entry.get("published"))

        if len(summary) > MAX_LEN:
            summary = summary[:MAX_LEN] + "..."

        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "published": published
        })

    return articles