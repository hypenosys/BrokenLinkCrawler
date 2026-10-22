# Contratos de datos propuestos — versión 1.0.0

Estado: diseño M0. Los JSON actuales no cumplen aún este contrato; no se propone cambiar su formato durante M0.

## Entidades
- `AuditRun`: run_id, schema_version, requested_start, effective_start, engine_version, configuration_hash, timestamps UTC, scope_policy_id, status, coverage.
- `Resource`: resource_id, original_url, normalized_url, resource_type, run_id.
- `FetchAttempt`: attempt_id, resource_id, requested_at, HTTP status o error, timing, final_url, redirect hops.
- `LinkOccurrence`: occurrence_id, source_resource_id, target_resource_id, element, attribute, link_text, dom_locator, observed_at.
- `Observation`: observation_id, rule_id, rule_version, resource_id, attempt_id, observed_value, evidence_ids.
- `Finding`: finding_id, rule_id, rule_version, classification, severity, confidence, observation_ids, occurrence_ids, remediation.
- `Evidence`: evidence_id, type, source, timestamp, content_hash, retention_policy, redaction_status.
- `Coverage`: discovered, attempted, verified, skipped, inconclusive, pending, excluded, and explicit limit events.

## Enumeraciones
`AuditRun.status`: CREATED, VALIDATING, RUNNING, COMPLETE, PARTIAL, INCONCLUSIVE, FAILED, CANCELLED.
`Finding.classification`: CONFIRMED, SUSPECTED, NEEDS_REVIEW, DISMISSED.
`severity`: CRITICAL, HIGH, MEDIUM, LOW, INFO.
`confidence`: HIGH, MEDIUM, LOW.

La severidad de impacto ciudadano no se deriva únicamente de HTTP status. Un HTTP 403/500 no se considera 404/410 confirmado.

## Integridad
Cada entidad incluye `run_id` o una relación inequívoca a él. Toda observación tiene recurso. Todo hallazgo confirmado enlaza observaciones y evidencias. La suma de estados terminales de recursos debe reconciliar con el conjunto procesado. Distinguir recursos únicos, intentos HTTP y apariciones de enlaces; nunca sumarlos como si fueran la misma métrica.

## Identidad
IDs de ejecución únicos. IDs de hallazgo estables entre ejecuciones mediante clave lógica versionada (regla + recurso + atributos relevantes), sin basarse en el número de fila. No declarar RESOLVED cuando la nueva ejecución carece de cobertura válida.

## Compatibilidad
`schema_version` independiente de `engine_version`. Cambios incompatibles requieren versión mayor y migración. Los consumidores deben tolerar campos opcionales; valores de enumeración desconocidos requieren estrategia explícita. Conservar fixtures de versiones previas.

## URL y privacidad
Guardar URL original y normalizada por separado. No eliminar query params sin política. Redactar credenciales, tokens y parámetros sensibles en logs e informes; documentar la pérdida de información por redacción. Capturas HTML y documentos completos desactivados por defecto.

## Criterios de aceptación del contrato
Validación JSON Schema, fixtures positivos y negativos, serialización determinista, compatibilidad con lectores anteriores, contadores reconciliados y referencias internas existentes.
