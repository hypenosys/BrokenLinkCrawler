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
        self.assertNotIn("<script>alert(1)</script>", output)
        self.assertIn("<script>const f=", output)
        self.assertIn("&lt;script&gt;", output)
        self.assertIn('<th scope="col">Página donde aparece</th>', output)

    def test_empty_report(self):
        self.report["broken"] = []
        self.assertIn("No se detectaron", render_text(self.report))
        self.assertIn("No se detectaron", render_html(self.report))

    def test_truncation_warning(self):
        self.report["truncated"] = True
        self.assertIn("no cubre todo el sitio", render_text(self.report))
        self.assertIn("Rastreo limitado", render_html(self.report))


    def test_csv_contains_all_occurrences(self):
        from brokenlinkcrawler.report import render_csv
        import csv
        import io
        rows = list(csv.DictReader(io.StringIO(render_csv(self.report))))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["pagina_origen"], "https://example.com/a")

    def test_csv_prevents_spreadsheet_formula_injection(self):
        from brokenlinkcrawler.report import render_csv
        self.report["broken"][0]["sources"] = ["=HYPERLINK(1)"]
        self.assertIn("'=HYPERLINK(1)", render_csv(self.report))

    def test_html_has_accessible_table_and_filter(self):
        output = render_html(self.report)
        self.assertIn('<main>', output)
        self.assertIn('scope="col"', output)
        self.assertIn('aria-controls="results"', output)
        self.assertIn('Página donde aparece', output)

    def test_pdf_writes_document(self):
        from brokenlinkcrawler.report import write_pdf
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.pdf"
            write_pdf(self.report, path)
            self.assertTrue(path.read_bytes().startswith(b"%PDF"))

if __name__ == "__main__":
    unittest.main()
