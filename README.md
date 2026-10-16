# BrokenLinkCrawler

Python CLI for finding broken HTTP links on a site, with referring-page information.

## Install (Python 3.10+)

```sh
git clone https://github.com/hypenosys/BrokenLinkCrawler.git
cd BrokenLinkCrawler
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Run

```sh
brokenlinkcrawler https://example.com --max-pages 300 --max-links 10000 --timeout 10 --delay 0.2 --output report.json
```

The crawler checks internal HTML links and referenced assets (including srcset), follows internal redirects, and reports HTTP 404/410 targets with the pages that reference them. It refuses redirects to other origins, validates all resolved IPs as public, and connects to the validated IP directly while preserving the original hostname for TLS verification and the HTTP Host header. It respects robots.txt by default and rejects crawling if the robots policy cannot be retrieved. `--ignore-robots` is available for sites you own or have permission to test.

JSON output includes `results`, `broken`, `pages_checked`, and `truncated`. Exit code 1 means broken links were detected; 0 means none were detected within the scan limits. Review `INCONCLUSIVE` and `SKIPPED` results separately.

### Limitations

This is a bounded single-threaded crawler, **not a guarantee of complete site coverage**. It does not render JavaScript, parse CSS URLs, load sitemaps, or check off-site links. Per-request timeouts are not a global deadline. `--max-pages` limits HTML page discovery and `--max-links` limits URL checks. For untrusted sites, run it in a restricted network environment as an additional defense in depth.

Run tests with `python -m unittest discover -s tests -v`. GitHub Actions runs the same tests on pushes.
