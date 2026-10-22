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


def audit_notice(report):
    status = report.get("audit_status")
    if status == "INCONCLUSIVE":
        return "AUDITORÍA INCONCLUSA: " + str(report.get("audit_reason") or "No se pudieron comprobar URLs satisfactoriamente.")
    if status == "PARTIAL":
        return "AUDITORÍA PARCIAL: hay URLs sin verificar o límites de rastreo."
    return ""


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
    if audit_notice(report):
        lines.append(audit_notice(report))
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
    """Self-contained, accessible HTML report; no remote assets or JavaScript."""
    rows = broken_occurrences(report)
    count = len(report.get("broken", []))
    occurrences = len(rows)
    warning = ('<p role="status" class="warning">Rastreo limitado: no se ha analizado todo el sitio.</p>'
               if report.get("truncated") else "")
    if audit_notice(report):
        warning += '<p role="alert" class="warning">' + escape(audit_notice(report)) + '</p>'
    body = []
    for index, row in enumerate(rows, 1):
        code = escape(str(row["http_status"] if row["http_status"] is not None else "?"))
        source = escape(row["source"], quote=True)
        target = escape(row["target"], quote=True)
        final = escape(row["final_url"], quote=True)
        body.append(
            f'<tr><th scope="row">{index}</th><td><a href="{target}">{target}</a></td>'
            f'<td><a href="{source}">{source}</a></td>'
            f'<td><strong class="code">HTTP {code}</strong></td>'
            f'<td>{("<a href=" + chr(34) + final + chr(34) + ">" + final + "</a>") if final != target else "—"}</td></tr>'
        )
    if not body:
        body.append('<tr><td colspan="5">No se detectaron enlaces HTTP 404/410 en las URLs comprobadas.</td></tr>')
    site = escape(str(report.get("start", "")))
    pages = escape(str(report.get("pages_checked", 0)))
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="color-scheme" content="light dark">'
        '<title>BrokenLinkCrawler - Informe</title>'
        '<style>'
        ':root{font-family:system-ui,sans-serif;line-height:1.5;color-scheme:light dark}'
        'body{max-width:1200px;margin:2rem auto;padding:0 1rem}'
        'a{overflow-wrap:anywhere}a:focus-visible,input:focus-visible{outline:3px solid #f90;outline-offset:2px}'
        '.summary{display:flex;gap:1rem;flex-wrap:wrap}.metric{border:1px solid #888;border-radius:10px;padding:1rem;min-width:160px}'
        '.metric strong{display:block;font-size:1.7rem}.scroll{overflow-x:auto}'
        'table{border-collapse:collapse;width:100%;margin-top:1rem}th,td{text-align:left;border-bottom:1px solid #888;padding:.7rem;vertical-align:top;overflow-wrap:anywhere}'
        'thead{background:Canvas}tbody tr[hidden]{display:none}tbody tr:nth-child(even){background:color-mix(in srgb,CanvasText 5%,Canvas)}'
        '.code{font-weight:700}.warning{border-left:4px solid #c60;padding:.7rem}'
        'input{font:inherit;padding:.6rem;max-width:100%;width:25rem}'
        '@media print{body{max-width:none;margin:0}input,label{display:none}a{color:inherit;text-decoration:none}thead{display:table-header-group}tr{break-inside:avoid}}'
        '</style></head><body><main>'
        '<h1>Informe de enlaces rotos</h1>'
        f'<p><strong>Sitio:</strong> {site}</p>'
        '<section aria-label="Resumen del análisis" class="summary">'
        f'<div class="metric"><strong>{pages}</strong>URLs comprobadas</div>'
        f'<div class="metric"><strong>{count}</strong>Enlaces rotos únicos</div>'
        f'<div class="metric"><strong>{occurrences}</strong>Apariciones</div></section>'
        + warning
        + '<h2>Incidencias confirmadas (HTTP 404/410)</h2>'
        + '<p>Otros estados, incluidos errores inconclusos, se conservan en el JSON. '
          'Los resultados pueden estar limitados por la configuración del rastreo.</p>'
        + '<label for="filter">Buscar en los resultados</label> '
          '<input id="filter" type="search" aria-controls="results" placeholder="Filtrar URL, origen o código">'
        + '<p id="filter-status" role="status" aria-live="polite"></p>'
        + '<div class="scroll"><table id="results"><caption>Enlaces rotos por página de origen</caption>'
          '<thead><tr><th scope="col">#</th><th scope="col">URL rota</th>'
          '<th scope="col">Página donde aparece</th><th scope="col">Estado</th>'
          '<th scope="col">URL final</th></tr></thead><tbody>'
        + "".join(body) + '</tbody></table></div></main>'
        + '<script>const f=document.getElementById("filter"),'
          'r=[...document.querySelectorAll("#results tbody tr")],'
          's=document.getElementById("filter-status");'
          'f.addEventListener("input",()=>{const q=f.value.toLocaleLowerCase();'
          'let n=0;for(const row of r){const match=row.textContent.toLocaleLowerCase().includes(q);'
          'row.hidden=!match;if(match)n++}s.textContent=n+" filas visibles";});</script>'
        + '</body></html>\\n'
    )


def render_csv(report):
    """Export every broken-link occurrence with spreadsheet-safe cells."""
    import csv
    import io
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["pagina_origen", "url_rota", "codigo_http", "url_final"])
    for row in broken_occurrences(report):
        def safe(value):
            value = str(value if value is not None else "")
            return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\\t", "\\r")) else value
        writer.writerow([safe(row["source"]), safe(row["target"]),
                         safe(row["http_status"]), safe(row["final_url"])])
    return stream.getvalue()


def write_pdf(report, path):
    """Paginated A4 report using ReportLab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    from xml.sax.saxutils import escape as xml_escape
    styles = getSampleStyleSheet()
    cell = ParagraphStyle("URLCell", parent=styles["BodyText"], fontSize=8, leading=11, wordWrap="CJK")
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=32, rightMargin=32,
                            topMargin=40, bottomMargin=40)
    elements = [Paragraph("Informe de enlaces rotos", styles["Title"]),
                Paragraph("Sitio: " + xml_escape(str(report.get("start", ""))), cell),
                Spacer(1, 12),
                Paragraph(f"URLs comprobadas: {report.get('pages_checked', 0)} | "
                          f"Enlaces rotos únicos: {len(report.get('broken', []))} | "
                          f"Apariciones: {len(broken_occurrences(report))}", styles["BodyText"]),
                Spacer(1, 12)]
    if report.get("truncated"):
        elements.append(Paragraph("AVISO: rastreo limitado; cobertura incompleta.", styles["BodyText"]))
    if audit_notice(report):
        elements.append(Paragraph(xml_escape(audit_notice(report)), styles["BodyText"]))
    data = [[Paragraph(x, cell) for x in ("#", "URL rota", "Página de origen", "HTTP")]]
    for i, row in enumerate(broken_occurrences(report), 1):
        data.append([Paragraph(str(i), cell),
                     Paragraph(xml_escape(str(row["target"])), cell),
                     Paragraph(xml_escape(str(row["source"])), cell),
                     Paragraph(xml_escape(str(row["http_status"] or "?")), cell)])
    if len(data) == 1:
        elements.append(Paragraph("No se detectaron enlaces HTTP 404/410.", styles["BodyText"]))
    else:
        table = LongTable(data, colWidths=[24, 210, 240, 35], repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                                   ("LINEBELOW", (0, 0), (-1, 0), .5, colors.grey)]))
        elements.append(table)
    doc.build(elements)


def write_readable_reports(report, json_path):
    base = Path(json_path).with_suffix("")
    txt = base.with_suffix(".txt")
    html = base.with_suffix(".html")
    txt.write_text(render_text(report), encoding="utf-8")
    html.write_text(render_html(report), encoding="utf-8")
    csv_path = base.with_suffix(".csv")
    csv_path.write_text("\ufeff" + render_csv(report), encoding="utf-8")
    pdf_path = base.with_suffix(".pdf")
    write_pdf(report, pdf_path)
    return txt, html, csv_path, pdf_path
