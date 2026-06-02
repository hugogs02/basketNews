LAYOUTS = {
    "feb_v1": {
        "item": "div.nodo",
        "title": "h2.titulo a",
        "link": "h2.titulo a",
        "summary": "div.entradilla"
    },

    "acb_v1": {
        "item": "a[data-testid='article-card-link']"
    },

    "lbf_v1": {
        "item": "div.row",
        "title": "span.news_title",
        "link": "div.archiveTile_Title a",
        "summary": "span.news_text",
        "date": "span.news_Date"
    },

    "ffbb_v1": {
        "item": "section.main__news-list__entry",
        "title": "h3",
        "link": "div.main__news-list__content a",
        "summary": "div.main__news-list__content p:not(.news__date)",
        "date": "p.news__date"
    },

    "lba_v1": {
        "type": "nextjs",
        "script_id": "__NEXT_DATA__",
        "base_url": "https://www.legabasket.it/news/"
    },

    "easycredit_bbl": {
        "type": "nextjs_posts"
    },

    "generic": {
        "item": None
    }
}