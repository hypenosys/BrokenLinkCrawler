import argparse
import json
import sys
from .crawler import crawl
from .report import write_readable_reports, broken_occurrences

def main():
    parser = argparse.ArgumentParser(description="Audit broken links on a website")
    parser.add_argument("url", help="HTTP(S) URL to start from")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum HTML pages to discover")
    parser.add_argument("--max-links", type=int, default=10000, help="Maximum URLs to check")
    parser.add_argument("--timeout", type=float, default=10, help="Per-request timeout in seconds")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between requests in seconds")
    parser.add_argument("--ignore-robots", action="store_true", help="Ignore robots.txt (only with permission)")
    parser.add_argument("--output", default="broken-links.json")
    args = parser.parse_args()
    def progress(event, **details):
        print(event, details, file=sys.stderr, flush=True)
    if args.max_pages < 1 or args.max_links < 1 or args.timeout <= 0 or args.delay < 0:
        parser.error("max-pages, max-links and timeout must be positive; delay must be nonnegative")
    try:
        report = crawl(args.url, max_pages=args.max_pages, max_links=args.max_links,
                       timeout=args.timeout, delay=args.delay, respect_robots=not args.ignore_robots, progress=progress)
    except ValueError as exc:
        parser.error(str(exc))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    txt_path, html_path, csv_path, pdf_path = write_readable_reports(report, args.output)
    print(f"Enlaces rotos: {len(report['broken'])} | Apariciones: {len(broken_occurrences(report))} | URLs comprobadas: {report['pages_checked']}")
    print(f"JSON: {args.output} | TXT: {txt_path} | HTML: {html_path} | CSV: {csv_path} | PDF: {pdf_path}")
    if report["truncated"]:
        print("WARNING: scan truncated by configured limits")
    return 1 if report["broken"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
