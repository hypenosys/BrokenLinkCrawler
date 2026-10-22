# API de extensiones — propuesta M0

## Tipos
DiscoveryPlugin: documento -> candidatos. AnalyzerPlugin: observaciones -> hallazgos. EvidencePlugin: contexto autorizado -> evidencias derivadas. ExporterPlugin: resultado consolidado -> formato. IntegrationPlugin: eventos -> entrega autorizada.

## Manifest (contrato propuesto)
Campos: manifest_version, plugin_id, version, api_compatibility, type, entrypoint, capabilities, network_access, filesystem_access, resource_limits. Versionar por separado API y reglas de detección.

## Capacidades
read:observations, read:evidence_redacted, write:findings, write:derived_evidence, export:results, emit:events. Ningún plugin adquiere acceso a red mediante la API de análisis; solicitar recursos al núcleo.

## Seguridad
Los manifiestos son declaraciones, no controles técnicos. Plugins integrados auditados pueden ejecutarse en proceso. Plugins de terceros requieren aislamiento de SO/contenedor, límites de CPU/memoria/tiempo y permisos reales. Fallos generan ANALYZER_FAILED y degradan cobertura; no desaparecen.

## Ciclo de vida
initialize(context) -> analyze(observation, readonly_context) -> finalize() -> shutdown(). Interfaces concretas, transporte RPC, errores, compatibilidad y firma de paquetes se ratificarán tras M1.

## Pruebas de contrato
Manifiestos inválidos, incompatibilidad de versión, timeout, excepción, intento de red, datos maliciosos, determinismo de resultados y recuperación tras fallo.
