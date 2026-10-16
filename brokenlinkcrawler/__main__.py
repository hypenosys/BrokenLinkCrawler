"""Allow launching with python -m brokenlinkcrawler."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
