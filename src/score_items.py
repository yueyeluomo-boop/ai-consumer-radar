from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import OpenAI

from models import Item


PROMPT = """你是一个消费级 AI 产品研究员。
请判断下面的信息是否值得进入「AI for Fun 全球消费产品周报」。

只关注：
- AI 社交
- AI 陪伴
- AI 视频消费
- AI 直播互动
- AI 虚拟主播
- AI avatar
- AI UGC
- AI meme / remix
- AI 互动剧情
- AI 二次元 / 角色扮演
- 其他普通用户可体验的 AI 娱乐产品

排除：
- AI for work
- 企业服务
- 办公效率
- 编程工具
- 客服
- CRM
- 文档总结
- 会议助手
- 数据分析

请只输出 JSON：
{{
  "is_consumer_ai": true/false,
  "is_ai_for_fun": true/false,
  "product_name": "",
  "category": "",
  "summary": "",
  "experience_innovation": "",
  "why_it_matters": "",
  "score": 1-10,
  "reason": ""
}}

待分析内容：
标题：{title}
正文：{raw_text}
链接：{url}
"""


def score_items(items: list[Item], keywords: dict[str, list[str]]) -> list[Item]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return [heuristic_score(item, keywords) for item in items]

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    scored: list[Item] = []
    for item in items:
        try:
            result = score_one_with_openai(client, model, item)
        except Exception as exc:
            print(f"fallback score for {item.url}: {exc}")
            result = heuristic_payload(item, keywords)
        apply_score(item, result)
        scored.append(item)
    return scored


def score_one_with_openai(client: OpenAI, model: str, item: Item) -> dict[str, Any]:
    prompt = PROMPT.format(
        title=item.title[:500],
        raw_text=item.raw_text[:6000],
        url=item.url,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def heuristic_score(item: Item, keywords: dict[str, list[str]]) -> Item:
    apply_score(item, heuristic_payload(item, keywords))
    return item


def heuristic_payload(item: Item, keywords: dict[str, list[str]]) -> dict[str, Any]:
    text = f"{item.title}\n{item.raw_text}".lower()
    include_hits = [word for word in keywords.get("include", []) if word in text]
    exclude_hits = [word for word in keywords.get("exclude", []) if word in text]
    score = min(10, max(1, 4 + len(include_hits) * 2 - len(exclude_hits) * 3))
    is_fun = bool(include_hits) and not exclude_hits
    return {
        "is_consumer_ai": is_fun,
        "is_ai_for_fun": is_fun,
        "product_name": guess_product_name(item.title),
        "category": guess_category(text),
        "summary": item.raw_text[:220] or item.title,
        "experience_innovation": "需要人工体验确认；当前基于公开文本和关键词初筛。",
        "why_it_matters": "命中了消费娱乐 AI 相关关键词，适合进入候选池继续追踪。",
        "score": score,
        "reason": f"keyword hits: {', '.join(include_hits[:6])}" if include_hits else "no keyword hit",
    }


def apply_score(item: Item, payload: dict[str, Any]) -> None:
    item.is_consumer_ai = bool(payload.get("is_consumer_ai"))
    item.is_ai_for_fun = bool(payload.get("is_ai_for_fun"))
    item.product_name = str(payload.get("product_name") or item.title)[:200]
    item.category = str(payload.get("category") or "Uncategorized")[:120]
    item.summary = str(payload.get("summary") or item.raw_text or item.title)[:1000]
    item.experience_innovation = str(payload.get("experience_innovation") or "")[:1000]
    item.why_it_matters = str(payload.get("why_it_matters") or "")[:1000]
    try:
        item.score = max(1, min(10, int(payload.get("score", 1))))
    except (TypeError, ValueError):
        item.score = 1
    item.reason = str(payload.get("reason") or "")[:1000]


def guess_product_name(title: str) -> str:
    cleaned = re.split(r"[-|:]", title, maxsplit=1)[0].strip()
    return cleaned or title


def guess_category(text: str) -> str:
    category_rules = [
        ("AI companion", ["companion", "girlfriend", "boyfriend", "character ai", "roleplay"]),
        ("AI video", ["video", "avatar", "shorts", "reels"]),
        ("AI social", ["social", "community", "chat"]),
        ("AI live / streamer", ["live", "streaming", "streamer", "vtuber", "virtual influencer"]),
        ("AI meme / remix", ["meme", "remix"]),
        ("AI anime / roleplay", ["anime", "npc", "roleplay"]),
    ]
    for category, terms in category_rules:
        if any(term in text for term in terms):
            return category
    return "Consumer AI entertainment"
