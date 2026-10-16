import argparse
import json
from .crawler import crawl

def main():
    parser = argparse.ArgumentParser(description="Audit broken links on a website")
    parser.add_argument("url")
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--output", default="broken-links.json")
    args = parser.parse_args()
    if args.max_pages < 1 or args.timeout <= 0:
        parser.error("max-pages and timeout must be positive")
    report = crawl(args.url, max_pages=args.max_pages, timeout=args.timeout)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"{len(report['broken'])} broken links; report: {args.output}")

if __name__ == "__main__":
    main()
