# Roadmap institucional — propuesta, sin autorización de código

## M0 — Baseline y contratos (1–2 semanas)
Inventario de comportamiento, ADR, entidades, amenazas, estados, estrategia de pruebas. Salida: documentos revisados y decisiones ratificadas.

## M1 — Núcleo seguro (3–5 semanas)
BLC-001 contratos; BLC-002 HTTP separado; BLC-003 alcance; BLC-004 redirecciones; BLC-005 sitemaps; BLC-006 evidencia DOM; BLC-007 URLs mal formadas; BLC-008 cobertura; BLC-009 laboratorio HTTP; BLC-010 hallazgos. Gate: auditoría reproducible y cobertura explicable.

## M2 — Informes (2–4 semanas)
BLC-011 exportadores coherentes; BLC-016 i18n; resumen ejecutivo, operativo y anexos; validación PDF accesible. Gate: responsables identifican incidencias y evidencias sin código.

## M3 — Plugins (3–5 semanas)
BLC-012 interfaces; BLC-013 manifiestos; BLC-017 documentos; BLC-018 accesibilidad automatizada. Gate: extensión independiente sin ampliación de permisos.

## M4 — Histórico (2–4 semanas)
BLC-014 SQLite; BLC-015 comparación, identidades estables y estados NEW/PERSISTING/RESOLVED/REGRESSED/UNVERIFIED. Gate: no falsos resueltos.

## M5 — Piloto institucional (3–5 semanas)
Privacidad, retención, permisos, SBOM, revisión de licencias, operación, piloto autorizado y aceptación. BLC-019 programación y BLC-020 API/multiportal se evalúan después, no son prerrequisitos del núcleo.

## Dependencias
M0 -> M1 -> M2; M1 -> M3; M2 + M3 -> M4 -> M5.

## Criterio general de cierre
Requisitos trazables, contratos documentados, pruebas positivas/negativas, seguridad y privacidad revisadas, compatibilidad evaluada, CI verificada y evidencia de resultados. Ningún merge de implementación sin gates aprobados.

## Riesgos actuales observados
README desactualizado respecto a CSV/PDF; docstring de HTML contradice presencia de JS; contadores de cobertura limitados; bootstrap inicial apex/www requiere revisión de presupuesto y robots; no hay esquema versionado ni persistencia.
