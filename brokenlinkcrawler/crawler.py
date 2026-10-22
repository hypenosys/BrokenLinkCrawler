"""Bounded, DNS-pinned crawler for HTTP(S) websites."""
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urldefrag, urlunsplit
from urllib.robotparser import RobotFileParser
import http.client
import ipaddress
import socket
import ssl
import time

AGENT = "BrokenLinkCrawler/0.2 (+link-audit)"
REDIRECTS = (301, 302, 303, 307, 308)
PAGE_TAGS = {"a": "href", "iframe": "src"}
RESOURCE_TAGS = {"img": "src", "script": "src", "link": "href", "source": "src", "video": "src", "audio": "src"}
MAX_BYTES = 2_000_000

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.pages = []
        self.base = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "base" and self.base is None and data.get("href"):
            self.base = data["href"]
        attr = PAGE_TAGS.get(tag) or RESOURCE_TAGS.get(tag)
        if attr and data.get(attr):
            self.links.append(data[attr])
            if tag in PAGE_TAGS:
                self.pages.append(data[attr])
        if tag in ("img", "source") and data.get("srcset"):
            for candidate in data["srcset"].split(","):
                src = candidate.strip().split()
                if src:
                    self.links.append(src[0])

def canonical(url):
    url = urldefrag(url)[0]
    p = urlsplit(url)
    if p.scheme.lower() not in ("http", "https") or not p.hostname or p.username is not None or p.password is not None:
        raise ValueError("Only HTTP(S) URLs without credentials are allowed")
    try:
        port = p.port
    except ValueError as exc:
        raise ValueError("Invalid port") from exc
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Invalid port")
    host = p.hostname.lower().rstrip(".")
    if "%" in host:
        raise ValueError("IPv6 zone identifiers are not allowed")
    # Reject non-standard numeric host forms rather than letting the OS reinterpret them.
    if host.replace(".", "").isdigit() and not _valid_ip(host):
        raise ValueError("Ambiguous numeric host")
    netloc = ("[" + host + "]") if ":" in host else host
    if port and port != (443 if p.scheme.lower() == "https" else 80):
        netloc += ":" + str(port)
    return urlunsplit((p.scheme.lower(), netloc, p.path or "/", p.query, ""))

def _valid_ip(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

def origin(url):
    p = urlsplit(url)
    return (p.scheme, p.hostname, p.port or (443 if p.scheme == "https" else 80))

def resolve_public(host, port):
    """Resolve once for this request; return the exact vetted address to connect to."""
    addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not addresses:
        raise ValueError("No DNS addresses")
    ips = []
    for item in addresses:
        ip = ipaddress.ip_address(item[4][0])
        if not ip.is_global:
            raise ValueError("Non-public address rejected")
        ips.append(str(ip))
    return ips[0]

def public_host(host):
    try:
        return bool(resolve_public(host, 443))
    except (OSError, ValueError):
        return False

class PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, ip, timeout):
        super().__init__(host, port, timeout=timeout)
        self.ip = ip

    def connect(self):
        self.sock = socket.create_connection((self.ip, self.port), self.timeout)

class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, port, ip, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self.ip = ip

    def connect(self):
        sock = socket.create_connection((self.ip, self.port), self.timeout)
        try:
            self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
        except BaseException:
            sock.close()
            raise

def request(url, timeout=10, method="GET", max_bytes=MAX_BYTES):
    p = urlsplit(canonical(url))
    port = p.port or (443 if p.scheme == "https" else 80)
    ip = resolve_public(p.hostname, port)
    cls = PinnedHTTPS if p.scheme == "https" else PinnedHTTP
    conn = cls(p.hostname, port, ip, timeout)
    try:
        path = urlunsplit(("", "", p.path or "/", p.query, ""))
        conn.request(method, path, headers={"User-Agent": AGENT, "Accept": "text/html,*/*;q=0.8", "Connection": "close"})
        response = conn.getresponse()
        headers = {k.lower(): v for k, v in response.getheaders()}
        body = b""
        if method != "HEAD" and headers.get("content-type", "").split(";")[0].strip().lower() in ("text/html", "application/xhtml+xml", "text/plain"):
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                body = body[:max_bytes]
        return response.status, headers, body
    finally:
        conn.close()

def www_equivalent(source, target):
    a, b = urlsplit(source), urlsplit(target)
    if a.scheme != "https" or b.scheme != "https" or a.port not in (None, 443) or b.port not in (None, 443):
        return False
    base = a.hostname.removeprefix("www.")
    return a.hostname != b.hostname and {a.hostname, b.hostname} == {base, "www." + base}


def crawl(start, max_pages=100, timeout=10, max_links=10000, delay=0.0,
          respect_robots=True, fetch=request, progress=None):
    if max_pages < 1 or max_links < 1 or timeout <= 0 or delay < 0:
        raise ValueError("Limits must be positive (delay may be zero)")
    def emit(event, **details):
        if progress is not None:
            progress(event, **details)

    start = canonical(start)
    requested_start = start
    bootstrap_error = None
    try:
        probe = start
        seen = {probe}
        for _ in range(6):
            status, headers, _ = fetch(probe, timeout=timeout)
            if status not in REDIRECTS or not headers.get("location"):
                break
            destination = canonical(urljoin(probe, headers["location"]))
            if origin(destination) != origin(probe) and not www_equivalent(probe, destination):
                bootstrap_error = f"Redirección inicial bloqueada: {probe} -> {destination}"
                break
            if destination in seen:
                bootstrap_error = "Bucle de redirección inicial"
                break
            seen.add(destination)
            probe = destination
        if bootstrap_error is None and origin(probe) != origin(start):
            emit("canonical_redirect", source=start, target=probe)
            start = probe
    except (OSError, ValueError, ssl.SSLError, http.client.HTTPException) as exc:
        bootstrap_error = f"No se pudo resolver la URL inicial: {exc}"
    root = origin(start)
    pending = deque([start])
    scheduled = {start}
    pages = {start}
    visited = set()
    results = {}
    references = {}
    robots = RobotFileParser()
    robots_url = urlunsplit((root[0], urlsplit(start).netloc, "/robots.txt", "", ""))
    emit("robots_start", url=robots_url, enabled=respect_robots)
    if respect_robots:
        try:
            status, _, body = fetch(robots_url, timeout=timeout)
            if status in (401, 403):
                robots.parse(["User-agent: *", "Disallow: /"])
            elif status >= 500 or status == 429:
                robots.parse(["User-agent: *", "Disallow: /"])
            elif status == 200:
                robots.parse(body.decode("utf-8", "replace").splitlines())
            else:
                robots.parse([])
        except (OSError, ValueError, ssl.SSLError):
            robots.parse(["User-agent: *", "Disallow: /"])
    emit("robots_done")
    checked = 0
    while pending and checked < max_links:
        url = pending.popleft()
        if url in visited:
            continue
        visited.add(url)
        checked += 1
        emit("checking", url=url, checked=checked, queued=len(pending), discovered=len(scheduled))
        if respect_robots and not robots.can_fetch(AGENT, url):
            results[url] = {"status": "SKIPPED", "reason": "robots.txt"}
            emit("result", url=url, status="SKIPPED", reason="robots.txt")
            continue
        if delay:
            time.sleep(delay)
        try:
            current = url
            redirects = set()
            for _ in range(6):
                status, headers, body = fetch(current, timeout=timeout)
                if status not in REDIRECTS:
                    break
                location = headers.get("location")
                if not location:
                    break
                target = canonical(urljoin(current, location))
                if origin(target) != root:
                    raise ValueError("Redirect outside origin blocked")
                if target in redirects or target == current:
                    raise ValueError("Redirect loop")
                if respect_robots and not robots.can_fetch(AGENT, target):
                    raise ValueError("Redirect forbidden by robots.txt")
                redirects.add(current)
                current = target
            else:
                raise ValueError("Too many redirects")
            state = "BROKEN" if status in (404, 410) else "OK" if 200 <= status < 400 else "INCONCLUSIVE"
            results[url] = {"status": state, "http_status": status, "final_url": current}
            emit("result", url=url, status=state, http_status=status, final_url=current)
            if state != "OK" or url not in pages or len(pages) > max_pages:
                continue
            if "html" not in headers.get("content-type", "").lower():
                continue
            parser = Links()
            parser.feed(body.decode("utf-8", "replace"))
            base = urljoin(current, parser.base) if parser.base else current
            for raw in parser.links:
                try:
                    target = canonical(urljoin(base, raw))
                except ValueError:
                    continue
                if origin(target) != root:
                    continue
                if target not in references and len(references) >= max_links:
                    continue
                sources = references.setdefault(target, [])
                if url not in sources:
                    sources.append(url)
                if raw in parser.pages and len(pages) < max_pages:
                    pages.add(target)
                if target not in scheduled and len(scheduled) < max_links:
                    pending.append(target)
                    scheduled.add(target)
        except (OSError, ValueError, ssl.SSLError, http.client.HTTPException) as exc:
            results[url] = {"status": "INCONCLUSIVE", "reason": str(exc)[:200]}
            emit("result", url=url, status="INCONCLUSIVE", reason=str(exc)[:200])
    emit("finished", checked=len(visited), remaining=len(pending))
    inconclusive = sum(item["status"] == "INCONCLUSIVE" for item in results.values())
    skipped = sum(item["status"] == "SKIPPED" for item in results.values())
    completed = sum(item["status"] in ("OK", "BROKEN") for item in results.values())
    audit_status = ("INCONCLUSIVE" if bootstrap_error or completed == 0 else
                    "PARTIAL" if pending or inconclusive or skipped or len(scheduled) >= max_links else "COMPLETE")
    return {
        "requested_start": requested_start,
        "start": start,
        "audit_status": audit_status,
        "audit_reason": bootstrap_error or (results.get(start, {}).get("reason") if completed == 0 else None),
        "inconclusive_count": inconclusive,
        "skipped_count": skipped,
        "checked_successfully": completed, "pages_checked": len(visited), "truncated": bool(pending) or len(scheduled) >= max_links,
        "results": results,
        "broken": [{"url": url, "sources": references.get(url, []), **result}
                   for url, result in sorted(results.items()) if result["status"] == "BROKEN"],
    }
