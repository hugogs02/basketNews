import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import json

from sources.scraper_layouts import LAYOUTS


def get_articles(url, layout="generic"):

    try:
        response = requests.get(url, timeout=10)
    except Exception:
        return []

    html = response.content.decode(
        response.apparent_encoding,
        errors="replace"
    )

    soup = BeautifulSoup(html, "html.parser")
    config = LAYOUTS.get(layout, LAYOUTS["generic"])

    articles = []

    # =========================================================
    # 1. API MODE (GENÉRICO)
    # =========================================================
    if config.get("type") == "api":

        data = None

        # intento directo JSON
        try:
            data = response.json()
        except Exception:
            pass

        # fallback scripts (Next.js / SSR JSON embebido)
        if not data:
            for script in soup.find_all("script"):
                if script.string and "publication_date" in script.string:
                    try:
                        data = json.loads(script.string)
                        break
                    except Exception:
                        continue

        if not data:
            return []

        def find_items(obj):
            if isinstance(obj, dict):
                if "items" in obj and isinstance(obj["items"], list):
                    return obj["items"]
                for v in obj.values():
                    res = find_items(v)
                    if res:
                        return res
            elif isinstance(obj, list):
                return obj
            return None

        items = find_items(data)

        if not items:
            return []

        fields = config.get("fields", {})

        for item in items:

            title = item.get(fields.get("title", "title"), "")
            summary = item.get(fields.get("summary", "excerpt"), "")
            date = item.get(fields.get("date", "publication_date"), "")
            link = item.get(fields.get("link", "url"), "")

            base_url = config.get("base_url", url)

            if link and link.startswith("/"):
                link = urljoin(base_url, link)

            if not title or not link:
                continue

            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "published": (
                    date.replace("T", " ")
                        .replace("Z", "")
                        .replace("+02:00", "")
                )
            })

        return articles

    # =========================================================
    # 2. NEXT.JS MODE (LBA / LEGABASKET)
    # =========================================================
    if config.get("type") == "nextjs":

        script = soup.find("script", {"id": config.get("script_id", "__NEXT_DATA__")})

        if not script:
            return []

        try:
            data = json.loads(script.string)
        except Exception:
            return []

        def find_contents(obj):

            if isinstance(obj, dict):

                if "contents" in obj and isinstance(obj["contents"], list):
                    return obj["contents"]

                for value in obj.values():
                    res = find_contents(value)
                    if res:
                        return res

            elif isinstance(obj, list):

                for value in obj:
                    res = find_contents(value)
                    if res:
                        return res

            return None

        items = find_contents(data)

        if not items:
            return []

        base_url = config.get("base_url", url)
        base = base_url.rstrip("/")

        for item in items:

            permalink = item.get("permalink", "")
            item_id = item.get("id", "")

            if item_id and permalink:
                link = f"{base}/{item_id}/{permalink}"
            else:
                link = base_url + permalink

            articles.append({
                "title": item.get("title", ""),
                "link": link,
                "summary": item.get("abstract", ""),
                "published": item.get("publication_date", "")
            })

        return articles
    
    # =========================================================
    # 3. NEXT.JS POSTS MODE (EASYCREDIT BBL)
    # =========================================================
    if config.get("type") == "nextjs_posts":

        script = soup.find("script", id="__NEXT_DATA__")

        if not script or not script.string:
            return []

        try:
            data = json.loads(script.string)
        except Exception:
            return []

        def find_posts(obj):

            if isinstance(obj, dict):

                if "posts" in obj and isinstance(obj["posts"], list):
                    return obj["posts"]

                for value in obj.values():
                    res = find_posts(value)
                    if res:
                        return res

            elif isinstance(obj, list):

                for value in obj:
                    res = find_posts(value)
                    if res:
                        return res

            return None

        posts = find_posts(data)

        if not posts:
            return []

        for post in posts:

            title = post.get("postTitle", "")
            link = post.get("permalink", "")
            summary = post.get("postExcerpt", "")[:150] + "..."
            published = post.get("postPublished", "")

            if not title or not link:
                continue

            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "published": published
            })

        return articles

    # =========================================================
    # 3. HTML LAYOUT MODE
    # =========================================================
    if config.get("item"):

        items = soup.select(config["item"])

        for item in items:

            # ------------------------
            # TITLE
            # ------------------------
            title = ""
            if config.get("title"):
                el = item.select_one(config["title"])
                if el:
                    title = el.get_text(strip=True)

            if not title or len(title) < 10:
                continue

            # ------------------------
            # LINK
            # ------------------------
            link = ""

            if config.get("link"):
                el = item.select_one(config["link"])
                if el:
                    link = el.get("href", "")

            if not link:
                if item.name == "a":
                    link = item.get("href", "")
                else:
                    a = item.find("a")
                    if a:
                        link = a.get("href", "")

            if not link:
                continue

            # ------------------------
            # SUMMARY
            # ------------------------
            summary = ""
            if config.get("summary"):
                el = item.select_one(config["summary"])
                if el:
                    summary = el.get_text(" ", strip=True)

            summary = summary.strip()

            # ------------------------
            # DATE
            # ------------------------
            published = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if config.get("date"):
                el = item.select_one(config["date"])
                if el:
                    published = el.get_text(strip=True)

            articles.append({
                "title": title,
                "link": urljoin(url, link),
                "summary": summary,
                "published": published
            })

        return articles

    # =========================================================
    # 4. GENERIC MODE (FALLBACK FINAL)
    # =========================================================
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