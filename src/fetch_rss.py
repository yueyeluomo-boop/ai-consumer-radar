from __future__ import annotations

from datetime import datetime, timezone

import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from models import Item


def clean_html(value: str | None) -> str:
    if not value:
        return ""
    return BeautifulSoup(value, "html.parser").get_text(" ", strip=True)


def parse_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = date_parser.parse(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.isoformat()


def fetch_rss_sources(sources: list[dict]) -> list[Item]:
    items: list[Item] = []
    for source in sources:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries:
            title = clean_html(entry.get("title")) or "Untitled"
            url = entry.get("link")
            if not url:
                continue
            raw_text = clean_html(
                entry.get("summary")
                or entry.get("description")
                or entry.get("content", [{}])[0].get("value")
            )
            published = (
                entry.get("published")
                or entry.get("updated")
                or datetime.now(timezone.utc).isoformat()
            )
            items.append(
                Item(
                    source_name=source["name"],
                    source_type=source.get("type", "rss"),
                    title=title,
                    url=url,
                    published_at=parse_date(published),
                    raw_text=raw_text,
                )
            )
    return items
