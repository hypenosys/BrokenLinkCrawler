# BrokenLinkCrawler — Arquitectura institucional (M0)

Estado: propuesta, no implementación. Fecha: 2026-10-22.

## Propósito
Motor de rastreo especializado y extensible, local-first, con evidencia verificable, límites de red y exportadores desacoplados. El alcance institucional se define mediante políticas autorizadas; no supone certificación legal.

## Baseline observado en master
- Python >=3.10; paquete `brokenlinkcrawler`, CLI `brokenlinkcrawler.cli:main`.
- `crawler.py`: HTMLParser, URLs HTTP(S), descubrimiento interno, validación DNS pública y conexión IP fijada, robots.txt, redirecciones internas y alias HTTPS apex/www iniciales.
- `report.py`: informes TXT, HTML con filtro JS, CSV con BOM y PDF ReportLab.
- `crawl()` devuelve diccionario con `requested_start`, `start`, `audit_status`, `audit_reason`, contadores, `results` y `broken`.
- No existe todavía API pública de plugins, esquema formal versionado, persistencia ni evidencia DOM.
- El README aún menciona solo tres informes y no refleja todas las capacidades actuales.

## Límites arquitectónicos
1. `core`: política, adquisición, planificador y ciclo de vida. Único propietario de acceso a red.
2. `discovery`: candidatos a recursos, nunca solicitudes HTTP directas.
3. `analyzers`: observaciones inmutables -> candidatos de hallazgo.
4. `evidence`: referencias verificables, retención y redacción.
5. `reporting`: vistas puras del resultado normalizado.
6. `storage`: adaptadores opcionales; SQLite primero.
7. `integrations`: consumidores de eventos autorizados.

Las dependencias apuntan hacia contratos estables, no hacia presentaciones. No reorganizar módulos antes de establecer pruebas de compatibilidad.

## ADR propuestas
- ADR-001 Python >=3.10 inicialmente.
- ADR-002 núcleo modular sin dependencia obligatoria de plugins.
- ADR-003 SQLite opcional para histórico local.
- ADR-004 JSON Schema y SemVer para datos intercambiables.
- ADR-005 una fuente normalizada para JSON, HTML, TXT, CSV y PDF.
- ADR-006 plugins de terceros fuera de proceso con aislamiento verificable.
- ADR-007 solo el núcleo controla el acceso a red.
- ADR-008 HTML estático primero; navegador opcional.
- ADR-009 GPL-3.0-only del núcleo; revisar compatibilidad de dependencias.
- ADR-010 IA nunca requisito para determinar hallazgos.

## Invariantes
- Ninguna petición fuera del alcance autorizado.
- Un recurso inconcluso no equivale a enlace sano ni a incidencia resuelta.
- Un hallazgo confirmado tiene observación y evidencia rastreables.
- Una auditoría completa es completa solo respecto al alcance y analizadores declarados.
- Exportar no modifica observaciones.
- Los fallos de plugins y exportadores no alteran silenciosamente la clasificación técnica.

## Decisiones diferidas
Concurrencia, aislamiento de plugins, esquema SQL, compatibilidad de navegador, API y autenticación requieren ADR separadas tras M1.
