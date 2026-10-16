"""Readable reports showing exactly where each broken link was found."""
from datetime import datetime, timezone
from html import escape
from pathlib import Path


def broken_occurrences(report):
    """One row per (source page, broken target), sorted for reproducibility."""
    rows = []
    for item in report.get("broken", []):
        target = item["url"]
        code = item.get("http_status")
        sources = sorted(set(item.get("sources", [])))
        for source in sources or ["(URL inicial o fuente desconocida)"]:
            rows.append({"source": source, "target": target, "http_status": code,
                         "final_url": item.get("final_url", target)})
    return sorted(rows, key=lambda row: (row["source"], row["target"]))


def render_text(report):
    rows = broken_occurrences(report)
    targets = len(report.get("broken", []))
    lines = [
        "BROKEN LINK CRAWLER - INFORME LEGIBLE",
        "=" * 65,
        f"Sitio inicial: {report.get('start', '')}",
        f"URLs comprobadas: {report.get('pages_checked', 0)}",
        f"Enlaces rotos únicos: {targets}",
        f"Apariciones de enlaces rotos: {len(rows)}",
        f"Rastreo limitado: {'SÍ' if report.get('truncated') else 'NO'}",
        "",
    ]
    if not rows:
        lines.append("No se detectaron enlaces HTTP 404/410 en las URLs comprobadas.")
    for i, row in enumerate(rows, 1):
        lines.extend([
            f"[{i}] HTTP {row['http_status'] if row['http_status'] is not None else '?'}",
            f"    PÁGINA DE ORIGEN: {row['source']}",
            f"    URL QUE FALLA:   {row['target']}",
        ])
        if row["final_url"] != row["target"]:
            lines.append(f"    URL FINAL:       {row['final_url']}")
        lines.append("")
    if report.get("truncated"):
        lines.append("AVISO: El rastreo alcanzó un límite; el informe no cubre todo el sitio.")
    return "\n".join(lines).rstrip() + "\n"


def render_html(report):
    rows = broken_occurrences(report)
    blocks = []
    for row in rows:
        code = escape(str(row["http_status"] or "?"))
        source = escape(row["source"], quote=True)
        target = escape(row["target"], quote=True)
        final = escape(row["final_url"], quote=True)
        blocks.append(
            f'<article><span class="code">HTTP {code}</span>'
            f'<div><strong>Página donde aparece:</strong> <a href="{source}">{source}</a></div>'
            f'<div><strong>Enlace roto:</strong> <a href="{target}">{target}</a></div>'
            + (f'<div><strong>Destino final:</strong> <a href="{final}">{final}</a></div>'
               if final != target else "")
            + '</article>'
        )
    if not blocks:
        blocks.append("<p>No se detectaron enlaces HTTP 404/410 en las URLs comprobadas.</p>")
    warning = ('<p class="warning">Rastreo limitado: no se ha analizado todo el sitio.</p>'
               if report.get("truncated") else "")
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>BrokenLinkCrawler - Informe</title>'
        '<style>body{font:16px system-ui,sans-serif;max-width:960px;margin:3rem auto;padding:0 1rem;'
        'line-height:1.6;color:#20242a}a{overflow-wrap:anywhere;color:#1456a0}'
        'article{border:1px solid #ddd;border-radius:8px;padding:1rem;margin:1rem 0}'
        '.code{font-weight:bold;color:#aa2525}.warning{color:#a33;font-weight:bold}'
        'small{color:#666}</style></head><body>'
        '<h1>Informe de enlaces rotos</h1>'
        f'<p><strong>Sitio:</strong> {escape(report.get("start", ""))}</p>'
        f'<p><strong>URLs comprobadas:</strong> {report.get("pages_checked", 0)}'
        f' · <strong>Enlaces rotos únicos:</strong> {len(report.get("broken", []))}'
        f' · <strong>Apariciones:</strong> {len(rows)}</p>'
        + warning + "".join(blocks) + '</body></html>\n'
    )


def write_readable_reports(report, json_path):
    base = Path(json_path).with_suffix("")
    txt = base.with_suffix(".txt")
    html = base.with_suffix(".html")
    txt.write_text(render_text(report), encoding="utf-8")
    html.write_text(render_html(report), encoding="utf-8")
    return txt, html
