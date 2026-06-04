from __future__ import annotations

from collections import Counter, defaultdict


def build_report_context(items: list[dict]) -> dict:
    category_counts = Counter(item.get("category") or "Uncategorized" for item in items)
    top_categories = [name for name, _ in category_counts.most_common(3)]

    insights = []
    if items:
        insights.append(f"本周共筛出 {len(items)} 个 AI for Fun 候选，最高分 {max(item['score'] for item in items)}/10。")
        insights.append("主要集中在：" + "、".join(top_categories) + "。")
        insights.append("建议优先体验高分产品，确认其真实互动质量、内容生成速度和用户留存线索。")
    else:
        insights.append("本周暂未筛出 score >= 6 的 AI for Fun 候选，需要扩充更垂直的产品源。")

    observations = build_observations(items)
    next_week = [
        "补充 TikTok / YouTube / Discord / X 上的 AI 视频、虚拟主播和角色互动来源。",
        "对高分产品做一次人工试用，记录 onboarding、互动闭环和付费点。",
        "优化关键词，降低 AI for work 和通用技术新闻的误入率。",
    ]

    return {
        "insights": insights,
        "observations": observations,
        "next_week": next_week,
    }


def build_observations(items: list[dict]) -> list[str]:
    if not items:
        return ["暂无足够样本形成稳定观察。"]

    by_category = defaultdict(list)
    for item in items:
        by_category[item.get("category") or "Uncategorized"].append(item)

    observations = []
    for category, category_items in list(by_category.items())[:5]:
        names = [item.get("product_name") or item.get("title") for item in category_items[:3]]
        observations.append(f"{category} 方向出现 {len(category_items)} 个候选：{', '.join(names)}。")
    return observations
