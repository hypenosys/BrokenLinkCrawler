import unittest
from brokenlinkcrawler.report import broken_occurrences, render_text, render_html

class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "start": "https://example.com/",
            "pages_checked": 3,
            "truncated": False,
            "broken": [
                {"url": "https://example.com/missing", "http_status": 404,
                 "final_url": "https://example.com/missing",
                 "sources": ["https://example.com/b", "https://example.com/a", "https://example.com/a"]},
                {"url": "https://example.com/gone", "http_status": 410,
                 "sources": ["https://example.com/a"]},
            ],
        }

    def test_one_row_per_source_and_target(self):
        rows = broken_occurrences(self.report)
        self.assertEqual(len(rows), 3)
        self.assertEqual([row["source"] for row in rows],
                         ["https://example.com/a", "https://example.com/a", "https://example.com/b"])

    def test_text_contains_origin_and_target(self):
        output = render_text(self.report)
        self.assertIn("PÁGINA DE ORIGEN: https://example.com/a", output)
        self.assertIn("URL QUE FALLA:   https://example.com/missing", output)
        self.assertIn("HTTP 410", output)

    def test_html_escapes_untrusted_urls(self):
        self.report["broken"][0]["url"] = 'https://example.com/?x=<script>alert(1)</script>'
        output = render_html(self.report)
        self.assertNotIn("<script>", output)
        self.assertIn("&lt;script&gt;", output)
        self.assertIn("Página donde aparece:", output)

    def test_empty_report(self):
        self.report["broken"] = []
        self.assertIn("No se detectaron", render_text(self.report))
        self.assertIn("No se detectaron", render_html(self.report))

    def test_truncation_warning(self):
        self.report["truncated"] = True
        self.assertIn("no cubre todo el sitio", render_text(self.report))
        self.assertIn("Rastreo limitado", render_html(self.report))

if __name__ == "__main__":
    unittest.main()
