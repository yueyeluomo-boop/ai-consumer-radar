from __future__ import annotations

from models import Item


def keyword_filter(items: list[Item], keywords: dict[str, list[str]]) -> list[Item]:
    include = keywords.get("include", [])
    exclude = keywords.get("exclude", [])
    kept: list[Item] = []

    for item in items:
        text = f"{item.title}\n{item.raw_text}".lower()
        include_hit = any(word in text for word in include)
        exclude_hit = any(word in text for word in exclude)
        if include_hit and not exclude_hit:
            kept.append(item)

    return kept
