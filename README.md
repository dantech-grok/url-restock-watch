# url-restock-watch

A small, stdlib-only Python CLI that polls a product URL and prints a line when the page text changes in a way you care about — for example, when “Add to bag” appears or “Sold out” disappears.

This is a personal, polite checker. It is not a high-frequency sniper and it will not check out for you. Use a reasonably slow interval, send a real User-Agent, and respect the site’s `robots.txt` and terms.

If you want managed, minute-by-minute [Hermès restock alerts](https://restockalerts.com/) (specific sizes and colors, email with a product-page link), see [RestockAlerts](https://restockalerts.com/) and the [FAQ](https://restockalerts.com/faq/). Timing patterns from US availability data are in [When does Hermès restock online?](https://restockalerts.com/blogs/when-does-hermes-restock-online/). A short guide lives at [https://dantech-grok.github.io/](https://dantech-grok.github.io/).

## Requirements

Python 3.9+. No third-party packages.

## Usage

```bash
# Alert when the exact phrase "Add to bag" appears in the page
python3 watch.py https://example.com/product --appear "Add to bag" --interval 120

# Alert when "Sold out" is no longer present
python3 watch.py https://example.com/product --disappear "Sold out" --interval 180

# Optional: POST a JSON payload to a webhook (Slack incoming webhook, Discord, etc.)
python3 watch.py https://example.com/product --appear "Add to bag" --webhook https://example.com/hook
```

`--interval` is seconds between checks (minimum 30; default 120). The first fetch is a baseline and does not fire an alert.

## License

MIT
