from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import REPORTS_DIR, TEMPLATES_DIR
from summarize import build_report_context


def generate_weekly_report(items: list[dict], now: datetime | None = None) -> tuple[str, str]:
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    iso_year, iso_week, _ = now.isocalendar()
    filename = f"{iso_year}-W{iso_week:02d}.html"

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("weekly_report.html.j2")
    extra = build_report_context(items)
    html = template.render(
        start_date=start.date().isoformat(),
        end_date=now.date().isoformat(),
        top_items=items,
        generated_at=now.isoformat(),
        **extra,
    )

    report_path = REPORTS_DIR / filename
    report_path.write_text(html, encoding="utf-8")
    (REPORTS_DIR / "index.html").write_text(html, encoding="utf-8")
    return filename, str(report_path)
