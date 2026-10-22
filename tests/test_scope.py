import unittest
from brokenlinkcrawler.scope import ScopePolicy, url_origin
from brokenlinkcrawler.crawler import crawl


class ScopeContractTests(unittest.TestCase):
    def test_same_origin_only(self):
        policy = ScopePolicy("https://www.example.com/")
        self.assertTrue(policy.allows("https://www.example.com/path?x=1"))
        for url in ("http://www.example.com/", "https://example.com/",
                    "https://api.example.com/", "https://www.example.com:8443/"):
            with self.subTest(url=url):
                self.assertFalse(policy.allows(url))
                with self.assertRaises(ValueError):
                    policy.require(url)

    def test_default_ports(self):
        self.assertEqual(url_origin("https://example.com:443/x"), url_origin("https://example.com/x"))

    def test_redirect_chain_and_coverage(self):
        def fetch(url, timeout=10):
            fixtures = {
                "https://example.com/robots.txt": (404, {}, b""),
                "https://example.com/": (200, {"content-type": "text/html"}, b'<a href="/old">Old</a>'),
                "https://example.com/old": (301, {"location": "/missing"}, b""),
                "https://example.com/missing": (404, {}, b""),
            }
            return fixtures[url]
        report = crawl("https://example.com/", fetch=fetch)
        self.assertEqual(report["results"]["https://example.com/old"]["redirect_chain"],
                         [{"source": "https://example.com/old", "target": "https://example.com/missing", "http_status": 301}])
        self.assertEqual(report["coverage"]["processed"], sum(report["coverage"][key] for key in ("ok", "broken", "inconclusive", "skipped")))
        self.assertEqual(report["broken"][0]["final_url"], "https://example.com/missing")


if __name__ == "__main__":
    unittest.main()
