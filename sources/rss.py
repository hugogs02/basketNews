import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

MAX_LEN = 250

def get_articles(url, layout=None):
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        link = entry.get("link", "")
        title = entry.get("title", "No title")
        published = entry.get("published") or datetime.now().strftime("%Y-%m-%d %H:%M")
        summary = entry.get("summary", "") or entry.get("description", "")
        summary = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)

        if len(summary) > MAX_LEN:
            summary = summary[:MAX_LEN] + "..."

        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "published": published
        })

    return articles