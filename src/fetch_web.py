from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from models import Item


HEADERS = {
    "User-Agent": "AIConsumerRadar/0.1 (+https://github.com/)",
}


def fetch_web_sources(sources: list[dict]) -> list[Item]:
    items: list[Item] = []
    for source in sources:
        try:
            response = requests.get(source["url"], headers=HEADERS, timeout=20)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"skip web source {source['name']}: {exc}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        candidates = soup.select("article") or soup.select("main a") or soup.select("a")
        seen: set[str] = set()

        for candidate in candidates[:80]:
            anchor = candidate if candidate.name == "a" else candidate.find("a", href=True)
            if not anchor or not anchor.get("href"):
                continue
            title = " ".join(anchor.get_text(" ", strip=True).split())
            if len(title) < 8:
                continue
            url = urljoin(source["url"], anchor["href"])
            if url in seen:
                continue
            seen.add(url)
            text = " ".join(candidate.get_text(" ", strip=True).split())[:2000]
            items.append(
                Item(
                    source_name=source["name"],
                    source_type=source.get("type", "web"),
                    title=title[:300],
                    url=url,
                    published_at=datetime.now(timezone.utc).isoformat(),
                    raw_text=text or title,
                )
            )
    return items
