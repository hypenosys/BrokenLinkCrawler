"""Conservative same-origin crawler. Refuses non-public IP destinations and redirects."""
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag
import ipaddress
import socket
import urllib.request
import urllib.error

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        for attr in (("href",) if tag in ("a", "link") else ("src",) if tag in ("img", "script", "iframe") else ()):
            if data.get(attr):
                self.links.append(data[attr])

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def public_host(host):
    try:
        addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    return bool(addresses) and all(ipaddress.ip_address(a[4][0]).is_global for a in addresses)

def crawl(start, max_pages=100, timeout=10):
    parsed = urlsplit(start)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Expected an HTTP(S) URL without credentials")
    origin = (parsed.scheme, parsed.hostname.lower(), parsed.port)
    pending = deque([start]); visited = set(); checked = {}; references = {}
    opener = urllib.request.build_opener(NoRedirect, urllib.request.ProxyHandler({}))
    while pending and len(visited) < max_pages:
        url = urldefrag(pending.popleft())[0]
        if url in visited:
            continue
        p = urlsplit(url)
        if (p.scheme, (p.hostname or "").lower(), p.port) != origin:
            continue
        visited.add(url)
        if not public_host(p.hostname):
            checked[url] = {"status": "BLOCKED", "reason": "non-public or unresolved host"}
            continue
        try:
            with opener.open(urllib.request.Request(url, headers={"User-Agent": "BrokenLinkCrawler/0.1"}), timeout=timeout) as resp:
                status = resp.status
                kind = resp.headers.get_content_type()
                body = resp.read(2_000_000) if kind == "text/html" else b""
            checked[url] = {"status": "OK", "http_status": status}
            if body:
                parser = Links(); parser.feed(body.decode("utf-8", "replace"))
                for link in parser.links:
                    target = urldefrag(urljoin(url, link))[0]
                    t = urlsplit(target)
                    if (t.scheme, (t.hostname or "").lower(), t.port) != origin:
                        continue
                    references.setdefault(target, []).append(url)
                    if target not in visited:
                        pending.append(target)
        except urllib.error.HTTPError as exc:
            checked[url] = {"status": "BROKEN" if exc.code in (404, 410) else "INCONCLUSIVE", "http_status": exc.code}
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            checked[url] = {"status": "INCONCLUSIVE", "reason": type(exc).__name__}
    return {"start": start, "pages_checked": len(visited), "truncated": bool(pending), "results": checked,
            "broken": [{"url": u, "sources": references.get(u, []), **r} for u, r in checked.items() if r["status"] == "BROKEN"]}
