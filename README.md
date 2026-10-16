# BrokenLinkCrawler

Experimental Python crawler for same-origin 404/410 link checks.

Install: `python -m pip install -e .`

Run: `brokenlinkcrawler https://example.com --max-pages 100 --output report.json`

Tests: `python -m unittest discover -s tests -v`

Limitations: no sitemap, robots.txt, external links, JavaScript rendering, or production-grade DNS pinning. DNS rebinding remains possible. Only use on trusted targets in a controlled environment. No stable release is claimed.
