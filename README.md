# BrokenLinkCrawler

Python CLI for finding broken HTTP links on a site, with referring-page information.

## Install (Python 3.10+)

```sh
git clone https://github.com/hypenosys/BrokenLinkCrawler.git
cd BrokenLinkCrawler
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Run

```sh
brokenlinkcrawler https://example.com --max-pages 300 --max-links 10000 --timeout 10 --delay 0.2 --output report.json
```

The crawler checks internal HTML links and referenced assets (including srcset), follows internal redirects, and reports HTTP 404/410 targets with the pages that reference them. It refuses redirects to other origins during crawling (with a narrowly constrained HTTPS apex/www initial canonicalization), validates all resolved IPs as public, and connects to the validated IP directly while preserving the original hostname for TLS verification and the HTTP Host header. It respects robots.txt by default and rejects crawling if the robots policy cannot be retrieved. `--ignore-robots` is available for sites you own or have permission to test.

JSON output includes `results`, `broken`, `pages_checked`, `truncated`, `audit_status`, and diagnostic counts. Exit code 1 means broken links were detected; 2 means the audit was inconclusive; 0 means none were confirmed (the audit may still be partial). Review `INCONCLUSIVE` and `SKIPPED` results separately.

### Limitations

This is a bounded single-threaded crawler, **not a guarantee of complete site coverage**. It does not render JavaScript, parse CSS URLs, load sitemaps, or check off-site links. Per-request timeouts are not a global deadline. `--max-pages` limits HTML page discovery and `--max-links` limits URL checks. For untrusted sites, run it in a restricted network environment as an additional defense in depth.

Run tests with `python -m unittest discover -s tests -v`. GitHub Actions runs the same tests on pushes.

## Informes legibles

Cada ejecución genera cinco archivos a partir de `--output report.json`: JSON (datos completos), TXT (lista legible), HTML (informe interactivo local), CSV (exportación tabular) y PDF (informe imprimible). En TXT y HTML se muestra **la página donde aparece el enlace roto**, **la URL que falla** y su **código HTTP**. Si un enlace roto aparece en varias páginas, se muestra una entrada por página de origen. Las URL sin página de origen conocida se identifican como tales.

```bash
.venv/Scripts/python -m brokenlinkcrawler https://www.montsia.cat/ca --max-pages 300 --max-links 10000 --delay 0.2 --output report.json
```

Abre `report.html` con tu navegador de Windows o `report.txt` con un editor. Los informes recogen únicamente enlaces detectados como 404/410; revisa `report.json` para estados inconclusos.

## Desarrollo institucional (M0/M1)

La especificación propuesta está en `docs/institutional/`. M1 introduce `ScopePolicy`, evidencia de saltos HTTP en `redirect_chain` y contadores `coverage` sin retirar las claves JSON existentes. La cobertura se refiere a los recursos procesados, no a todo el sitio. Estas ampliaciones deben validarse con `python -m unittest discover -s tests -v` antes de fusionarse.
