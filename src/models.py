from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    source_name: str
    source_type: str
    title: str
    url: str
    published_at: str | None
    raw_text: str
    summary: str | None = None
    product_name: str | None = None
    category: str | None = None
    score: int | None = None
    reason: str | None = None
    is_consumer_ai: bool | None = None
    is_ai_for_fun: bool | None = None
    experience_innovation: str | None = None
    why_it_matters: str | None = None
