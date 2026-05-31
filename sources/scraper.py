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

    if config.get("type") == "api":
        r = requests.get(
            "https://backoffice.prod.acb.com/api/pages/"
            "?type=news.ArticlePage"
            "&fields=short_title,excerpt,first_published_at,url"
            "&limit=20"
            "&offset=0"
            "&order=-first_published_at",
            timeout=10
        )

        data = r.json()
        items = (
            data.get("items")
            or data.get("results")
            or data.get("data")
            or []
        )

        print("ACB ITEMS:", len(items))

        for item in items:

            link = item.get("url", "")
            if link.startswith("/"):
                link = "https://acb.com" + link

            articles.append({
                "title": item.get("short_title", ""),
                "link": link,
                "summary": item.get("excerpt", ""),
                "published": (
                    item.get("first_published_at", "")
                    .replace("T", " ")
                    .replace("Z", "")
                )
            })

        return articles

    # Layout
    if config.get("item"):
        items = soup.select(config["item"])

        for item in items:

            # ------------------------
            # LINK (SIEMPRE desde <a>)
            # ------------------------
            link = item.get("href", "")

            # ------------------------
            # TITLE
            # ------------------------
            title_el = item.select_one("h3")
            title = title_el.get_text(strip=True) if title_el else ""

            if not title:
                continue

            # ------------------------
            # SUMMARY
            # ------------------------
            summary_el = item.select_one("p")
            summary = summary_el.get_text(" ", strip=True) if summary_el else ""

            articles.append({
                "title": title,
                "link": urljoin(url, link),
                "summary": summary,
                "published": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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