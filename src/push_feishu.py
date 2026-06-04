from __future__ import annotations

import os

import requests


def push_feishu_report(filename: str, item_count: int) -> None:
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    if not webhook_url:
        print("FEISHU_WEBHOOK_URL not set, skip push")
        return

    base_url = os.getenv("PUBLIC_REPORT_BASE_URL", "").rstrip("/")
    report_url = f"{base_url}/{filename}" if base_url else filename
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"AI for Fun 全球消费产品周报已生成：{report_url}\n本周候选：{item_count} 个"
        },
    }
    response = requests.post(webhook_url, json=payload, timeout=20)
    response.raise_for_status()
