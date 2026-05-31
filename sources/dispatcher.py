from sources import rss, scraper


def get_source(type_name):

    if type_name == "rss":
        return rss.get_articles

    if type_name == "scraper":
        return scraper.get_articles

    raise ValueError(f"Unknown type: {type_name}")