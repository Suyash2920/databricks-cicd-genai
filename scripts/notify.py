#!/usr/bin/env python3
"""
Send the pipeline result to Microsoft Teams (Workflows webhook) or Slack (incoming webhook).

Usage:
  python scripts/notify.py --title "CD pipeline" --result CI=success --result QA=failure

Environment:
  NOTIFY_WEBHOOK_URL   Teams Workflows or Slack webhook URL (skipped if empty)
  RUN_URL              Link to the GitHub Actions run
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

OK_RESULTS = ("success", "skipped")


def build_facts(results):
    facts = [
        ("Repository", os.getenv("GITHUB_REPOSITORY", "local")),
        ("Branch", os.getenv("GITHUB_REF_NAME", "local")),
        ("Commit", (os.getenv("GITHUB_SHA") or "local")[:7]),
        ("Triggered by", os.getenv("GITHUB_ACTOR", "local")),
    ]
    return facts + [(name, value or "unknown") for name, value in results]


def teams_payload(title, passed, facts, run_url):
    card = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": f"{'PASSED' if passed else 'FAILED'}: {title}",
                "weight": "Bolder",
                "size": "Medium",
                "color": "Good" if passed else "Attention",
                "wrap": True,
            },
            {"type": "FactSet", "facts": [{"title": k, "value": v} for k, v in facts]},
        ],
    }
    if run_url:
        card["actions"] = [{"type": "Action.OpenUrl", "title": "Open pipeline run", "url": run_url}]
    return {
        "type": "message",
        "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}],
    }


def slack_payload(title, passed, facts, run_url):
    lines = [f"*{'PASSED' if passed else 'FAILED'}: {title}*"] + [f"{k}: {v}" for k, v in facts]
    if run_url:
        lines.append(run_url)
    return {"text": "\n".join(lines)}


def main():
    parser = argparse.ArgumentParser(description="Send pipeline result to Teams or Slack")
    parser.add_argument("--title", required=True)
    parser.add_argument("--result", action="append", default=[], help="NAME=RESULT, e.g. QA=success")
    args = parser.parse_args()

    results = [tuple(item.split("=", 1)) if "=" in item else (item, "") for item in args.result]
    passed = all(value in OK_RESULTS for _, value in results)
    facts = build_facts(results)
    run_url = os.getenv("RUN_URL", "")

    webhook = os.getenv("NOTIFY_WEBHOOK_URL", "").strip()
    if not webhook:
        print("::notice::NOTIFY_WEBHOOK_URL secret is not set - skipping Teams/Slack notification.")
        return 0
    host = urllib.parse.urlparse(webhook)
    if host.scheme != "https":
        print("::warning::NOTIFY_WEBHOOK_URL must start with https:// - notification not sent.")
        return 0

    is_slack = (host.hostname or "").endswith("hooks.slack.com")
    payload = (slack_payload if is_slack else teams_payload)(args.title, passed, facts, run_url)
    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    target = "Slack" if is_slack else "Teams"
    try:
        # Scheme is validated as https above (bandit B310 false positive).
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
            print(f"{target} notification sent (HTTP {response.status}).")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:300]
        print(f"::warning::{target} notification failed: HTTP {error.code} {body}")
    except OSError as error:
        print(f"::warning::{target} notification failed: {error}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
