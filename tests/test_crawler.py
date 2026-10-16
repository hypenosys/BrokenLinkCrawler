import unittest
from brokenlinkcrawler.crawler import Links, crawl

class Tests(unittest.TestCase):
    def test_links(self):
        p = Links(); p.feed('<a href="/missing">x</a><img src="/pic.png">')
        self.assertEqual(p.links, ["/missing", "/pic.png"])
    def test_bad_scheme(self):
        with self.assertRaises(ValueError):
            crawl("file:///etc/passwd")
    def test_credentials(self):
        with self.assertRaises(ValueError):
            crawl("http://user:pass@example.com")

if __name__ == "__main__":
    unittest.main()
