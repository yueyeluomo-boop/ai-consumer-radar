from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from config import DB_PATH, ensure_runtime_dirs, load_keywords, load_sources
from db import connect, fetch_weekly_items, insert_items
from fetch_rss import fetch_rss_sources
from fetch_web import fetch_web_sources
from filtering import keyword_filter
from generate_report import generate_weekly_report
from push_feishu import push_feishu_report
from score_items import score_items


def run_daily() -> None:
    ensure_runtime_dirs()
    sources = load_sources()
    keywords = load_keywords()

    rss_items = fetch_rss_sources(sources.get("rss_sources", []))
    web_items = fetch_web_sources(sources.get("web_sources", []))
    candidates = keyword_filter(rss_items + web_items, keywords)
    scored = score_items(candidates, keywords)

    with connect(DB_PATH) as conn:
        inserted = insert_items(conn, scored)

    print(
        f"daily complete: fetched={len(rss_items) + len(web_items)} "
        f"candidates={len(candidates)} inserted={inserted}"
    )


def run_weekly() -> None:
    ensure_runtime_dirs()
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)

    with connect(DB_PATH) as conn:
        rows = fetch_weekly_items(conn, start.isoformat(), min_score=6)

    items = [dict(row) for row in rows]
    filename, path = generate_weekly_report(items, now=now)
    push_feishu_report(filename, len(items))
    print(f"weekly complete: report={path} items={len(items)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Consumer Product Weekly Radar")
    parser.add_argument("command", choices=["daily", "weekly"], help="pipeline command")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "daily":
        run_daily()
    elif args.command == "weekly":
        run_weekly()


if __name__ == "__main__":
    main()
