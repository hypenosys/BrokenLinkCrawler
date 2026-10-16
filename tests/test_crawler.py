import unittest
from unittest.mock import patch
from brokenlinkcrawler.crawler import Links, canonical, crawl, resolve_public, request

class Tests(unittest.TestCase):
    def test_links(self):
        p = Links()
        p.feed('<a href="/missing">x</a><img src="/pic.png"><source srcset="/a.png 1x, /b.png 2x">')
        self.assertEqual(p.links, ["/missing", "/pic.png", "/a.png", "/b.png"])

    def test_invalid_urls(self):
        for url in ("file:///etc/passwd", "http://user:pass@example.com", "http://127.0.0.1:0",
                    "http://1234/", "http://[fe80::1%25eth0]/"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                canonical(url)

    def test_normalization(self):
        self.assertEqual(canonical("HTTPS://EXAMPLE.COM:443/a#x"), "https://example.com/a")

    def test_dns_private_block(self):
        import socket
        fake = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]
        with patch("socket.getaddrinfo", return_value=fake):
            with self.assertRaises(ValueError):
                resolve_public("example.com", 80)

    def test_dns_mixed_block(self):
        import socket
        fake = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 80)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 80))]
        with patch("socket.getaddrinfo", return_value=fake):
            with self.assertRaises(ValueError):
                resolve_public("example.com", 80)

    def test_link_discovery_and_broken_sources(self):
        calls = []
        def fetch(url, timeout=10):
            calls.append(url)
            paths = {
                "https://example.com/robots.txt": (404, {}, b""),
                "https://example.com/": (200, {"content-type": "text/html"}, b'<a href="/next">Next</a><a href="/missing">Missing</a>'),
                "https://example.com/next": (200, {"content-type": "text/html"}, b'<a href="/missing">Again</a>'),
                "https://example.com/missing": (404, {"content-type": "text/html"}, b""),
            }
            return paths[url]
        result = crawl("https://example.com", fetch=fetch)
        self.assertEqual(result["broken"][0]["url"], "https://example.com/missing")
        self.assertEqual(set(result["broken"][0]["sources"]), {"https://example.com/", "https://example.com/next"})
        self.assertFalse(result["truncated"])

    def test_robots_blocks(self):
        def fetch(url, timeout=10):
            if url.endswith("robots.txt"):
                return 200, {}, b"User-agent: *\nDisallow: /secret"
            if url.endswith("/"):
                return 200, {"content-type": "text/html"}, b'<a href="/secret">secret</a>'
            raise AssertionError("blocked URL fetched")
        result = crawl("https://example.com", fetch=fetch)
        self.assertEqual(result["results"]["https://example.com/secret"]["status"], "SKIPPED")

    def test_redirect_outside_origin(self):
        def fetch(url, timeout=10):
            if url.endswith("robots.txt"):
                return 404, {}, b""
            return 302, {"location": "http://127.0.0.1/private"}, b""
        result = crawl("https://example.com", fetch=fetch)
        self.assertEqual(result["results"]["https://example.com/"]["status"], "INCONCLUSIVE")

    def test_bounded(self):
        def fetch(url, timeout=10):
            if url.endswith("robots.txt"):
                return 404, {}, b""
            return 200, {"content-type": "text/html"}, b'<a href="/a">a</a><a href="/b">b</a>'
        result = crawl("https://example.com", fetch=fetch, max_links=2)
        self.assertTrue(result["truncated"])
        self.assertLessEqual(result["pages_checked"], 2)

if __name__ == "__main__":
    unittest.main()
