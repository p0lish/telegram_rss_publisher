import logging
import time
import feedparser
import requests

logger = logging.getLogger(__name__)

SCRAPE_TIMEOUT = 5


def normalize_tag(tag: str) -> str:
    return f'#{tag.strip().lower().replace(" ", "_").replace("-", "_")}'


def get_tags_from_meta(url: str) -> list[str]:
    """Scrape meta keywords from article page for rich tags."""
    try:
        resp = requests.get(url, timeout=SCRAPE_TIMEOUT, headers={
            "User-Agent": "TelexBot/1.0"
        })
        resp.raise_for_status()
        # Simple extraction without BeautifulSoup
        import re
        match = re.search(
            r'<meta\s+name=["\']keywords["\']\s+content=["\']([^"\']+)["\']',
            resp.text,
            re.IGNORECASE
        )
        if match:
            raw = match.group(1).split(",")
            return list({normalize_tag(t) for t in raw if t.strip()})
    except Exception as e:
        logger.debug(f"Tag scrape failed for {url}: {e}")
    return []


def get_tags_from_entry(entry) -> list[str]:
    """Extract tags from RSS entry metadata as fallback."""
    try:
        raw_tags = entry.get("tags", [])
        return list({normalize_tag(t["term"]) for t in raw_tags if t.get("term")})
    except (AttributeError, KeyError, TypeError):
        return []


def get_news_list(url: str) -> list[dict]:
    feed = feedparser.parse(url)

    if feed.bozo and not feed.entries:
        raise RuntimeError(f"RSS parse failed: {feed.bozo_exception}")

    entries = sorted(
        feed.entries,
        key=lambda e: e.get("published_parsed", time.gmtime(0))
    )

    results = []
    for entry in entries:
        link = entry.get("link", "")
        if not link:
            continue

        # Try rich tags from HTML, fall back to RSS tags
        tags = get_tags_from_meta(link) or get_tags_from_entry(entry)

        results.append({
            "title": entry.get("title", "Untitled"),
            "timestamp": int(time.mktime(entry.published_parsed)) if entry.get("published_parsed") else 0,
            "url": link,
            "tags": " ".join(tags),
        })

    return results


if __name__ == "__main__":
    import json
    news = get_news_list("https://telex.hu/rss")
    print(json.dumps(news[:3], indent=2, ensure_ascii=False))
