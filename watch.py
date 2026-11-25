#!/usr/bin/env python3
"""Poll a product URL and print a line when availability-related text changes."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

MIN_INTERVAL = 30
DEFAULT_INTERVAL = 120
USER_AGENT = "url-restock-watch/0.1 (+https://github.com/dantech-grok/url-restock-watch)"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url: str, timeout: int) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def present(haystack: str, needle: str, ignore_case: bool) -> bool:
    if ignore_case:
        return needle.lower() in haystack.lower()
    return needle in haystack


def notify(message: str, webhook: str | None) -> None:
    print(message, flush=True)
    if not webhook:
        return
    body = json.dumps({"text": message, "content": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except urllib.error.URLError as exc:
        print(f"{now()} webhook failed: {exc}", file=sys.stderr, flush=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Watch a URL for restock-related text changes.")
    p.add_argument("url", help="Product page URL to poll")
    p.add_argument("--appear", help="Alert when this text appears on the page")
    p.add_argument("--disappear", help="Alert when this text is no longer on the page")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="Seconds between checks (min 30, default 120)")
    p.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    p.add_argument("--ignore-case", action="store_true", help="Case-insensitive matching")
    p.add_argument("--webhook", help="Optional webhook URL to POST when an alert fires")
    args = p.parse_args()

    if not args.appear and not args.disappear:
        p.error("provide --appear and/or --disappear")
    interval = max(args.interval, MIN_INTERVAL)
    if args.interval < MIN_INTERVAL:
        print(f"{now()} interval raised to {MIN_INTERVAL}s", file=sys.stderr)

    print(f"{now()} watching {args.url} every {interval}s", flush=True)
    baseline_set = False
    last_appear = None
    last_disappear = None

    while True:
        try:
            html = fetch(args.url, args.timeout)
        except Exception as exc:  # noqa: BLE001 — keep the loop alive on network errors
            print(f"{now()} fetch failed: {exc}", file=sys.stderr, flush=True)
            time.sleep(interval)
            continue

        if args.appear:
            is_there = present(html, args.appear, args.ignore_case)
            if baseline_set and is_there and not last_appear:
                notify(f"{now()} APPEARED {args.appear!r} on {args.url}", args.webhook)
            last_appear = is_there
        if args.disappear:
            is_there = present(html, args.disappear, args.ignore_case)
            if baseline_set and (not is_there) and last_disappear:
                notify(f"{now()} DISAPPEARED {args.disappear!r} on {args.url}", args.webhook)
            last_disappear = is_there

        if not baseline_set:
            print(f"{now()} baseline ready", flush=True)
            baseline_set = True
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
