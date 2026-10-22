# Estrategia de pruebas institucionales — M0

## Baseline
Suite existente en tests/test_crawler.py y tests/test_report.py; el usuario confirmó previamente 18/18 tests antes de la última PR de redirecciones. No se han ejecutado tests en esta intervención documental. No extrapolar el resultado a master actual.

## Capas
1. Unitarias: canonicalización, estados, clasificación, parsers, serialización.
2. Contratos: JSON Schema, plugins, migraciones y compatibilidad.
3. Integración: servidor HTTP sintético local y transporte real aislado.
4. Seguridad: SSRF, DNS rebinding, IPv6, redirecciones, TLS, robots, HTML/CSV injection.
5. E2E: auditoría reproducible de un sitio sintético con verdad conocida.
6. Presentación: PDF multipágina, Unicode, URLs largas, accesibilidad automática y manual.
7. Multiplataforma: Windows y Linux, Python soportados.

## Invariantes
No se solicita destino no autorizado. Hallazgos confirmados tienen observaciones y evidencia. Contadores reconciliados. Fallos de exportación no mutan resultados. CANCELLED/FAILED no se presentan como COMPLETE. Un recurso no visitado no puede darse por RESOLVED.

## Gates
M0: documentación revisada, trazabilidad de requisitos y ninguna modificación de código.
M1: pruebas unitarias y de seguridad críticas verdes, integración HTTP real, límites verificados.
M2: coherencia entre formatos, evidencia accesible y exportación segura.
M3: aislamiento de plugins y contratos verificados.
M4: migraciones e histórico sin falsos RESOLVED.
M5: piloto autorizado, revisión de privacidad y operación documentada.

Objetivos orientativos: 100% de casos críticos conocidos y referencias válidas; >=90% de cobertura del núcleo como métrica auxiliar. No afirmar certificación por cobertura de tests.
