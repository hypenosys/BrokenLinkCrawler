# Modelo de seguridad — propuesta M0

## Activos y fronteras
Activos: disponibilidad de portales auditados, datos personales en páginas/URLs, credenciales, evidencias, resultados y entorno ejecutor. Fronteras: CLI -> configuración; red -> respuesta no confiable; parser -> hallazgos; plugin -> núcleo; informe -> navegador/Excel/PDF.

## Amenazas
- SSRF a loopback, RFC1918, link-local, metadata endpoints, IPv6, direcciones DNS mixtas, DNS rebinding y formatos numéricos ambiguos.
- Redirecciones externas, cambios HTTPS -> HTTP, bucles, puertos no autorizados.
- Respuestas enormes, compresión maliciosa, enlaces infinitos y denegación de servicio accidental.
- HTML/URL malicioso en informes, CSV formula injection y documentos hostiles.
- Exfiltración por plugins, registros con tokens, capturas con datos personales.
- Robots.txt inaccesible, autenticación involuntaria y políticas de alcance ambiguas.

## Controles
Solo el transporte del núcleo hace peticiones. Validar cada destino y salto; conectar a IP validada conservando hostname para TLS. Aplicar presupuestos de tiempo, tamaño, profundidad, peticiones y concurrencia; detenerse ante denegaciones según política. Nunca rastrear sistemas autenticados ni subdominios sin autorización. Rechazar plugins no confiables en proceso; un subproceso sin sandbox no garantiza aislamiento.

## Baseline observado y pendientes
Existen validación DNS pública, conexión IP fijada, robots y límite de bytes de cuerpo HTML. Pendiente demostrar límites de tamaño descomprimido, deadline global, registro completo de redirecciones, políticas configurables y pruebas E2E de rebinding. La redirección inicial apex/www se resuelve antes de cargar robots.txt: requiere revisión explícita del presupuesto de peticiones y de la política de robots en M1.

## Privacidad
No conservar cuerpos íntegros, cookies, cabeceras Authorization ni datos de formularios por defecto. Retención configurable y eliminación verificable. No enviar contenido a servicios de IA externos automáticamente.

## Operación institucional
Autorización escrita del alcance, horario de ejecución, rate limiting conservador, registro de operador, versión de reglas y respuesta ante incidentes. ENS/RGPD requieren evaluación específica del despliegue: la herramienta no certifica cumplimiento.
