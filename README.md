# AI Consumer Product Weekly Radar

An MVP automation system for tracking global consumer AI products focused on fun, social, content, video, live, avatar, UGC, meme/remix, interactive story, anime, and roleplay use cases.

The first version uses RSS, public web pages, YAML-configured sources, OpenAI JSON scoring, SQLite storage, Jinja2 HTML reports, GitHub Actions, GitHub Pages, and optional Feishu webhook pushes.

## Quick start

```bash
pip install -r requirements.txt
python src/main.py daily
python src/main.py weekly
```

Set environment variables when running with LLM scoring or push notifications:

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4.1-mini"
export FEISHU_WEBHOOK_URL="..."
export PUBLIC_REPORT_BASE_URL="https://<user>.github.io/<repo>"
```

If `OPENAI_API_KEY` is not set, the system falls back to a deterministic keyword-based scoring path so the pipeline remains runnable.

## Commands

```bash
python src/main.py daily
```

Fetches RSS and web sources, filters by keywords, scores items, and writes them into `data/radar.sqlite`.

```bash
python src/main.py weekly
```

Reads the past 7 days of scored items, generates `reports/YYYY-WW.html`, updates `reports/index.html`, and pushes a Feishu message when `FEISHU_WEBHOOK_URL` is configured.

## Configuration

Edit sources in `config/sources.yaml`.

Edit include/exclude keywords in `config/keywords.yaml`.

## GitHub Pages

This repo includes a GitHub Actions workflow at `.github/workflows/weekly.yml`.

It runs:

- Daily collector: every day at 01:00 UTC
- Weekly report: every Friday at 02:00 UTC
- Manual run: via `workflow_dispatch`

The weekly/manual run uploads `reports/` as a GitHub Pages artifact and deploys it automatically.

In GitHub, open repository settings:

1. Go to `Settings -> Pages`.
2. Set `Source` to `GitHub Actions`.
3. Save.

After the first successful weekly/manual workflow run, the latest report will be available at the Pages URL shown by the workflow deployment step.

## GitHub Secrets

Recommended secrets:

- `OPENAI_API_KEY`
- `FEISHU_WEBHOOK_URL`

Optional repository variable or secret:

- `PUBLIC_REPORT_BASE_URL`

Recommended repository variables:

- `OPENAI_MODEL`, default: `gpt-4.1-mini`
- `PUBLIC_REPORT_BASE_URL`, for example: `https://<user>.github.io/<repo>`

## Deploy checklist

1. Push this project to a GitHub repository.
2. Add `OPENAI_API_KEY` in `Settings -> Secrets and variables -> Actions -> Secrets`.
3. Add `FEISHU_WEBHOOK_URL` if Feishu push is needed.
4. Add `PUBLIC_REPORT_BASE_URL` in repository variables if you want Feishu messages to include a full report URL.
5. Enable GitHub Pages with `Source: GitHub Actions`.
6. Run `AI Consumer Radar Weekly` manually once from the Actions tab.
