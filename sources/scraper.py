import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

from sources.scraper_layouts import LAYOUTS


def get_articles(url, layout="generic"):
    response = requests.get(url, timeout=10)
    html = response.content.decode(response.apparent_encoding, errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    config = LAYOUTS.get(layout, LAYOUTS["generic"])
    articles = []

    # Layout
    if config.get("item"):
        items = soup.select(config["item"])

        for item in items:
            title_el = item.select_one(config["title"])
            link_el = item.select_one(config["link"])
            summary_el = item.select_one(config.get("summary"))

            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            link = link_el.get("href", "")

            summary = ""
            if summary_el:
                summary = summary_el.get_text(" ", strip=True)

            articles.append({
                "title": title,
                "link": urljoin(url, link),
                "summary": summary,
                "published": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

        return articles

    # Generic mode
    links = soup.find_all("a")
    seen = set()

    for a in links:
        title = a.get_text(" ", strip=True)
        link = a.get("href", "")

        if not title or len(title) < 15:
            continue

        if link in seen:
            continue

        seen.add(link)

        articles.append({
            "title": title,
            "link": urljoin(url, link),
            "summary": "",
            "published": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    return articles