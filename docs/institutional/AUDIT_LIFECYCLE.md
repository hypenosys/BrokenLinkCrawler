# Ciclo de vida y cobertura — diseño M0

## Estados
CREATED -> VALIDATING -> RUNNING -> COMPLETE | PARTIAL | INCONCLUSIVE | FAILED | CANCELLED.

- COMPLETE: todo el alcance *descubierto y declarado* fue evaluado con los métodos habilitados y sin pendientes relevantes.
- PARTIAL: existen comprobaciones válidas pero también elementos pendientes, excluidos, saltados o inconclusos.
- INCONCLUSIVE: no hay evidencia suficiente para una conclusión útil sobre el objetivo.
- FAILED: fallo interno o de integridad de ejecución.
- CANCELLED: cancelación solicitada, conservando resultados parciales.

No interpretar COMPLETE como descubrimiento exhaustivo de todas las URLs posibles del sitio.

## Métricas disjuntas
Descubierto, programado, intentado, evaluado, omitido, inconcluso, pendiente y excluido necesitan definiciones formales y contadores reconciliables. Registrar límites alcanzados y razones de exclusión. Diferenciar páginas HTML de recursos HTTP y apariciones.

## Eventos
run_started, policy_validated, resource_discovered, fetch_started, fetch_finished, observation_recorded, finding_derived, scope_excluded, limit_reached, run_finished, run_failed, run_cancelled.

Cada evento tendrá ID, run_id, timestamp UTC, tipo, versión y datos mínimos redactados.

## Códigos de salida
Mantener compatibilidad con 0 (sin rotos confirmados), 1 (rotos confirmados), 2 (auditoría inconclusa). Diseñar códigos para FAILED/CANCELLED sin colisiones antes de cambiarlos. Un resultado PARTIAL puede incluir enlaces rotos; el CLI debe imprimir explícitamente su cobertura.

## Reanudación
No incluida en M0. En M4, guardar frontier, deduplicación, política, hashes y checkpoints; no repetir hallazgos por reintentos.
