# Informe de ejecución Tasks 10–15

Fecha local: 20/09/2026. Rama `develop`. Sin commit ni push. Se conservaron los cambios
previos y la base existente. Fuente funcional: consignas versionadas derivadas del manual;
las capturas del PDF no se usaron como datos reales ni como credenciales.

## Resultado

Tasks 10–14 implementadas y verificadas en el entorno de prueba. Task 15 completó
aceptación local, guías y soporte configurable. **La aceptación institucional integral
sigue pendiente** de plantilla/reglas oficiales, requisitos no confirmados y API RENAPER.
El usuario autorizó plantillas/personas de prueba y preparativos sin API; confirmó que
la composición impide envío si falla, pero afiliación observada/RENAPER pendiente permiten
enviar una lista completa a revisión. Tras el envío se bloquea edición de contenido.

- Composición exacta por versión, grupos/posiciones/contexto/DNI, paridad global y alternancia
  configurable. Evaluación persistida; envío transaccional e idempotente. Aprobación
  sistémica preparada con evidencia obligatoria, sin aprobaciones por mocks en la base local.
- Bandeja ADMIN paginada y detalle agregado con personas, controles y vínculos contextuales.
- Dashboards por rol/elección, métricas SQL compartidas con reportes, denominador explícito.
- Exportaciones reales: listas XLSX/CSV, reportes XLSX/PDF, padrón XLSX/CSV; filtros completos,
  límites explícitos, protección de fórmulas, MIME y manejo central de sesión/errores.
- Auditoría ADMIN paginada, filtros, historia de lista/candidato, eventos de envío/aprobación
  diferenciados. Alta heredada de candidatos también quedó atómica y auditada.
- Ayuda por rol y recuperación asistida con contacto configurable; sin correo simulado.

## Archivos y arquitectura

Se reutilizaron ElectoralList, ListValidation, CandidateValidation, AuditLog, reglas
versionadas y control de asignaciones. **No hay migración adicional de Tasks 10–15**;
la cadena de 04–09 sigue siendo necesaria para una instalación limpia.

Nuevos servicios: `composition_service`, `submission_service`, `inspection_service`,
`reporting_service`, `export_service`; repositorio `reporting_repository`, schemas de filtros
`reporting`, router `/admin`. Se extendieron `electoral_workflow_service`, `audit_service`,
`candidate_service`, consultas de padrón y el cliente frontend compartido.
Frontend: Dashboard/Validaciones/Reportes/CandidatosRevision reales, Auditoria/Ayuda,
componentes Reporting/Composition, detalle y descargas del padrón. Dependency nueva:
ReportLab >=4,<5, reutilizando openpyxl para XLSX. Los endpoints delegan a servicios y repositorios.

Contratos, transiciones, columnas, filtros, permisos y límites completos en
[SUBMISSION_REPORTING_AUDIT.md](../SUBMISSION_REPORTING_AUDIT.md).
Archivos exactos y cambios acumulados del workspace en [estado Git](evidencia-10-15/git-state.txt).
El diff acumulado también contiene Tasks 03–09; no se atribuye todo a este bloque.

## Verificaciones ejecutadas

| Verificación | Resultado |
| --- | --- |
| Backend, `python -m pytest -q` | **110 passed**; 37 pruebas nuevas en test_tasks_10_15.py |
| Frontend, `npm run test` | **14 passed**; blobs/MIME/401/errores incluidos |
| Frontend build y lint | PASS |
| Alembic current / heads | `e271bb89a403` / mismo head |
| Alembic check | No new upgrade operations detected |
| PostgreSQL limpio | Upgrade → downgrade a 8c4f2e91b6a7 → upgrade: PASS |
| Dos importaciones concurrentes PostgreSQL | PASS; un solo lote vigente |
| Dos envíos concurrentes PostgreSQL | PASS; una evaluación de envío y un evento, un segundo resultado idempotente |
| Backup/restauración | PASS, en copia temporal; coinciden usuarios/listas/personas/candidatos/padrón/auditoría |
| Exportaciones API contra PostgreSQL real | Los seis formatos/rutas responden archivos válidos y coinciden con filtros |
| PDF multipágina | 60 registros, 7 páginas renderizadas e inspeccionadas; todos los registros/encabezados/pies presentes |
| Volumen de exportación | 10.000 filas × 18 campos: CSV ~0,04 s; XLSX ~0,77 s, 10.001 filas contando encabezado |
| Navegador real | Login/logout ambos roles, envío ambos cargos, lectura posterior, bandeja/reportes/auditoría/ayuda, descargas |
| Responsive | 1440 px y 390 px; ancho de documento 390 en móvil, sin overflow global |
| Consola | Sin errores en recorridos verificados; sin overlay Vite |
| Git diff --check / --cached --check | PASS |

Versiones: Python 3.12.13, Node 24.19.0, PostgreSQL 17, Vite 8.0.3, ReportLab 4.5.1.
Advertencias existentes: `crypt`/`datetime.utcnow` deprecados y catálogo Browserslist
antiguo; no impidieron pruebas/build. No se actualizaron dependencias ajenas al alcance.
Las mediciones de exportación son locales, no una promesa de concurrencia/capacidad productiva.

Las pruebas cubren 24=16+8 y 22 posiciones; 23/25 y 21/23; grupos/orden incorrectos,
paridad/alternancia/duplicados/contexto; faltantes y corrección; permisos/revocación/plazo;
observación y pendiente; revisión actual vs legacy; rollback de auditoría; métricas vacías
y por estado; exportación superior a una página, filtros y límites; tildes/ceros/fórmulas;
auditoría por actor/recurso y fechas Argentina. La aprobación positiva usa un doble de
proveedor **solo en tests aislados**. No se verificó RENAPER real ni normativa institucional.

## Recorrido local conservado

Se crearon por API dos listas ficticias `QA1015-22` y `QA1015-24`, con 22 y 24 posiciones,
respectivamente. Ambas se enviaron desde navegador como APODERADO y quedaron en lectura.
Reporte filtrado por `QA1015`: 2 listas, 46 candidatos, 2 enviadas, 0 aprobadas. Las ausencias
en padrón y RENAPER pendiente permanecen visibles. El script temporal de carga fue ejecutado
y eliminado; no se versionó. La DB local conserva los ejemplos para revisión del usuario.

La restauración de prueba comparó 2 usuarios, 8 listas, 68 personas, 68 candidaturas,
24 afiliados y 105 eventos en el snapshot usado. La prueba concurrente corrió únicamente
sobre esa copia, luego eliminada. No se borraron/reemplazaron datos de la base de trabajo.
Los archivos descargados se abrieron programáticamente con openpyxl/CSV y PDF se renderizó;
las descargas Excel/PDF/CSV también se accionaron desde sus botones del navegador.

## Evidencia y operación

- [Bandeja ADMIN](evidencia-10-15/bandeja-admin.png), [reporte ADMIN](evidencia-10-15/reportes-admin.png).
- [Auditoría contextual](evidencia-10-15/auditoria-admin.png), [reporte móvil](evidencia-10-15/reportes-mobile.png).
- [Lista enviada](evidencia-10-15/apoderado-envio.png), [dashboard apoderado móvil](evidencia-10-15/dashboard-apoderado-mobile.png).
- PDF de control: [primera página](evidencia-10-15/pdf-pagina-1.png), [última página](evidencia-10-15/pdf-pagina-7.png).
- [Manual ADMIN](../MANUAL_ADMIN.md), [manual APODERADO](../MANUAL_APODERADO.md), [operación/recuperación](../OPERACION_LOCAL.md).

API en <http://localhost:8000>, frontend en <http://localhost:5173>, PostgreSQL Docker saludable.
Las tareas y documentación están incorporadas al seguimiento de Git; secretos y seeds siguen fuera.

## Pendientes externos explícitos

- Plantilla oficial y criterios D01–D06; las decisiones de prueba no son aprobación normativa.
- Proveedor/documentación/acceso RENAPER, adapter HTTP y aceptación autorizada. Preparación
  actual conserva pendientes/errores y no afirma identidad verificada.
- Valor institucional de SUPPORT_CONTACT; el canal no se inventa. La recuperación asistida funciona.
- Reapertura/dispensas/decisiones manuales no fueron acordadas ni implementadas.
- Aceptación institucional de todas las capacidades; CAP-15 y la parte externa de CAP-26 siguen abiertas.
